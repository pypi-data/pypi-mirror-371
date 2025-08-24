"""
Cocotb testbench for Simple ALU differential testing.

This testbench demonstrates the complete differential testing framework
by comparing the Simple ALU hardware implementation with its golden model.
"""

import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock
import sys
import os
from pathlib import Path
import torch

# Add framework to Python path
framework_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(framework_root))

# Framework imports
from testbench.base import DiffTestBase, TestSequence, TestVector
from golden_model.models import SimpleALUGoldenModel
from golden_model.models.simple_alu_model import ALUTestVectorGenerator
from testbench.base.dut_interface import DUTInterface, create_standard_interface_config
from golden_model.base.utils import TensorComparator, ComparisonMode, ComparisonResult
from scripts.logger import get_logger, log_test_start, log_test_complete

# Test configuration
TEST_CONFIG = {
    'clock_period': 10,
    'clock_units': 'ns',
    'reset_cycles': 5,
    'data_width': 32,
    'timeout_cycles': 100
}


class SimpleALUDiffTest(DiffTestBase):
    """
    Differential test for Simple ALU.
    
    This class implements the complete differential testing flow
    for comparing the ALU hardware with its golden model.
    """
    
    def __init__(self, dut):
        # Create golden model
        golden_model = SimpleALUGoldenModel(
            data_width=TEST_CONFIG['data_width']
        )
        
        super().__init__(dut, golden_model, "SimpleALUDiffTest")
        
        # Configure for ALU testing
        self.config.update(TEST_CONFIG)
        
        # Create DUT interface
        interface_config = create_standard_interface_config(
            clock_name="clk",
            reset_name="rst_n", 
            input_signals=["a_i", "b_i", "op_i", "valid_i"],
            output_signals=["result_o", "valid_o", "ready_o", "overflow_o", "zero_o",
                          "debug_stage1_o", "debug_stage2_o", "debug_flags_o"]
        )
        
        self.dut_interface = DUTInterface(dut, interface_config)
        
        # Test vector generator
        self.vector_generator = ALUTestVectorGenerator(TEST_CONFIG['data_width'])
        
        # Setup comparator with appropriate tolerance
        self.comparator = TensorComparator(
            default_mode=ComparisonMode.BIT_ACCURATE,
            default_tolerance=0
        )
        
    async def setup_dut(self):
        """Custom DUT setup for ALU."""
        self.logger.info("Setting up Simple ALU DUT")
        
        # Initialize all inputs to safe values
        initial_values = {
            'a_i': 0,
            'b_i': 0, 
            'op_i': 0xF,  # NOP operation
            'valid_i': 0
        }
        
        self.dut_interface.apply_test_vector(initial_values)
        
        # Wait for reset to complete
        await ClockCycles(self.dut.clk, 2)
        
    async def apply_custom_stimulus(self, test_vector: TestVector):
        """Apply ALU-specific stimulus."""
        # Apply test vector to DUT
        stimulus = {
            'a_i': test_vector.inputs['a'],
            'b_i': test_vector.inputs['b'],
            'op_i': test_vector.inputs['op'],
            'valid_i': 1 if test_vector.inputs.get('valid', True) else 0
        }
        
        # Wait for ready signal first
        if hasattr(self.dut, 'ready_o'):
            await self._wait_for_ready()
        
        self.dut_interface.apply_test_vector(stimulus)
        self.logger.debug(f"Applied stimulus: a={stimulus['a_i']}, b={stimulus['b_i']}, op={stimulus['op_i']}")
        self.logger.debug(f"Ready signal: {int(self.dut.ready_o.value)}")
            
    async def _wait_for_ready(self):
        """Wait for DUT ready signal."""
        timeout_cycles = self.config['timeout_cycles']
        
        for cycle in range(timeout_cycles):
            await RisingEdge(self.dut.clk)
            if int(self.dut.ready_o.value) == 1:
                return
                
        raise TimeoutError(f"DUT ready signal not asserted within {timeout_cycles} cycles")
        
    async def capture_dut_outputs(self):
        """Capture ALU outputs."""
        # Wait for valid output
        await self._wait_for_valid_output()
        
        self.logger.debug(f"After valid, ready={int(self.dut.ready_o.value)}, valid={int(self.dut.valid_o.value)}")
        
        # Capture all outputs
        outputs = {
            'result': int(self.dut.result_o.value),
            'overflow': bool(int(self.dut.overflow_o.value)),
            'zero': bool(int(self.dut.zero_o.value)), 
            'valid': bool(int(self.dut.valid_o.value)),
            'debug_stage1': int(self.dut.debug_stage1_o.value),
            'debug_stage2': int(self.dut.debug_stage2_o.value),
            'debug_flags': torch.tensor([(int(self.dut.debug_flags_o.value) >> i) & 1 for i in range(4)], dtype=torch.int64)
        }
        
        self.logger.debug(f"Captured outputs: {outputs}")
        
        # Wait extra cycles for hardware to return to ready state
        await ClockCycles(self.dut.clk, 5)
        
        # Reset valid_i to make sure we're in a clean state
        self.dut.valid_i.value = 0
        await ClockCycles(self.dut.clk, 2)
        
        return outputs
        
    async def _wait_for_valid_output(self):
        """Wait for valid output from ALU."""
        timeout_cycles = self.config['timeout_cycles']
        
        for cycle in range(timeout_cycles):
            await RisingEdge(self.dut.clk)
            if int(self.dut.valid_o.value) == 1:
                return
                
        raise TimeoutError(f"ALU valid output not asserted within {timeout_cycles} cycles")
        
    async def compare_checkpoints(self, golden_checkpoints, hardware_outputs):
        """Compare golden model checkpoints with hardware outputs."""
        comparisons = []
        
        # Compare main outputs
        golden_outputs = golden_checkpoints.get('outputs', {})
        
        main_comparisons = [
            ('result', 'result'),
            ('overflow', 'overflow'),
            ('zero', 'zero'),
            ('debug_stage1', 'debug_stage1'),
            ('debug_stage2', 'debug_stage2')
        ]
        
        for golden_key, hw_key in main_comparisons:
            if golden_key in golden_outputs and hw_key in hardware_outputs:
                golden_val = golden_outputs[golden_key]
                hw_val = hardware_outputs[hw_key]
                
                # Debug output
                self.logger.debug(f"Comparing {golden_key}: Golden={golden_val}, Hardware={hw_val}")
                
                comparison = self.comparator.compare(
                    golden_val, hw_val, name=f"main_{golden_key}"
                )
                comparisons.append(comparison)
                
        # Compare intermediate stages
        stage1_checkpoint = golden_checkpoints.get('stage1', {})
        stage2_checkpoint = golden_checkpoints.get('stage2', {})
        
        if 'result' in stage1_checkpoint:
            comparison = self.comparator.compare(
                stage1_checkpoint['result'],
                hardware_outputs.get('debug_stage1', 0),
                name="stage1_result"
            )
            comparisons.append(comparison)
            
        if 'result' in stage2_checkpoint:
            comparison = self.comparator.compare(
                stage2_checkpoint['result'],
                hardware_outputs.get('debug_stage2', 0),
                name="stage2_result"
            )
            comparisons.append(comparison)
            
        return comparisons
        
    async def cleanup_dut(self):
        """Cleanup ALU DUT."""
        self.logger.info("Cleaning up Simple ALU DUT")
        
        # Set inputs to safe values
        self.dut.valid_i.value = 0
        await ClockCycles(self.dut.clk, 2)


# Test sequences
def create_corner_case_sequence():
    """Create corner case test sequence."""
    generator = ALUTestVectorGenerator()
    corner_vectors = generator.generate_corner_cases()
    
    test_vectors = []
    for i, vector_data in enumerate(corner_vectors[:20]):  # Limit for demo
        test_vector = TestVector(
            inputs=vector_data,
            test_id=f"corner_{i}"
        )
        test_vectors.append(test_vector)
        
    return TestSequence("corner_cases", test_vectors)


def create_random_sequence(count=100):
    """Create random test sequence."""
    generator = ALUTestVectorGenerator()
    random_vectors = generator.generate_random_vectors(count)
    
    test_vectors = []
    for i, vector_data in enumerate(random_vectors):
        test_vector = TestVector(
            inputs=vector_data,
            test_id=f"random_{i}"
        )
        test_vectors.append(test_vector)
        
    return TestSequence("random_tests", test_vectors)


def create_targeted_sequence():
    """Create targeted test sequence."""
    generator = ALUTestVectorGenerator()
    targeted_vectors = generator.generate_targeted_vectors()
    
    test_vectors = []
    for i, vector_data in enumerate(targeted_vectors):
        test_vector = TestVector(
            inputs=vector_data,
            test_id=f"targeted_{i}"
        )
        test_vectors.append(test_vector)
        
    return TestSequence("targeted_tests", test_vectors)


# Main test functions
@cocotb.test()
async def test_alu_corner_cases(dut):
    """Test ALU with corner cases."""
    logger = get_logger("test_alu_corner_cases")
    log_test_start("ALU Corner Cases", TEST_CONFIG)
    
    try:
        # Create differential test instance
        diff_test = SimpleALUDiffTest(dut)
        
        # Create test sequence
        test_sequence = create_corner_case_sequence()
        
        # Run test sequences without cleanup to avoid early termination
        await diff_test._setup_phase()
        
        # Execute test sequences
        for sequence in [test_sequence]:
            await diff_test._run_sequence(sequence)
        
        # Analyze results immediately from the sequence
        results = test_sequence.results  # Get results from the sequence
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        
        # Debug: print details about failed tests
        failed_results = [r for r in results if not r.passed]
        if failed_results:
            logger.info(f"Failed test details: {[r.test_id for r in failed_results]}")
        
        test_result = {
            'passed': passed_tests == total_tests,
            'total': total_tests,
            'passed_count': passed_tests,
            'failed_count': total_tests - passed_tests
        }
        
        log_test_complete("ALU Corner Cases", test_result)
        logger.info(f"Corner case results: {passed_tests}/{total_tests} passed")
        
        # Assert overall pass BEFORE cleanup
        assert passed_tests == total_tests, f"Corner case test failed: {passed_tests}/{total_tests} passed"
        
        # Skip cleanup to avoid simulator termination issue
        # await diff_test._cleanup_phase()
        logger.info("Test completed successfully - skipping cleanup to avoid simulator shutdown")
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        log_test_complete("ALU Corner Cases", {'passed': False, 'error': str(e)})
        raise


@cocotb.test()
async def test_alu_random(dut):
    """Test ALU with random inputs."""
    logger = get_logger("test_alu_random")
    log_test_start("ALU Random Tests", TEST_CONFIG)
    
    try:
        diff_test = SimpleALUDiffTest(dut)
        test_sequence = create_random_sequence(50)  # Reduced for demo
        
        results = await diff_test.run_test([test_sequence])
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        
        test_result = {
            'passed': passed_tests == total_tests,
            'total': total_tests,
            'passed_count': passed_tests,
            'failed_count': total_tests - passed_tests
        }
        
        log_test_complete("ALU Random Tests", test_result)
        assert passed_tests == total_tests, f"Random test failed: {passed_tests}/{total_tests} passed"
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        log_test_complete("ALU Random Tests", {'passed': False, 'error': str(e)})
        raise


@cocotb.test()
async def test_alu_targeted(dut):
    """Test ALU with targeted test cases."""
    logger = get_logger("test_alu_targeted")
    log_test_start("ALU Targeted Tests", TEST_CONFIG)
    
    try:
        diff_test = SimpleALUDiffTest(dut)
        test_sequence = create_targeted_sequence()
        
        results = await diff_test.run_test([test_sequence])
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        
        test_result = {
            'passed': passed_tests == total_tests,
            'total': total_tests,
            'passed_count': passed_tests,
            'failed_count': total_tests - passed_tests
        }
        
        log_test_complete("ALU Targeted Tests", test_result)
        assert passed_tests == total_tests, f"Targeted test failed: {passed_tests}/{total_tests} passed"
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        log_test_complete("ALU Targeted Tests", {'passed': False, 'error': str(e)})
        raise


@cocotb.test()
async def test_alu_comprehensive(dut):
    """Comprehensive ALU test with all sequences."""
    logger = get_logger("test_alu_comprehensive")
    log_test_start("ALU Comprehensive Test", TEST_CONFIG)
    
    try:
        diff_test = SimpleALUDiffTest(dut)
        
        # Create all test sequences
        sequences = [
            create_corner_case_sequence(),
            create_random_sequence(25),  # Reduced for demo
            create_targeted_sequence()
        ]
        
        # Run all sequences
        results = await diff_test.run_test(sequences)
        
        # Analyze results by sequence
        sequence_results = {}
        current_idx = 0
        
        for sequence in sequences:
            seq_results = results[current_idx:current_idx + len(sequence.test_vectors)]
            seq_passed = sum(1 for r in seq_results if r.passed)
            
            sequence_results[sequence.name] = {
                'total': len(seq_results),
                'passed': seq_passed,
                'failed': len(seq_results) - seq_passed
            }
            
            current_idx += len(sequence.test_vectors)
        
        # Overall results
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        
        test_result = {
            'passed': passed_tests == total_tests,
            'total': total_tests,
            'passed_count': passed_tests,
            'failed_count': total_tests - passed_tests,
            'sequence_results': sequence_results
        }
        
        log_test_complete("ALU Comprehensive Test", test_result)
        
        # Log sequence-specific results
        for seq_name, seq_result in sequence_results.items():
            logger.info(f"Sequence {seq_name}: {seq_result['passed']}/{seq_result['total']} passed")
            
        assert passed_tests == total_tests, f"Comprehensive test failed: {passed_tests}/{total_tests} passed"
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        log_test_complete("ALU Comprehensive Test", {'passed': False, 'error': str(e)})
        raise