"""
Cocotb testbench for FPU differential testing.

This testbench demonstrates a simple differential testing framework
by comparing the FPU hardware implementation with its golden model.
The FPU performs a simple max(a, b) operation.
"""

import cocotb
from cocotb.triggers import Timer
import sys
import os
from pathlib import Path
import torch
import numpy as np

# Add framework to Python path
framework_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(framework_root))

# Framework imports
from testbench.base import DiffTestBase, TestSequence, TestVector
from golden_model.models import FPUGoldenModel, FPUTestVectorGenerator
from testbench.base.dut_interface import DUTInterface, create_standard_interface_config
from golden_model.base.utils import TensorComparator, ComparisonMode, ComparisonResult
from scripts.logger import get_logger, log_test_start, log_test_complete

# Test configuration
TEST_CONFIG = {
    'data_width': 32,
    'timeout_ns': 100,  # Combinational logic should be fast
    'setup_time_ns': 10
}


class FPUDiffTest(DiffTestBase):
    """
    Differential test for FPU.
    
    This class implements the complete differential testing flow
    for comparing the FPU hardware with its golden model.
    """
    
    def __init__(self, dut):
        # Create golden model
        golden_model = FPUGoldenModel(data_width=TEST_CONFIG['data_width'])
        
        super().__init__(dut, golden_model, "FPUDiffTest")
        
        # Configure for FPU testing
        self.config.update(TEST_CONFIG)
        
        # Create DUT interface for combinational logic (no clock needed)
        interface_config = create_standard_interface_config(
            clock_name=None,  # No clock for combinational logic
            reset_name=None,  # No reset for combinational logic
            input_signals=["a", "b"],
            output_signals=["result"]
        )
        
        self.dut_interface = DUTInterface(dut, interface_config)
        
        # Test vector generator
        self.vector_generator = FPUTestVectorGenerator(data_width=TEST_CONFIG['data_width'])
        
        # Setup comparator for exact integer matching
        self.comparator = TensorComparator(
            default_mode=ComparisonMode.EXACT,
            default_tolerance=0  # Exact match required
        )
        
    async def setup_dut(self):
        """Custom DUT setup for FPU."""
        self.logger.info("Setting up FPU DUT")
        
        # Initialize inputs to safe values
        self.dut.a.value = 0
        self.dut.b.value = 0
        
        # Wait for setup
        await Timer(TEST_CONFIG['setup_time_ns'], units='ns')
        
    async def apply_custom_stimulus(self, test_vector: TestVector):
        """Apply FPU-specific stimulus."""
        # Store test context
        self._store_test_context(test_vector)
        
        # Extract inputs
        a = test_vector.inputs.get('a', 0)
        b = test_vector.inputs.get('b', 0)
        
        # Apply stimulus to DUT
        self.dut.a.value = int(a)
        self.dut.b.value = int(b)
        
        self.logger.debug(f"Applied FPU stimulus: a={a}, b={b}")
        
        # Wait for combinational logic to settle
        await Timer(TEST_CONFIG['timeout_ns'], units='ns')
        
    async def capture_dut_outputs(self):
        """Capture FPU outputs."""
        # No clock, so just capture the current output
        result = int(self.dut.result.value)
        
        outputs = {
            'result': torch.tensor(result, dtype=torch.int64)
        }
        
        self.logger.debug(f"Captured FPU output: result={result}")
        
        return outputs
        
    async def _compare_outputs(self, test_vector, hardware_outputs):
        """Override base class comparison to handle FPU-specific logic."""
        # Run golden model
        golden_outputs = self.golden_model(test_vector.inputs)
        golden_checkpoints = self.golden_model.get_all_checkpoints()
        
        # Perform comparisons
        comparisons = await self.compare_checkpoints(golden_checkpoints, hardware_outputs)
        
        # Calculate overall result
        all_passed = all(comp.passed for comp in comparisons)
        
        # Create result
        from testbench.base.testbench_base import DiffTestResult, TestPhase
        result = DiffTestResult(
            test_name=test_vector.test_id,
            passed=all_passed,
            phase=TestPhase.COMPARISON,
            comparisons=comparisons,
            execution_time=0.0  # No execution time for combinational logic
        )
        
        return result

    async def compare_checkpoints(self, golden_checkpoints, hardware_outputs):
        """Compare golden model checkpoints with hardware outputs."""
        comparisons = []
        
        # Compare main result
        golden_outputs = golden_checkpoints.get('final_outputs', {})
        
        if 'result' in golden_outputs and 'result' in hardware_outputs:
            golden_result = golden_outputs['result']
            hw_result = hardware_outputs['result']
            
            self.logger.debug(f"Comparing results: Golden={golden_result}, HW={hw_result}")
            
            comparison = self.comparator.compare(
                golden_result, hw_result,
                name="result",
                mode=ComparisonMode.EXACT
            )
            comparisons.append(comparison)
            
        return comparisons
        
    async def cleanup_dut(self):
        """Cleanup FPU DUT."""
        self.logger.info("Cleaning up FPU DUT")
        
        # Set inputs to safe values
        self.dut.a.value = 0
        self.dut.b.value = 0
        await Timer(TEST_CONFIG['setup_time_ns'], units='ns')

    def _store_test_context(self, test_vector):
        """Store test context for output capture."""
        self._current_test_type = test_vector.inputs.get('test_type', 'unknown')
        self._current_test_id = test_vector.test_id


# Test sequence generators
def create_simple_test_sequence():
    """Create a simple test sequence."""
    generator = FPUTestVectorGenerator()
    simple_vector = generator.generate_simple_test_pair()
    
    test_vector = TestVector(
        inputs=simple_vector,
        test_id=simple_vector['test_id']
    )
    
    return TestSequence("simple_test", [test_vector])


def create_corner_case_sequence():
    """Create corner case test sequence."""
    generator = FPUTestVectorGenerator()
    corner_vectors = generator.generate_corner_case_vectors()
    
    test_vectors = []
    for vector_data in corner_vectors:
        test_vector = TestVector(
            inputs=vector_data,
            test_id=vector_data['test_id']
        )
        test_vectors.append(test_vector)
        
    return TestSequence("corner_cases", test_vectors)


def create_random_test_sequence(count=20):
    """Create random test sequence."""
    generator = FPUTestVectorGenerator()
    random_vectors = generator.generate_random_vectors(count, seed=123)
    
    test_vectors = []
    for vector_data in random_vectors:
        test_vector = TestVector(
            inputs=vector_data,
            test_id=vector_data['test_id']
        )
        test_vectors.append(test_vector)
        
    return TestSequence("random_tests", test_vectors)


# Main test functions
@cocotb.test()
async def test_fpu_simple(dut):
    """Test FPU with a simple case."""
    logger = get_logger("test_fpu_simple")
    log_test_start("FPU Simple Test", TEST_CONFIG)
    
    try:
        # Create differential test instance
        diff_test = FPUDiffTest(dut)
        
        # Create test sequence
        test_sequence = create_simple_test_sequence()
        
        # Setup and run
        await diff_test._setup_phase()
        await diff_test._run_sequence(test_sequence)
        
        # Analyze results
        results = test_sequence.results
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        
        test_result = {
            'passed': passed_tests == total_tests,
            'total': total_tests,
            'passed_count': passed_tests,
            'failed_count': total_tests - passed_tests
        }
        
        log_test_complete("FPU Simple Test", test_result)
        logger.info(f"Simple test results: {passed_tests}/{total_tests} passed")
        
        assert passed_tests == total_tests, f"Simple test failed: {passed_tests}/{total_tests} passed"
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        log_test_complete("FPU Simple Test", {'passed': False, 'error': str(e)})
        raise


@cocotb.test()
async def test_fpu_corner_cases(dut):
    """Test FPU with corner cases."""
    logger = get_logger("test_fpu_corner_cases")
    log_test_start("FPU Corner Cases", TEST_CONFIG)
    
    try:
        diff_test = FPUDiffTest(dut)
        await diff_test._setup_phase()
        
        # Run corner case tests
        corner_sequence = create_corner_case_sequence()
        await diff_test._run_sequence(corner_sequence)
        
        # Analyze results
        results = corner_sequence.results
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        
        test_result = {
            'passed': passed_tests == total_tests,
            'total': total_tests,
            'passed_count': passed_tests,
            'failed_count': total_tests - passed_tests
        }
        
        log_test_complete("FPU Corner Cases", test_result)
        assert passed_tests == total_tests, f"Corner case test failed: {passed_tests}/{total_tests} passed"
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        log_test_complete("FPU Corner Cases", {'passed': False, 'error': str(e)})
        raise


@cocotb.test()
async def test_fpu_random(dut):
    """Test FPU with random inputs."""
    logger = get_logger("test_fpu_random")
    log_test_start("FPU Random Tests", TEST_CONFIG)
    
    try:
        diff_test = FPUDiffTest(dut)
        await diff_test._setup_phase()
        
        # Run random tests
        random_sequence = create_random_test_sequence(count=10)  # Reduced for demo
        await diff_test._run_sequence(random_sequence)
        
        # Analyze results
        results = random_sequence.results
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        
        test_result = {
            'passed': passed_tests == total_tests,
            'total': total_tests,
            'passed_count': passed_tests,
            'failed_count': total_tests - passed_tests
        }
        
        log_test_complete("FPU Random Tests", test_result)
        assert passed_tests == total_tests, f"Random test failed: {passed_tests}/{total_tests} passed"
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        log_test_complete("FPU Random Tests", {'passed': False, 'error': str(e)})
        raise


@cocotb.test()
async def test_fpu_comprehensive(dut):
    """Comprehensive FPU test with all sequences."""
    logger = get_logger("test_fpu_comprehensive")
    log_test_start("FPU Comprehensive Test", TEST_CONFIG)
    
    try:
        diff_test = FPUDiffTest(dut)
        await diff_test._setup_phase()
        
        # Create and run all test sequences
        sequences = [
            create_simple_test_sequence(),
            create_corner_case_sequence(),
            create_random_test_sequence(count=5)  # Reduced for demo
        ]
        
        all_results = []
        sequence_results = {}
        
        for sequence in sequences:
            await diff_test._run_sequence(sequence)
            
            results = sequence.results
            all_results.extend(results)
            
            seq_passed = sum(1 for r in results if r.passed)
            sequence_results[sequence.name] = {
                'total': len(results),
                'passed': seq_passed,
                'failed': len(results) - seq_passed
            }
        
        # Overall results
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.passed)
        
        test_result = {
            'passed': passed_tests == total_tests,
            'total': total_tests,
            'passed_count': passed_tests,
            'failed_count': total_tests - passed_tests,
            'sequence_results': sequence_results
        }
        
        log_test_complete("FPU Comprehensive Test", test_result)
        
        # Log sequence-specific results
        for seq_name, seq_result in sequence_results.items():
            logger.info(f"Sequence {seq_name}: {seq_result['passed']}/{seq_result['total']} passed")
            
        assert passed_tests == total_tests, f"Comprehensive test failed: {passed_tests}/{total_tests} passed"
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        log_test_complete("FPU Comprehensive Test", {'passed': False, 'error': str(e)})
        raise