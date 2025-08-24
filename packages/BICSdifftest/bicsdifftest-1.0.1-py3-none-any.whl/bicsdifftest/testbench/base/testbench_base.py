"""
Base classes for cocotb differential testing framework.

This module provides the foundation for implementing cocotb testbenches
that perform differential testing between hardware designs and PyTorch golden models.
"""

import cocotb
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.result import TestFailure, TestSuccess

import torch
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union, Callable, Awaitable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# Import golden model components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from golden_model.base import GoldenModelBase, TensorComparator, ComparisonResult


class TestPhase(Enum):
    """Test execution phases."""
    SETUP = "setup"
    STIMULUS = "stimulus" 
    RESPONSE = "response"
    COMPARISON = "comparison"
    CLEANUP = "cleanup"


@dataclass
class TestVector:
    """Test vector container."""
    inputs: Dict[str, Any]
    expected_outputs: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    test_id: Optional[str] = None


@dataclass 
class DiffTestResult:
    """Result of differential test execution."""
    test_name: str
    passed: bool
    phase: TestPhase
    comparisons: List[ComparisonResult]
    execution_time: float
    error_message: Optional[str] = None
    debug_data: Optional[Dict[str, Any]] = None


class ClockGenerator:
    """Clock generation utility for testbenches."""
    
    def __init__(self, dut, clock_name: str = "clk", period: int = 10, units: str = "ns"):
        """
        Initialize clock generator.
        
        Args:
            dut: Device under test
            clock_name: Name of clock signal
            period: Clock period
            units: Time units
        """
        self.dut = dut
        self.clock_name = clock_name
        self.period = period
        self.units = units
        self.clock_signal = getattr(dut, clock_name)
        self.clock_task = None
        
    async def start_clock(self):
        """Start the clock."""
        clock = Clock(self.clock_signal, self.period, units=self.units)
        self.clock_task = cocotb.start_soon(clock.start())
        
    def stop_clock(self):
        """Stop the clock."""
        if self.clock_task:
            self.clock_task.kill()


class SignalMonitor:
    """Monitor for DUT signals with value tracking."""
    
    def __init__(self, dut, signal_name: str, edge_type: str = "rising"):
        """
        Initialize signal monitor.
        
        Args:
            dut: Device under test
            signal_name: Name of signal to monitor
            edge_type: Edge type to monitor ("rising", "falling", "both")
        """
        self.dut = dut
        self.signal_name = signal_name
        self.signal = getattr(dut, signal_name)
        self.edge_type = edge_type
        self.values = []
        self.timestamps = []
        self.monitoring = False
        self.monitor_task = None
        
    async def start_monitoring(self):
        """Start monitoring the signal."""
        self.monitoring = True
        self.monitor_task = cocotb.start_soon(self._monitor_loop())
        
    def stop_monitoring(self):
        """Stop monitoring the signal."""
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.kill()
            
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            if self.edge_type == "rising":
                await RisingEdge(self.signal)
            elif self.edge_type == "falling":
                await FallingEdge(self.signal)
            else:  # both
                await RisingEdge(self.signal)
                
            self.values.append(int(self.signal.value))
            self.timestamps.append(cocotb.utils.get_sim_time())
            
    def get_values(self) -> List[int]:
        """Get captured values."""
        return self.values.copy()
        
    def clear_values(self):
        """Clear captured values."""
        self.values.clear()
        self.timestamps.clear()


class TestSequence:
    """Base class for test sequences."""
    
    def __init__(self, name: str, test_vectors: List[TestVector]):
        """
        Initialize test sequence.
        
        Args:
            name: Sequence name
            test_vectors: List of test vectors
        """
        self.name = name
        self.test_vectors = test_vectors
        self.current_vector_index = 0
        self.results = []
        
    def has_next(self) -> bool:
        """Check if more test vectors available."""
        return self.current_vector_index < len(self.test_vectors)
        
    def get_next(self) -> Optional[TestVector]:
        """Get next test vector."""
        if self.has_next():
            vector = self.test_vectors[self.current_vector_index]
            self.current_vector_index += 1
            return vector
        return None
        
    def reset(self):
        """Reset sequence to beginning."""
        self.current_vector_index = 0
        self.results.clear()


class DiffTestBase(ABC):
    """
    Base class for differential testing with cocotb and PyTorch golden models.
    
    This class provides the infrastructure for comparing hardware designs
    against software reference implementations at multiple checkpoints.
    """
    
    def __init__(self, dut, golden_model: GoldenModelBase, test_name: str = "DiffTest"):
        """
        Initialize differential test base.
        
        Args:
            dut: Device under test (cocotb DUT object)
            golden_model: PyTorch golden model for reference
            test_name: Name of the test
        """
        self.dut = dut
        self.golden_model = golden_model
        self.test_name = test_name
        
        # Test infrastructure
        self.logger = logging.getLogger(f"cocotb.{test_name}")
        self.clock_gen = ClockGenerator(dut)
        self.comparator = TensorComparator()
        
        # Test state
        self.test_results = []
        self.current_phase = TestPhase.SETUP
        self.start_time = 0
        
        # Signal monitors
        self.monitors = {}
        
        # Configuration
        self.config = {
            'clock_period': 10,
            'clock_units': 'ns',
            'reset_cycles': 5,
            'comparison_tolerance': 1e-6,
            'enable_waves': True,
            'debug_mode': False
        }
        
    async def run_test(self, test_sequences: List[TestSequence]) -> List[DiffTestResult]:
        """
        Run complete differential test with given sequences.
        
        Args:
            test_sequences: List of test sequences to execute
            
        Returns:
            List of test results
        """
        self.start_time = time.time()
        self.logger.info(f"Starting differential test: {self.test_name}")
        
        try:
            # Setup phase
            await self._setup_phase()
            
            # Execute test sequences
            for sequence in test_sequences:
                await self._run_sequence(sequence)
                
            # Cleanup phase
            await self._cleanup_phase()
            
        except Exception as e:
            self.logger.error(f"Test failed with exception: {str(e)}")
            result = DiffTestResult(
                test_name=self.test_name,
                passed=False,
                phase=self.current_phase,
                comparisons=[],
                execution_time=time.time() - self.start_time,
                error_message=str(e)
            )
            self.test_results.append(result)
            
        return self.test_results
        
    async def _setup_phase(self):
        """Setup phase - initialize DUT and golden model."""
        self.current_phase = TestPhase.SETUP
        self.logger.info("Setup phase started")
        
        # Start clock
        await self.clock_gen.start_clock()
        
        # Reset DUT
        await self._reset_dut()
        
        # Initialize golden model
        self.golden_model.reset_checkpoints()
        
        # Setup signal monitors
        await self._setup_monitors()
        
        # Custom setup
        await self.setup_dut()
        
        self.logger.info("Setup phase completed")
        
    async def _run_sequence(self, sequence: TestSequence):
        """Run a test sequence."""
        self.logger.info(f"Running sequence: {sequence.name}")
        
        sequence.reset()
        
        while sequence.has_next():
            test_vector = sequence.get_next()
            
            try:
                # Apply stimulus
                self.current_phase = TestPhase.STIMULUS
                await self._apply_stimulus(test_vector)
                
                # Capture response
                self.current_phase = TestPhase.RESPONSE
                hardware_outputs = await self._capture_response()
                
                # Compare with golden model
                self.current_phase = TestPhase.COMPARISON
                result = await self._compare_outputs(test_vector, hardware_outputs)
                
                self.test_results.append(result)
                sequence.results.append(result)
                
                if not result.passed:
                    self.logger.error(f"Test vector failed: {test_vector.test_id}")
                    if not self.config.get('continue_on_error', False):
                        raise TestFailure(f"Test failed at vector {test_vector.test_id}")
                        
            except Exception as e:
                error_result = DiffTestResult(
                    test_name=f"{sequence.name}_{test_vector.test_id}",
                    passed=False,
                    phase=self.current_phase,
                    comparisons=[],
                    execution_time=time.time() - self.start_time,
                    error_message=str(e)
                )
                self.test_results.append(error_result)
                
                if not self.config.get('continue_on_error', False):
                    raise
                    
    async def _apply_stimulus(self, test_vector: TestVector):
        """Apply test stimulus to DUT."""
        # Apply inputs to DUT
        for signal_name, value in test_vector.inputs.items():
            if hasattr(self.dut, signal_name):
                signal = getattr(self.dut, signal_name)
                signal.value = value
                self.logger.debug(f"Applied {signal_name} = {value}")
                
        # Wait for clock edge
        await RisingEdge(self.dut.clk)
        
        # Custom stimulus application
        await self.apply_custom_stimulus(test_vector)
        
    async def _capture_response(self) -> Dict[str, Any]:
        """Capture DUT response."""
        # Wait for processing
        await self._wait_for_valid_output()
        
        # Capture output signals
        outputs = await self.capture_dut_outputs()
        
        return outputs
        
    async def _compare_outputs(self, test_vector: TestVector, 
                             hardware_outputs: Dict[str, Any]) -> DiffTestResult:
        """Compare hardware outputs with golden model."""
        # Run golden model
        golden_outputs = self.golden_model(test_vector.inputs)
        golden_checkpoints = self.golden_model.get_all_checkpoints()
        
        # Perform comparisons
        comparisons = []
        
        # Compare main outputs
        for output_name, golden_value in golden_outputs.items() if isinstance(golden_outputs, dict) else [("output", golden_outputs)]:
            if output_name in hardware_outputs:
                hardware_value = hardware_outputs[output_name]
                
                comparison = self.comparator.compare(
                    golden_value,
                    hardware_value,
                    tolerance=self.config['comparison_tolerance'],
                    name=f"{test_vector.test_id}_{output_name}"
                )
                comparisons.append(comparison)
                
        # Compare checkpoint outputs
        checkpoint_comparisons = await self.compare_checkpoints(
            golden_checkpoints, hardware_outputs
        )
        comparisons.extend(checkpoint_comparisons)
        
        # Determine overall pass/fail
        all_passed = all(comp.passed for comp in comparisons)
        
        return DiffTestResult(
            test_name=f"{test_vector.test_id}",
            passed=all_passed,
            phase=TestPhase.COMPARISON,
            comparisons=comparisons,
            execution_time=time.time() - self.start_time,
            debug_data={
                'golden_checkpoints': {k: v.tolist() if isinstance(v, torch.Tensor) else v 
                                     for k, v in golden_checkpoints.items()},
                'hardware_outputs': hardware_outputs
            }
        )
        
    async def _cleanup_phase(self):
        """Cleanup phase."""
        self.current_phase = TestPhase.CLEANUP
        self.logger.info("Cleanup phase started")
        
        # Stop monitors
        for monitor in self.monitors.values():
            monitor.stop_monitoring()
            
        # Stop clock
        self.clock_gen.stop_clock()
        
        # Custom cleanup
        await self.cleanup_dut()
        
        # Generate reports
        await self._generate_reports()
        
        self.logger.info("Cleanup phase completed")
        
    async def _reset_dut(self):
        """Reset the DUT."""
        if hasattr(self.dut, 'rst_n'):
            self.dut.rst_n.value = 0
            await ClockCycles(self.dut.clk, self.config['reset_cycles'])
            self.dut.rst_n.value = 1
            await ClockCycles(self.dut.clk, 2)
        elif hasattr(self.dut, 'reset'):
            self.dut.reset.value = 1
            await ClockCycles(self.dut.clk, self.config['reset_cycles'])
            self.dut.reset.value = 0
            await ClockCycles(self.dut.clk, 2)
            
    async def _setup_monitors(self):
        """Setup signal monitors."""
        # Override in subclass to add specific monitors
        pass
        
    async def _wait_for_valid_output(self):
        """Wait for valid output from DUT."""
        # Default: wait one clock cycle
        await ClockCycles(self.dut.clk, 1)
        
    async def _generate_reports(self):
        """Generate test reports."""
        if not self.test_results:
            return
            
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        
        self.logger.info(f"Test Summary: {passed_tests}/{total_tests} passed")
        
        # Generate detailed report if configured
        if self.config.get('generate_report', True):
            report_path = Path(f"reports/{self.test_name}_report.json")
            report_path.parent.mkdir(exist_ok=True)
            
            report_data = {
                'test_name': self.test_name,
                'execution_time': time.time() - self.start_time,
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': total_tests - passed_tests,
                    'pass_rate': passed_tests / total_tests * 100
                },
                'results': [
                    {
                        'name': result.test_name,
                        'passed': result.passed,
                        'phase': result.phase.value,
                        'execution_time': result.execution_time,
                        'comparison_count': len(result.comparisons),
                        'error_message': result.error_message
                    }
                    for result in self.test_results
                ]
            }
            
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)
                
            self.logger.info(f"Detailed report saved to {report_path}")
    
    # Abstract methods to be implemented by subclasses
    
    @abstractmethod
    async def setup_dut(self):
        """Custom DUT setup. Override in subclass."""
        pass
        
    @abstractmethod
    async def apply_custom_stimulus(self, test_vector: TestVector):
        """Apply custom stimulus. Override in subclass."""
        pass
        
    @abstractmethod 
    async def capture_dut_outputs(self) -> Dict[str, Any]:
        """Capture DUT outputs. Override in subclass."""
        pass
        
    @abstractmethod
    async def compare_checkpoints(self, golden_checkpoints: Dict[str, Any],
                                hardware_outputs: Dict[str, Any]) -> List[ComparisonResult]:
        """Compare golden model checkpoints with hardware. Override in subclass."""
        pass
        
    @abstractmethod
    async def cleanup_dut(self):
        """Custom DUT cleanup. Override in subclass."""
        pass


# Utility functions for common test patterns

async def wait_for_signal(signal, value: int, timeout_cycles: int = 1000):
    """Wait for signal to reach specific value."""
    for _ in range(timeout_cycles):
        if int(signal.value) == value:
            return
        await RisingEdge(signal._handle.get_root())
    raise TimeoutError(f"Signal {signal._name} did not reach {value} within {timeout_cycles} cycles")


async def pulse_signal(signal, active_cycles: int = 1, inactive_cycles: int = 1):
    """Generate a pulse on a signal."""
    signal.value = 1
    await ClockCycles(signal._handle.get_root().clk, active_cycles)
    signal.value = 0
    await ClockCycles(signal._handle.get_root().clk, inactive_cycles)