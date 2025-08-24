"""
Configuration management for differential testing framework.

This module provides centralized configuration management,
including test parameters, comparison settings, and tool configurations.
"""

from .config_manager import ConfigManager, TestConfig, ComparisonConfig
from .test_profiles import TestProfile, ProfileManager
from .environment import EnvironmentManager

__all__ = [
    'ConfigManager',
    'TestConfig', 
    'ComparisonConfig',
    'TestProfile',
    'ProfileManager',
    'EnvironmentManager'
]