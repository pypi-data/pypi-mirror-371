"""
Configuration management system for the differential testing framework.

This module provides centralized configuration management with support for
different test profiles, environment-specific settings, and validation.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from abc import ABC, abstractmethod


class ComparisonMode(Enum):
    """Comparison modes for verification."""
    BIT_EXACT = "bit_exact"
    ABSOLUTE_TOLERANCE = "absolute_tolerance"
    RELATIVE_TOLERANCE = "relative_tolerance"
    ULP_TOLERANCE = "ulp_tolerance"
    CUSTOM = "custom"


@dataclass
class ComparisonConfig:
    """Configuration for data comparison."""
    mode: ComparisonMode = ComparisonMode.BIT_EXACT
    absolute_tolerance: float = 0.0
    relative_tolerance: float = 0.0
    ulp_tolerance: int = 0
    ignore_x_z: bool = False
    custom_comparator: Optional[str] = None
    
    # Signal-specific overrides
    signal_overrides: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class VerilatorConfig:
    """Verilator-specific configuration."""
    optimization_level: str = "Os"
    enable_waves: bool = True
    wave_format: str = "vcd"
    trace_depth: int = 99
    threads: int = 1
    compile_args: List[str] = field(default_factory=list)
    coverage: bool = False
    debug_mode: bool = False


@dataclass
class CocotbConfig:
    """Cocotb-specific configuration."""
    log_level: str = "INFO"
    reduced_log_fmt: bool = True
    random_seed: Optional[int] = None
    test_timeout: int = 300
    sim_timeout: int = 600


@dataclass 
class TestConfig:
    """Complete test configuration."""
    # Test identification
    name: str
    description: str = ""
    version: str = "1.0"
    
    # DUT configuration
    top_module: str = ""
    verilog_sources: List[str] = field(default_factory=list)
    include_dirs: List[str] = field(default_factory=list)
    defines: Dict[str, str] = field(default_factory=dict)
    
    # Golden model configuration
    golden_model_class: str = ""
    golden_model_config: Dict[str, Any] = field(default_factory=dict)
    
    # Test execution
    test_vectors: List[str] = field(default_factory=list)  # Paths to test vector files
    test_sequences: List[str] = field(default_factory=list)  # Test sequence names
    
    # Tool configurations
    verilator: VerilatorConfig = field(default_factory=VerilatorConfig)
    cocotb: CocotbConfig = field(default_factory=CocotbConfig)
    comparison: ComparisonConfig = field(default_factory=ComparisonConfig)
    
    # Output configuration
    work_dir: str = "sim_work"
    reports_dir: str = "reports"
    logs_dir: str = "logs"
    waves_dir: str = "waves"
    
    # Execution options
    parallel_jobs: int = 1
    continue_on_error: bool = False
    cleanup_on_success: bool = True


class ConfigValidator:
    """Validates configuration settings."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_config(self, config: TestConfig) -> List[str]:
        """
        Validate a test configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Basic validation
        if not config.name:
            errors.append("Test name is required")
            
        if not config.top_module:
            errors.append("Top module is required")
            
        if not config.verilog_sources:
            errors.append("At least one Verilog source is required")
            
        # File existence checks
        for source in config.verilog_sources:
            if not Path(source).exists():
                errors.append(f"Verilog source not found: {source}")
                
        for include_dir in config.include_dirs:
            if not Path(include_dir).exists():
                errors.append(f"Include directory not found: {include_dir}")
                
        for test_vector in config.test_vectors:
            if not Path(test_vector).exists():
                errors.append(f"Test vector file not found: {test_vector}")
                
        # Golden model validation
        if config.golden_model_class:
            # Basic class name validation
            if not config.golden_model_class.replace('.', '').replace('_', '').isalnum():
                errors.append(f"Invalid golden model class name: {config.golden_model_class}")
                
        # Tool configuration validation
        errors.extend(self._validate_verilator_config(config.verilator))
        errors.extend(self._validate_cocotb_config(config.cocotb))
        errors.extend(self._validate_comparison_config(config.comparison))
        
        return errors
        
    def _validate_verilator_config(self, config: VerilatorConfig) -> List[str]:
        """Validate Verilator configuration."""
        errors = []
        
        valid_opt_levels = ["O0", "O1", "O2", "O3", "Os"]
        if config.optimization_level not in valid_opt_levels:
            errors.append(f"Invalid optimization level: {config.optimization_level}")
            
        valid_wave_formats = ["vcd", "fst"]
        if config.wave_format not in valid_wave_formats:
            errors.append(f"Invalid wave format: {config.wave_format}")
            
        if config.threads < 1:
            errors.append("Thread count must be at least 1")
            
        if config.trace_depth < 1:
            errors.append("Trace depth must be at least 1")
            
        return errors
        
    def _validate_cocotb_config(self, config: CocotbConfig) -> List[str]:
        """Validate Cocotb configuration."""
        errors = []
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config.log_level not in valid_log_levels:
            errors.append(f"Invalid log level: {config.log_level}")
            
        if config.test_timeout < 1:
            errors.append("Test timeout must be at least 1 second")
            
        if config.sim_timeout < 1:
            errors.append("Simulation timeout must be at least 1 second")
            
        return errors
        
    def _validate_comparison_config(self, config: ComparisonConfig) -> List[str]:
        """Validate comparison configuration."""
        errors = []
        
        if config.mode == ComparisonMode.ABSOLUTE_TOLERANCE and config.absolute_tolerance < 0:
            errors.append("Absolute tolerance must be non-negative")
            
        if config.mode == ComparisonMode.RELATIVE_TOLERANCE and config.relative_tolerance < 0:
            errors.append("Relative tolerance must be non-negative")
            
        if config.mode == ComparisonMode.ULP_TOLERANCE and config.ulp_tolerance < 0:
            errors.append("ULP tolerance must be non-negative")
            
        return errors


class ConfigManager:
    """
    Central configuration manager for the differential testing framework.
    
    Handles loading, saving, and managing test configurations with support
    for multiple formats and environment-specific overrides.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.validator = ConfigValidator()
        
        # Loaded configurations
        self.configs = {}
        
        # Environment variables for overrides
        self.env_prefix = "DIFFTEST_"
        
    def load_config(self, config_file: Union[str, Path]) -> TestConfig:
        """
        Load configuration from file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Loaded TestConfig
        """
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = self.config_dir / config_path
            
        self.logger.info(f"Loading configuration from {config_path}")
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        # Load based on file extension
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            data = self._load_yaml(config_path)
        elif config_path.suffix.lower() == '.json':
            data = self._load_json(config_path)
        else:
            raise ValueError(f"Unsupported configuration format: {config_path.suffix}")
            
        # Apply environment overrides
        data = self._apply_env_overrides(data)
        
        # Convert to TestConfig
        config = self._dict_to_config(data)
        
        # Validate configuration
        errors = self.validator.validate_config(config)
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)
            
        # Cache the configuration
        self.configs[config.name] = config
        
        self.logger.info(f"Successfully loaded configuration: {config.name}")
        return config
        
    def save_config(self, config: TestConfig, output_file: Union[str, Path], format: str = "yaml"):
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save
            output_file: Output file path
            format: Output format ("yaml" or "json")
        """
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = self.config_dir / output_path
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dictionary
        data = asdict(config)
        
        # Save based on format
        if format.lower() in ['yaml', 'yml']:
            self._save_yaml(data, output_path)
        elif format.lower() == 'json':
            self._save_json(data, output_path)
        else:
            raise ValueError(f"Unsupported output format: {format}")
            
        self.logger.info(f"Configuration saved to {output_path}")
        
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        with open(file_path, 'r') as f:
            return yaml.safe_load(f) or {}
            
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON configuration file."""
        with open(file_path, 'r') as f:
            return json.load(f)
            
    def _save_yaml(self, data: Dict[str, Any], file_path: Path):
        """Save configuration as YAML."""
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
    def _save_json(self, data: Dict[str, Any], file_path: Path):
        """Save configuration as JSON."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def _apply_env_overrides(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides."""
        # Look for environment variables with the configured prefix
        overrides = {}
        
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Convert environment variable name to config path
                # e.g., DIFFTEST_VERILATOR_THREADS -> verilator.threads
                config_path = key[len(self.env_prefix):].lower().split('_')
                
                # Apply override
                current = overrides
                for part in config_path[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                    
                # Convert value to appropriate type
                try:
                    # Try to parse as JSON for complex types
                    current[config_path[-1]] = json.loads(value)
                except json.JSONDecodeError:
                    # Fall back to string
                    current[config_path[-1]] = value
                    
        # Merge overrides into data
        data = self._deep_merge(data, overrides)
        
        if overrides:
            self.logger.debug(f"Applied environment overrides: {overrides}")
            
        return data
        
    def _deep_merge(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def _dict_to_config(self, data: Dict[str, Any]) -> TestConfig:
        """Convert dictionary to TestConfig object."""
        # Handle nested configurations
        if 'verilator' in data and isinstance(data['verilator'], dict):
            data['verilator'] = VerilatorConfig(**data['verilator'])
            
        if 'cocotb' in data and isinstance(data['cocotb'], dict):
            data['cocotb'] = CocotbConfig(**data['cocotb'])
            
        if 'comparison' in data and isinstance(data['comparison'], dict):
            comparison_data = data['comparison'].copy()
            if 'mode' in comparison_data:
                comparison_data['mode'] = ComparisonMode(comparison_data['mode'])
            data['comparison'] = ComparisonConfig(**comparison_data)
            
        return TestConfig(**data)
        
    def get_config(self, name: str) -> Optional[TestConfig]:
        """Get cached configuration by name."""
        return self.configs.get(name)
        
    def list_configs(self) -> List[str]:
        """List all loaded configuration names."""
        return list(self.configs.keys())
        
    def create_default_config(self, name: str, top_module: str, 
                            verilog_sources: List[str]) -> TestConfig:
        """
        Create a default configuration.
        
        Args:
            name: Configuration name
            top_module: Top-level module name
            verilog_sources: List of Verilog source files
            
        Returns:
            Default TestConfig
        """
        config = TestConfig(
            name=name,
            description=f"Default configuration for {name}",
            top_module=top_module,
            verilog_sources=verilog_sources,
            golden_model_class=f"golden_model.models.{name.lower()}.GoldenModel"
        )
        
        self.configs[name] = config
        return config
        
    def export_template(self, template_file: str = "config_template.yaml"):
        """Export a configuration template."""
        template_path = self.config_dir / template_file
        
        # Create a sample configuration
        sample_config = TestConfig(
            name="example_test",
            description="Example test configuration",
            top_module="example_dut",
            verilog_sources=["rtl/example_dut.sv"],
            include_dirs=["rtl/common"],
            defines={"SIMULATION": "1"},
            golden_model_class="golden_model.models.example.ExampleGoldenModel",
            test_sequences=["basic_test", "corner_cases"]
        )
        
        self.save_config(sample_config, template_path, "yaml")
        self.logger.info(f"Configuration template exported to {template_path}")