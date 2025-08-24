"""
Test profiles management for differential testing framework.

This module provides predefined test configurations and profile management
for different testing scenarios and environments.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
import json
from pathlib import Path


class TestProfileType(Enum):
    """Types of test profiles."""
    QUICK = "quick"
    FULL = "full"  
    REGRESSION = "regression"
    DEBUG = "debug"
    PERFORMANCE = "performance"


@dataclass
class TestProfile:
    """
    Test profile configuration.
    
    Defines a complete test configuration including simulation parameters,
    comparison settings, and execution options.
    """
    name: str
    profile_type: TestProfileType
    description: str = ""
    
    # Simulation settings
    timeout: int = 100000
    clock_period: int = 10
    reset_cycles: int = 5
    
    # Test generation
    num_random_tests: int = 100
    test_seed: Optional[int] = None
    
    # Comparison settings
    comparison_mode: str = "exact"
    tolerance: float = 1e-6
    ulp_tolerance: int = 4
    
    # Execution settings
    parallel: bool = True
    max_workers: int = 4
    
    # Debug settings
    generate_waves: bool = False
    debug_level: str = "INFO"
    save_checkpoints: bool = False
    
    # Advanced settings
    extra_args: Dict[str, Any] = field(default_factory=dict)


class ProfileManager:
    """
    Manages test profiles and provides profile-based configuration.
    
    Handles loading, saving, and applying test profiles for different
    testing scenarios.
    """
    
    def __init__(self, profiles_dir: Optional[Path] = None):
        """Initialize profile manager."""
        self.profiles_dir = profiles_dir or Path(__file__).parent / "profiles"
        self.profiles: Dict[str, TestProfile] = {}
        self._load_default_profiles()
    
    def _load_default_profiles(self):
        """Load default test profiles."""
        # Quick profile for fast testing
        self.profiles["quick"] = TestProfile(
            name="quick",
            profile_type=TestProfileType.QUICK,
            description="Quick test profile for fast verification",
            timeout=10000,
            num_random_tests=10,
            parallel=True,
            max_workers=2,
            generate_waves=False,
            debug_level="WARNING"
        )
        
        # Full profile for comprehensive testing
        self.profiles["full"] = TestProfile(
            name="full",
            profile_type=TestProfileType.FULL,
            description="Full test profile for comprehensive verification",
            timeout=100000,
            num_random_tests=1000,
            parallel=True,
            max_workers=4,
            generate_waves=True,
            debug_level="INFO",
            save_checkpoints=True
        )
        
        # Debug profile for debugging
        self.profiles["debug"] = TestProfile(
            name="debug",
            profile_type=TestProfileType.DEBUG,
            description="Debug profile with detailed logging and waves",
            timeout=100000,
            num_random_tests=10,
            parallel=False,
            max_workers=1,
            generate_waves=True,
            debug_level="DEBUG",
            save_checkpoints=True
        )
        
        # Performance profile
        self.profiles["performance"] = TestProfile(
            name="performance",
            profile_type=TestProfileType.PERFORMANCE,
            description="Performance testing with timing analysis",
            timeout=1000000,
            num_random_tests=10000,
            parallel=True,
            max_workers=8,
            generate_waves=False,
            debug_level="WARNING"
        )
    
    def get_profile(self, name: str) -> Optional[TestProfile]:
        """Get test profile by name."""
        return self.profiles.get(name)
    
    def list_profiles(self) -> List[str]:
        """List available profile names."""
        return list(self.profiles.keys())
    
    def add_profile(self, profile: TestProfile):
        """Add a custom test profile."""
        self.profiles[profile.name] = profile
    
    def save_profile(self, profile: TestProfile, path: Optional[Path] = None):
        """Save test profile to file."""
        if path is None:
            self.profiles_dir.mkdir(exist_ok=True)
            path = self.profiles_dir / f"{profile.name}.json"
        
        profile_data = {
            "name": profile.name,
            "profile_type": profile.profile_type.value,
            "description": profile.description,
            "timeout": profile.timeout,
            "clock_period": profile.clock_period,
            "reset_cycles": profile.reset_cycles,
            "num_random_tests": profile.num_random_tests,
            "test_seed": profile.test_seed,
            "comparison_mode": profile.comparison_mode,
            "tolerance": profile.tolerance,
            "ulp_tolerance": profile.ulp_tolerance,
            "parallel": profile.parallel,
            "max_workers": profile.max_workers,
            "generate_waves": profile.generate_waves,
            "debug_level": profile.debug_level,
            "save_checkpoints": profile.save_checkpoints,
            "extra_args": profile.extra_args
        }
        
        with open(path, 'w') as f:
            json.dump(profile_data, f, indent=2)
    
    def load_profile(self, path: Path) -> TestProfile:
        """Load test profile from file."""
        with open(path, 'r') as f:
            data = json.load(f)
        
        return TestProfile(
            name=data["name"],
            profile_type=TestProfileType(data["profile_type"]),
            description=data.get("description", ""),
            timeout=data.get("timeout", 100000),
            clock_period=data.get("clock_period", 10),
            reset_cycles=data.get("reset_cycles", 5),
            num_random_tests=data.get("num_random_tests", 100),
            test_seed=data.get("test_seed"),
            comparison_mode=data.get("comparison_mode", "exact"),
            tolerance=data.get("tolerance", 1e-6),
            ulp_tolerance=data.get("ulp_tolerance", 4),
            parallel=data.get("parallel", True),
            max_workers=data.get("max_workers", 4),
            generate_waves=data.get("generate_waves", False),
            debug_level=data.get("debug_level", "INFO"),
            save_checkpoints=data.get("save_checkpoints", False),
            extra_args=data.get("extra_args", {})
        )
    
    def apply_profile(self, profile_name: str, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply test profile to base configuration."""
        profile = self.get_profile(profile_name)
        if not profile:
            raise ValueError(f"Profile '{profile_name}' not found")
        
        config = base_config.copy()
        
        # Apply profile settings
        if "simulation" not in config:
            config["simulation"] = {}
        
        config["simulation"].update({
            "timeout": profile.timeout,
            "clock_period": profile.clock_period,
            "reset_cycles": profile.reset_cycles,
            "waves": profile.generate_waves
        })
        
        if "testing" not in config:
            config["testing"] = {}
            
        config["testing"].update({
            "num_random_tests": profile.num_random_tests,
            "test_seed": profile.test_seed,
            "parallel": profile.parallel,
            "max_workers": profile.max_workers
        })
        
        if "comparison" not in config:
            config["comparison"] = {}
            
        config["comparison"].update({
            "mode": profile.comparison_mode,
            "tolerance": profile.tolerance,
            "ulp_tolerance": profile.ulp_tolerance
        })
        
        if "logging" not in config:
            config["logging"] = {}
            
        config["logging"].update({
            "level": profile.debug_level,
            "save_checkpoints": profile.save_checkpoints
        })
        
        # Apply extra args
        config.update(profile.extra_args)
        
        return config