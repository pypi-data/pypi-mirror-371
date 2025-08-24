"""
Scripts and utilities for the differential testing framework.

This module provides command-line tools, automation scripts,
and utilities for running and managing differential tests.
"""

from .logger import setup_logging, DifftestLogger
from .test_runner import TestRunner, TestRunnerConfig
from .report_generator import ReportGenerator

__all__ = [
    'setup_logging',
    'DifftestLogger',
    'TestRunner',
    'TestRunnerConfig',
    'ReportGenerator'
]