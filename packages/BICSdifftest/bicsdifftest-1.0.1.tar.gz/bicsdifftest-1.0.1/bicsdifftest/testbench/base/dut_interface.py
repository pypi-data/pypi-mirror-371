"""
DUT interface utilities for structured signal access and control.

This module provides classes for organizing and managing DUT signals
in a structured way for differential testing.
"""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging


class SignalDirection(Enum):
    """Signal direction types."""
    INPUT = "input"
    OUTPUT = "output" 
    INOUT = "inout"


class SignalType(Enum):
    """Signal data types."""
    LOGIC = "logic"
    CLOCK = "clock"
    RESET = "reset"
    DATA = "data"
    CONTROL = "control"
    STATUS = "status"


@dataclass
class SignalInfo:
    """Information about a DUT signal."""
    name: str
    direction: SignalDirection
    signal_type: SignalType
    width: int = 1
    description: str = ""
    active_low: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class SignalBundle:
    """
    A bundle of related signals with structured access.
    
    This class groups related signals together and provides
    convenient methods for accessing and controlling them.
    """
    
    def __init__(self, name: str, dut, signal_specs: List[SignalInfo]):
        """
        Initialize signal bundle.
        
        Args:
            name: Bundle name
            dut: Device under test
            signal_specs: List of signal specifications
        """
        self.name = name
        self.dut = dut
        self.signal_specs = {spec.name: spec for spec in signal_specs}
        self.signals = {}
        self.logger = logging.getLogger(f"cocotb.{name}")
        
        # Map signals from DUT
        self._map_signals()
        
    def _map_signals(self):
        """Map signals from DUT to bundle."""
        for signal_name, spec in self.signal_specs.items():
            if hasattr(self.dut, signal_name):
                self.signals[signal_name] = getattr(self.dut, signal_name)
                self.logger.debug(f"Mapped signal: {signal_name}")
            else:
                self.logger.warning(f"Signal {signal_name} not found in DUT")
                
    def get_signal(self, name: str):
        """Get signal by name."""
        return self.signals.get(name)
        
    def set_signal(self, name: str, value: Union[int, str]):
        """Set signal value."""
        if name in self.signals:
            self.signals[name].value = value
            self.logger.debug(f"Set {name} = {value}")
        else:
            raise ValueError(f"Signal {name} not found in bundle")
            
    def get_signal_value(self, name: str) -> int:
        """Get current signal value."""
        if name in self.signals:
            return int(self.signals[name].value)
        else:
            raise ValueError(f"Signal {name} not found in bundle")
            
    def get_all_values(self) -> Dict[str, int]:
        """Get all signal values as dictionary."""
        return {name: int(signal.value) for name, signal in self.signals.items()}
        
    def set_multiple(self, values: Dict[str, Union[int, str]]):
        """Set multiple signal values."""
        for name, value in values.items():
            self.set_signal(name, value)
            
    def get_inputs(self) -> Dict[str, int]:
        """Get all input signal values."""
        return {
            name: int(signal.value)
            for name, signal in self.signals.items()
            if self.signal_specs[name].direction == SignalDirection.INPUT
        }
        
    def get_outputs(self) -> Dict[str, int]:
        """Get all output signal values."""
        return {
            name: int(signal.value)
            for name, signal in self.signals.items()
            if self.signal_specs[name].direction == SignalDirection.OUTPUT
        }
        
    def reset_inputs(self, default_values: Optional[Dict[str, int]] = None):
        """Reset all input signals to default values."""
        defaults = default_values or {}
        
        for name, spec in self.signal_specs.items():
            if spec.direction == SignalDirection.INPUT:
                if name in defaults:
                    self.set_signal(name, defaults[name])
                else:
                    # Use reasonable defaults based on signal type
                    if spec.signal_type == SignalType.RESET:
                        self.set_signal(name, 1 if spec.active_low else 0)
                    else:
                        self.set_signal(name, 0)


class DUTInterface:
    """
    High-level interface to Device Under Test.
    
    This class provides a structured way to interact with the DUT,
    organizing signals into logical bundles and providing common
    operations for differential testing.
    """
    
    def __init__(self, dut, interface_config: Dict[str, Any]):
        """
        Initialize DUT interface.
        
        Args:
            dut: Device under test
            interface_config: Configuration defining signal bundles
        """
        self.dut = dut
        self.config = interface_config
        self.bundles = {}
        self.logger = logging.getLogger(f"cocotb.DUTInterface")
        
        # Create signal bundles
        self._create_bundles()
        
    def _create_bundles(self):
        """Create signal bundles from configuration."""
        for bundle_name, bundle_config in self.config.get('bundles', {}).items():
            signal_specs = []
            
            for signal_config in bundle_config['signals']:
                spec = SignalInfo(
                    name=signal_config['name'],
                    direction=SignalDirection(signal_config['direction']),
                    signal_type=SignalType(signal_config.get('type', 'logic')),
                    width=signal_config.get('width', 1),
                    description=signal_config.get('description', ''),
                    active_low=signal_config.get('active_low', False),
                    metadata=signal_config.get('metadata', {})
                )
                signal_specs.append(spec)
                
            self.bundles[bundle_name] = SignalBundle(bundle_name, self.dut, signal_specs)
            self.logger.info(f"Created bundle: {bundle_name} with {len(signal_specs)} signals")
            
    def get_bundle(self, name: str) -> Optional[SignalBundle]:
        """Get signal bundle by name."""
        return self.bundles.get(name)
        
    def get_clock_signal(self) -> Optional[Any]:
        """Get the main clock signal."""
        # Look for clock in bundles first
        for bundle in self.bundles.values():
            for name, spec in bundle.signal_specs.items():
                if spec.signal_type == SignalType.CLOCK:
                    return bundle.get_signal(name)
                    
        # Fall back to common clock names
        common_clock_names = ['clk', 'clock', 'CLK', 'CLOCK']
        for clock_name in common_clock_names:
            if hasattr(self.dut, clock_name):
                return getattr(self.dut, clock_name)
                
        return None
        
    def get_reset_signal(self) -> Optional[Any]:
        """Get the main reset signal."""
        # Look for reset in bundles first
        for bundle in self.bundles.values():
            for name, spec in bundle.signal_specs.items():
                if spec.signal_type == SignalType.RESET:
                    return bundle.get_signal(name), spec.active_low
                    
        # Fall back to common reset names
        common_reset_names = [('rst_n', True), ('reset_n', True), 
                            ('rst', False), ('reset', False)]
        for reset_name, active_low in common_reset_names:
            if hasattr(self.dut, reset_name):
                return getattr(self.dut, reset_name), active_low
                
        return None, False
        
    async def reset_dut(self, cycles: int = 5):
        """Reset the DUT using the identified reset signal."""
        reset_info = self.get_reset_signal()
        if reset_info[0] is None:
            self.logger.warning("No reset signal found")
            return
            
        reset_signal, active_low = reset_info
        clock_signal = self.get_clock_signal()
        
        if clock_signal is None:
            self.logger.error("No clock signal found for reset")
            return
            
        # Apply reset
        if active_low:
            reset_signal.value = 0
            await ClockCycles(clock_signal, cycles)
            reset_signal.value = 1
        else:
            reset_signal.value = 1
            await ClockCycles(clock_signal, cycles)
            reset_signal.value = 0
            
        # Wait additional cycles for reset to take effect
        await ClockCycles(clock_signal, 2)
        self.logger.info(f"DUT reset completed ({cycles} cycles)")
        
    def apply_test_vector(self, test_vector: Dict[str, Any]):
        """Apply test vector to appropriate input signals."""
        applied_signals = []
        
        for bundle in self.bundles.values():
            for signal_name in test_vector:
                if signal_name in bundle.signals:
                    spec = bundle.signal_specs[signal_name]
                    if spec.direction == SignalDirection.INPUT:
                        bundle.set_signal(signal_name, test_vector[signal_name])
                        applied_signals.append(signal_name)
                        
        # Also try direct DUT signal access for signals not in bundles
        for signal_name, value in test_vector.items():
            if signal_name not in applied_signals and hasattr(self.dut, signal_name):
                signal = getattr(self.dut, signal_name)
                signal.value = value
                applied_signals.append(signal_name)
                
        self.logger.debug(f"Applied test vector to signals: {applied_signals}")
        
    def capture_outputs(self) -> Dict[str, Any]:
        """Capture all output signals."""
        outputs = {}
        
        for bundle_name, bundle in self.bundles.items():
            bundle_outputs = bundle.get_outputs()
            if bundle_outputs:
                outputs[bundle_name] = bundle_outputs
                
        # Also capture direct DUT outputs not in bundles
        dut_outputs = {}
        for attr_name in dir(self.dut):
            if not attr_name.startswith('_'):
                try:
                    signal = getattr(self.dut, attr_name)
                    if hasattr(signal, 'value'):
                        # Check if it's not already captured in bundles
                        already_captured = False
                        for bundle in self.bundles.values():
                            if attr_name in bundle.signals:
                                already_captured = True
                                break
                                
                        if not already_captured:
                            dut_outputs[attr_name] = int(signal.value)
                except:
                    pass  # Skip attributes that can't be accessed as signals
                    
        if dut_outputs:
            outputs['dut_direct'] = dut_outputs
            
        return outputs
        
    def get_signal_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all signals."""
        info = {}
        
        for bundle_name, bundle in self.bundles.items():
            bundle_info = {}
            for signal_name, spec in bundle.signal_specs.items():
                bundle_info[signal_name] = {
                    'direction': spec.direction.value,
                    'type': spec.signal_type.value,
                    'width': spec.width,
                    'description': spec.description,
                    'active_low': spec.active_low,
                    'metadata': spec.metadata
                }
            info[bundle_name] = bundle_info
            
        return info
        
    def validate_interface(self) -> List[str]:
        """Validate that all configured signals exist in DUT."""
        missing_signals = []
        
        for bundle_name, bundle in self.bundles.items():
            for signal_name in bundle.signal_specs:
                if signal_name not in bundle.signals:
                    missing_signals.append(f"{bundle_name}.{signal_name}")
                    
        if missing_signals:
            self.logger.error(f"Missing signals: {missing_signals}")
        else:
            self.logger.info("Interface validation passed")
            
        return missing_signals


def create_standard_interface_config(clock_name: str = "clk", 
                                   reset_name: str = "rst_n",
                                   input_signals: List[str] = None,
                                   output_signals: List[str] = None) -> Dict[str, Any]:
    """
    Create a standard interface configuration.
    
    Args:
        clock_name: Name of clock signal
        reset_name: Name of reset signal  
        input_signals: List of input signal names
        output_signals: List of output signal names
        
    Returns:
        Interface configuration dictionary
    """
    config = {
        'bundles': {
            'control': {
                'signals': [
                    {
                        'name': clock_name,
                        'direction': 'input',
                        'type': 'clock',
                        'description': 'Main clock signal'
                    },
                    {
                        'name': reset_name,
                        'direction': 'input', 
                        'type': 'reset',
                        'active_low': reset_name.endswith('_n'),
                        'description': 'Reset signal'
                    }
                ]
            }
        }
    }
    
    if input_signals:
        config['bundles']['inputs'] = {
            'signals': [
                {
                    'name': signal,
                    'direction': 'input',
                    'type': 'data',
                    'description': f'Input signal {signal}'
                }
                for signal in input_signals
            ]
        }
        
    if output_signals:
        config['bundles']['outputs'] = {
            'signals': [
                {
                    'name': signal,
                    'direction': 'output',
                    'type': 'data', 
                    'description': f'Output signal {signal}'
                }
                for signal in output_signals
            ]
        }
        
    return config