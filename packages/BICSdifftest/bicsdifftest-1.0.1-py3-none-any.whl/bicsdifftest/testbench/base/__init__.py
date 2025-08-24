"""
Cocotb Testbench Base Classes for Differential Testing Framework

This module provides base classes for implementing cocotb testbenches
that integrate with PyTorch golden models for comprehensive hardware verification.
"""

from .testbench_base import (
    DiffTestBase,
    TestSequence,
    TestVector,
    SignalMonitor,
    ClockGenerator
)
from .dut_interface import DUTInterface, SignalBundle
from .verification_components import (
    DataDriver,
    ResponseChecker,
    CoverageCollector
)

__all__ = [
    'DiffTestBase',
    'TestSequence',
    'TestVector', 
    'SignalMonitor',
    'ClockGenerator',
    'DUTInterface',
    'SignalBundle',
    'DataDriver',
    'ResponseChecker',
    'CoverageCollector'
]