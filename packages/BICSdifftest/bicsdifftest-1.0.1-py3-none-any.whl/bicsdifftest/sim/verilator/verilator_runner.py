"""
Verilator runner for executing simulations with cocotb integration.

This module provides the main interface for running Verilator simulations
within the differential testing framework.
"""

import os
import subprocess
import shlex
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
import logging
import json
import tempfile
import shutil


@dataclass
class VerilatorConfig:
    """Configuration for Verilator simulation."""
    
    # Core configuration
    top_module: str
    verilog_sources: List[str]
    testbench_module: str
    
    # Compilation options
    compile_args: List[str] = field(default_factory=lambda: [
        "-Wall", "-Wno-TIMESCALEMOD", "-Wno-DECLFILENAME"
    ])
    
    # Simulation options
    sim_args: List[str] = field(default_factory=list)
    
    # Cocotb specific
    cocotb_module: str = ""
    python_search_path: List[str] = field(default_factory=list)
    
    # Output control
    enable_waves: bool = True
    wave_format: str = "vcd"  # vcd, fst
    trace_depth: int = 99
    
    # Performance options
    optimization_level: str = "Os"  # O0, O1, O2, O3, Os
    threads: int = 1
    
    # Directory paths
    work_dir: Optional[str] = None
    build_dir: Optional[str] = None
    
    # Debug options
    debug_mode: bool = False
    coverage: bool = False
    
    # Timeout
    timeout_seconds: int = 300


class VerilatorRunner:
    """
    Verilator simulation runner with cocotb integration.
    
    This class handles the complete workflow of compiling and running
    Verilog designs with Verilator, integrated with cocotb testbenches.
    """
    
    def __init__(self, config: VerilatorConfig):
        """
        Initialize Verilator runner.
        
        Args:
            config: Verilator configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Set up directories
        self.work_dir = Path(config.work_dir or "sim_work")
        self.build_dir = Path(config.build_dir or self.work_dir / "build")
        self.waves_dir = self.work_dir / "waves"
        self.logs_dir = self.work_dir / "logs"
        
        # Create directories
        for directory in [self.work_dir, self.build_dir, self.waves_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Runtime state
        self.compiled = False
        self.simulation_process = None
        
    def compile(self) -> bool:
        """
        Compile Verilog sources with Verilator.
        
        Returns:
            True if compilation successful, False otherwise
        """
        self.logger.info(f"Compiling {self.config.top_module} with Verilator")
        
        # Prepare compilation command
        cmd = self._build_compile_command()
        
        try:
            # Run compilation
            self.logger.debug(f"Compile command: {' '.join(cmd)}")
            
            with open(self.logs_dir / "compile.log", "w") as log_file:
                result = subprocess.run(
                    cmd,
                    cwd=self.work_dir,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    timeout=self.config.timeout_seconds
                )
                
            if result.returncode == 0:
                self.compiled = True
                self.logger.info("Compilation successful")
                return True
            else:
                self.logger.error(f"Compilation failed with return code {result.returncode}")
                self._log_compile_errors()
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Compilation timed out after {self.config.timeout_seconds} seconds")
            return False
        except Exception as e:
            self.logger.error(f"Compilation error: {str(e)}")
            return False
            
    def _build_compile_command(self) -> List[str]:
        """Build the Verilator compilation command."""
        cmd = ["verilator"]
        
        # Basic options
        cmd.extend(["--cc", "--exe"])
        cmd.extend(["-sv"])  # SystemVerilog support
        
        # Top module
        cmd.extend(["--top-module", self.config.top_module])
        
        # Optimization
        cmd.extend([f"-{self.config.optimization_level}"])
        
        # Threading
        if self.config.threads > 1:
            cmd.extend(["--threads", str(self.config.threads)])
            
        # Debug options
        if self.config.debug_mode:
            cmd.extend(["--debug", "--gdbbt"])
            
        # Coverage
        if self.config.coverage:
            cmd.extend(["--coverage"])
            
        # Tracing
        if self.config.enable_waves:
            if self.config.wave_format == "fst":
                cmd.extend(["--trace-fst"])
            else:
                cmd.extend(["--trace"])
            cmd.extend(["--trace-depth", str(self.config.trace_depth)])
            
        # Build directory
        cmd.extend(["-Mdir", str(self.build_dir)])
        
        # Additional compile arguments
        cmd.extend(self.config.compile_args)
        
        # Verilog source files
        for source in self.config.verilog_sources:
            source_path = Path(source)
            if not source_path.is_absolute():
                source_path = self.work_dir / source_path
            cmd.append(str(source_path))
            
        # Testbench/main file
        cmd.append(self.config.testbench_module)
        
        return cmd
        
    def _log_compile_errors(self):
        """Log compilation errors from log file."""
        compile_log = self.logs_dir / "compile.log"
        if compile_log.exists():
            with open(compile_log, 'r') as f:
                log_content = f.read()
                self.logger.error("Compilation errors:")
                self.logger.error(log_content)
                
    def run_simulation(self, test_name: str = "default") -> bool:
        """
        Run the compiled simulation.
        
        Args:
            test_name: Name of the test for logging
            
        Returns:
            True if simulation completed successfully, False otherwise
        """
        if not self.compiled:
            self.logger.error("Cannot run simulation: design not compiled")
            return False
            
        self.logger.info(f"Running simulation: {test_name}")
        
        # Set up environment for cocotb
        env = self._setup_simulation_environment()
        
        # Build simulation command
        cmd = self._build_simulation_command()
        
        try:
            # Run simulation
            self.logger.debug(f"Simulation command: {' '.join(cmd)}")
            
            with open(self.logs_dir / f"{test_name}_sim.log", "w") as log_file:
                self.simulation_process = subprocess.run(
                    cmd,
                    cwd=self.work_dir,
                    env=env,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    timeout=self.config.timeout_seconds
                )
                
            if self.simulation_process.returncode == 0:
                self.logger.info("Simulation completed successfully")
                return True
            else:
                self.logger.error(f"Simulation failed with return code {self.simulation_process.returncode}")
                self._log_simulation_errors(test_name)
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Simulation timed out after {self.config.timeout_seconds} seconds")
            return False
        except Exception as e:
            self.logger.error(f"Simulation error: {str(e)}")
            return False
            
    def _setup_simulation_environment(self) -> Dict[str, str]:
        """Set up environment variables for simulation."""
        env = os.environ.copy()
        
        # Cocotb configuration
        if self.config.cocotb_module:
            env["MODULE"] = self.config.cocotb_module
            
        # Python path
        python_paths = [str(self.work_dir)]
        python_paths.extend(self.config.python_search_path)
        
        if "PYTHONPATH" in env:
            python_paths.append(env["PYTHONPATH"])
            
        env["PYTHONPATH"] = ":".join(python_paths)
        
        # Simulation configuration
        env["SIM"] = "verilator"
        env["TOPLEVEL"] = self.config.top_module
        
        # Wave generation
        if self.config.enable_waves:
            env["WAVES"] = "1"
            
        # Additional environment variables
        env["COCOTB_REDUCED_LOG_FMT"] = "1"
        
        return env
        
    def _build_simulation_command(self) -> List[str]:
        """Build the simulation execution command."""
        # The compiled executable
        exe_name = f"V{self.config.top_module}"
        exe_path = self.build_dir / exe_name
        
        cmd = [str(exe_path)]
        
        # Add simulation arguments
        cmd.extend(self.config.sim_args)
        
        # Add wave file if tracing enabled
        if self.config.enable_waves:
            wave_file = self.waves_dir / f"waves.{self.config.wave_format}"
            if self.config.wave_format == "fst":
                cmd.extend(["+trace"])
            else:
                cmd.extend(["+trace"])
                
        return cmd
        
    def _log_simulation_errors(self, test_name: str):
        """Log simulation errors from log file."""
        sim_log = self.logs_dir / f"{test_name}_sim.log"
        if sim_log.exists():
            with open(sim_log, 'r') as f:
                log_content = f.read()
                self.logger.error("Simulation errors:")
                self.logger.error(log_content)
                
    def run_cocotb_test(self, test_module: str, test_name: str = None) -> bool:
        """
        Run a cocotb test.
        
        Args:
            test_module: Python module containing the test
            test_name: Specific test function to run
            
        Returns:
            True if test passed, False otherwise
        """
        if not self.compiled:
            if not self.compile():
                return False
                
        # Set up cocotb environment
        env = self._setup_simulation_environment()
        env["MODULE"] = test_module
        
        if test_name:
            env["TESTCASE"] = test_name
            
        # Use make for cocotb integration
        cmd = ["make", "-f", "Makefile.cocotb"]
        
        try:
            self.logger.info(f"Running cocotb test: {test_module}::{test_name or 'all'}")
            
            log_file_name = f"cocotb_{test_module}_{test_name or 'all'}.log"
            
            with open(self.logs_dir / log_file_name, "w") as log_file:
                result = subprocess.run(
                    cmd,
                    cwd=self.work_dir,
                    env=env,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    timeout=self.config.timeout_seconds
                )
                
            success = result.returncode == 0
            
            if success:
                self.logger.info("Cocotb test passed")
            else:
                self.logger.error("Cocotb test failed")
                with open(self.logs_dir / log_file_name, 'r') as f:
                    self.logger.error(f.read())
                    
            return success
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Cocotb test timed out after {self.config.timeout_seconds} seconds")
            return False
        except Exception as e:
            self.logger.error(f"Cocotb test error: {str(e)}")
            return False
            
    def clean(self):
        """Clean build artifacts."""
        self.logger.info("Cleaning build artifacts")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            self.build_dir.mkdir(parents=True, exist_ok=True)
            
        # Clean wave files
        for wave_file in self.waves_dir.glob("*"):
            if wave_file.is_file():
                wave_file.unlink()
                
        self.compiled = False
        
    def get_build_info(self) -> Dict[str, Any]:
        """Get information about the build."""
        info = {
            'top_module': self.config.top_module,
            'compiled': self.compiled,
            'work_dir': str(self.work_dir),
            'build_dir': str(self.build_dir),
            'verilog_sources': self.config.verilog_sources,
            'wave_enabled': self.config.enable_waves,
            'wave_format': self.config.wave_format
        }
        
        # Add file information if compiled
        if self.compiled:
            exe_name = f"V{self.config.top_module}"
            exe_path = self.build_dir / exe_name
            info['executable'] = str(exe_path)
            info['executable_exists'] = exe_path.exists()
            
        return info
        
    def create_makefile(self, makefile_path: str = None) -> str:
        """
        Create a Makefile for cocotb integration.
        
        Args:
            makefile_path: Path to create Makefile, defaults to work_dir/Makefile.cocotb
            
        Returns:
            Path to created Makefile
        """
        makefile_path = makefile_path or str(self.work_dir / "Makefile.cocotb")
        
        makefile_content = f"""# Auto-generated Makefile for cocotb integration
# Generated by BICSdifftest framework

# Simulator
SIM ?= verilator

# Top level module
TOPLEVEL ?= {self.config.top_module}

# Verilog sources
VERILOG_SOURCES = {' '.join(self.config.verilog_sources)}

# Cocotb module
MODULE ?= {self.config.cocotb_module}

# Compile arguments
COMPILE_ARGS = {' '.join(self.config.compile_args)}

# Simulation arguments  
SIM_ARGS = {' '.join(self.config.sim_args)}

# Additional Verilator arguments
ifeq ($(SIM),verilator)
    COMPILE_ARGS += --trace --trace-depth {self.config.trace_depth}
    COMPILE_ARGS += -{self.config.optimization_level}
    COMPILE_ARGS += -Mdir {self.build_dir}
    
    ifneq ($(THREADS),)
        COMPILE_ARGS += --threads $(THREADS)
    endif
endif

# Include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

# Custom targets
.PHONY: clean compile run waves

clean:
\t@echo "Cleaning build artifacts"
\trm -rf {self.build_dir}/*
\trm -rf {self.waves_dir}/*
\trm -rf {self.logs_dir}/*

compile: $(TOPLEVEL).so

run: compile
\t@echo "Running simulation"
\t$(MAKE) sim

waves:
\t@echo "Opening waveform viewer"
\tgtkwave {self.waves_dir}/waves.vcd &

# Debug target
debug: COMPILE_ARGS += --debug --gdbbt
debug: compile
\t@echo "Running simulation in debug mode"
\t$(MAKE) sim
"""
        
        with open(makefile_path, 'w') as f:
            f.write(makefile_content)
            
        self.logger.info(f"Created Makefile at {makefile_path}")
        return makefile_path