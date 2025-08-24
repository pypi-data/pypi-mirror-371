"""
Verilator integration for differential testing framework.

This module provides classes and utilities for integrating Verilator
simulation with the differential testing framework.
"""

from .verilator_runner import VerilatorRunner, VerilatorConfig
from .build_system import VerilatorBuildSystem, BuildConfig
from .simulation_manager import SimulationManager, SimulationResult

__all__ = [
    'VerilatorRunner',
    'VerilatorConfig', 
    'VerilatorBuildSystem',
    'BuildConfig',
    'SimulationManager',
    'SimulationResult'
]