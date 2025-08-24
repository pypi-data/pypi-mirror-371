"""
Environment management for differential testing framework.

This module handles environment variable management, tool detection,
and system configuration for the testing framework.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import subprocess
import logging


@dataclass
class ToolConfig:
    """Configuration for external tools."""
    name: str
    executable: str
    version_cmd: Optional[str] = None
    required: bool = True
    min_version: Optional[str] = None
    found: bool = False
    version: Optional[str] = None
    path: Optional[Path] = None


class EnvironmentManager:
    """
    Manages environment configuration and tool detection.
    
    Handles detection of required tools, environment variable management,
    and system configuration validation.
    """
    
    def __init__(self):
        """Initialize environment manager."""
        self.logger = logging.getLogger(__name__)
        self.tools: Dict[str, ToolConfig] = {}
        self.env_vars: Dict[str, str] = {}
        self._setup_required_tools()
    
    def _setup_required_tools(self):
        """Setup required tool configurations."""
        self.tools = {
            "verilator": ToolConfig(
                name="Verilator",
                executable="verilator", 
                version_cmd="verilator --version",
                required=True,
                min_version="4.0"
            ),
            "python": ToolConfig(
                name="Python",
                executable="python3",
                version_cmd="python3 --version",
                required=True,
                min_version="3.8"
            ),
            "make": ToolConfig(
                name="Make",
                executable="make",
                version_cmd="make --version",
                required=True
            ),
            "cocotb": ToolConfig(
                name="CocoTB",
                executable="python3",
                version_cmd="python3 -c 'import cocotb; print(cocotb.__version__)'",
                required=True
            ),
            "pytorch": ToolConfig(
                name="PyTorch",
                executable="python3",
                version_cmd="python3 -c 'import torch; print(torch.__version__)'",
                required=True
            ),
            "gtkwave": ToolConfig(
                name="GTKWave",
                executable="gtkwave",
                version_cmd="gtkwave --version",
                required=False
            )
        }
    
    def check_tools(self) -> bool:
        """Check availability of all required tools."""
        all_found = True
        
        for tool_name, tool_config in self.tools.items():
            found = self._check_tool(tool_config)
            self.tools[tool_name] = tool_config
            
            if not found and tool_config.required:
                all_found = False
                self.logger.error(f"Required tool '{tool_config.name}' not found")
            elif found:
                self.logger.info(f"Found {tool_config.name} {tool_config.version} at {tool_config.path}")
        
        return all_found
    
    def _check_tool(self, tool_config: ToolConfig) -> bool:
        """Check if a specific tool is available."""
        try:
            # Find executable
            path = shutil.which(tool_config.executable)
            if not path:
                return False
            
            tool_config.path = Path(path)
            tool_config.found = True
            
            # Get version if command provided
            if tool_config.version_cmd:
                try:
                    result = subprocess.run(
                        tool_config.version_cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        # Extract version from output
                        output = result.stdout.strip()
                        if not output:
                            output = result.stderr.strip()
                        tool_config.version = self._extract_version(output)
                
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    pass
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Error checking tool {tool_config.name}: {e}")
            return False
    
    def _extract_version(self, version_output: str) -> str:
        """Extract version number from tool output."""
        # Simple version extraction - can be enhanced
        import re
        
        # Look for version patterns like "1.2.3", "v1.2.3", etc.
        patterns = [
            r'(\d+\.\d+\.\d+)',
            r'(\d+\.\d+)',
            r'version\s+(\d+\.\d+\.\d+)',
            r'v(\d+\.\d+\.\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, version_output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return version_output.split()[0] if version_output else "unknown"
    
    def setup_environment(self) -> Dict[str, str]:
        """Setup environment variables for testing."""
        env = os.environ.copy()
        
        # Add project paths
        project_root = Path(__file__).parent.parent
        env["DIFFTEST_ROOT"] = str(project_root)
        env["PYTHONPATH"] = str(project_root) + ":" + env.get("PYTHONPATH", "")
        
        # CocoTB settings
        env["COCOTB_REDUCED_LOG_FMT"] = "1"
        
        # Verilator settings
        env["VERILATOR_ROOT"] = env.get("VERILATOR_ROOT", "")
        
        # Store environment variables
        self.env_vars = env
        return env
    
    def get_tool_path(self, tool_name: str) -> Optional[Path]:
        """Get path to a specific tool."""
        tool_config = self.tools.get(tool_name)
        return tool_config.path if tool_config and tool_config.found else None
    
    def is_tool_available(self, tool_name: str) -> bool:
        """Check if a specific tool is available."""
        tool_config = self.tools.get(tool_name)
        return tool_config.found if tool_config else False
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive environment information."""
        return {
            "tools": {
                name: {
                    "found": config.found,
                    "version": config.version,
                    "path": str(config.path) if config.path else None,
                    "required": config.required
                }
                for name, config in self.tools.items()
            },
            "python_path": os.environ.get("PYTHONPATH", ""),
            "project_root": str(Path(__file__).parent.parent),
            "working_directory": str(Path.cwd())
        }
    
    def validate_environment(self) -> List[str]:
        """Validate environment and return list of issues."""
        issues = []
        
        # Check required tools
        for name, config in self.tools.items():
            if config.required and not config.found:
                issues.append(f"Required tool '{config.name}' not found")
        
        # Check Python packages
        required_packages = [
            "cocotb",
            "torch", 
            "numpy",
            "pyyaml"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                issues.append(f"Required Python package '{package}' not installed")
        
        # Check directories
        project_root = Path(__file__).parent.parent
        required_dirs = [
            "golden_model",
            "testbench", 
            "sim",
            "config"
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                issues.append(f"Required directory '{dir_name}' not found")
        
        return issues
    
    def setup_logging_environment(self) -> Dict[str, str]:
        """Setup environment variables for logging."""
        env = self.env_vars.copy()
        
        # Create log directories
        project_root = Path(__file__).parent.parent
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        env["DIFFTEST_LOG_DIR"] = str(log_dir)
        
        return env