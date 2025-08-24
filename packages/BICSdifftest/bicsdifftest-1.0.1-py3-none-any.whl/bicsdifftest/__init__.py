"""
BICSdifftest - Differential Testing Framework for Verilog Hardware Verification

A comprehensive framework for testing hardware designs by comparing Verilog RTL
implementations against PyTorch golden models using CocoTB.

Copyright (c) 2024 Guolin Yang
Licensed under the MIT License
"""

__version__ = "1.0.0"
__author__ = "Guolin Yang"
__email__ = "curryfromuestc@gmail.com"

# Safe imports with error handling
__all__ = [
    "__version__",
    "__author__",
    "__email__"
]

# Import main CLI functionality
try:
    from .cli import BICSdifftestCLI, main
    __all__.extend(["BICSdifftestCLI", "main"])
except ImportError as e:
    print(f"Warning: Could not import CLI components: {e}")

# Import key components
try:
    from .config.config_manager import ConfigManager
    __all__.append("ConfigManager")
except ImportError as e:
    print(f"Warning: Could not import ConfigManager: {e}")

try:
    from .scripts.test_runner import TestRunner
    __all__.append("TestRunner")
except ImportError as e:
    print(f"Warning: Could not import TestRunner: {e}")

try:
    from .golden_model.base.golden_model_base import GoldenModelBase
    __all__.append("GoldenModelBase")
except ImportError as e:
    print(f"Warning: Could not import GoldenModelBase: {e}")

try:
    from .testbench.base.testbench_base import TestbenchBase
    __all__.append("TestbenchBase")
except ImportError as e:
    print(f"Warning: Could not import TestbenchBase: {e}")

def get_version():
    """Get package version."""
    return __version__

def get_package_info():
    """Get package information."""
    return {
        "name": "BICSdifftest",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": "Differential Testing Framework for Verilog Hardware Verification"
    }