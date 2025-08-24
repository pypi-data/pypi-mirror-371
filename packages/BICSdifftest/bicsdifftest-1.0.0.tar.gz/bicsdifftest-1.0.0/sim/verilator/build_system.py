"""
Build system for managing Verilator compilation and dependencies.

This module provides advanced build system functionality including
dependency tracking, incremental compilation, and build configuration management.
"""

import os
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import logging
import subprocess
import shutil


@dataclass
class BuildTarget:
    """Represents a build target with dependencies."""
    name: str
    sources: List[str]
    dependencies: List[str] = field(default_factory=list)
    build_dir: str = "build"
    compile_args: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BuildConfig:
    """Configuration for build system."""
    project_name: str
    root_dir: str
    build_dir: str = "build"
    cache_dir: str = ".build_cache"
    
    # Global compile options
    global_compile_args: List[str] = field(default_factory=list)
    global_defines: Dict[str, str] = field(default_factory=dict)
    global_includes: List[str] = field(default_factory=list)
    
    # Build behavior
    parallel_jobs: int = 1
    incremental: bool = True
    verbose: bool = False
    
    # Tool paths
    verilator_path: str = "verilator"
    make_path: str = "make"


class DependencyTracker:
    """Tracks file dependencies for incremental builds."""
    
    def __init__(self, cache_dir: str):
        """
        Initialize dependency tracker.
        
        Args:
            cache_dir: Directory to store dependency cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.dependency_file = self.cache_dir / "dependencies.json"
        self.hash_file = self.cache_dir / "file_hashes.json"
        
        self.dependencies = {}
        self.file_hashes = {}
        
        self.load_cache()
        self.logger = logging.getLogger(__name__)
        
    def load_cache(self):
        """Load dependency cache from disk."""
        if self.dependency_file.exists():
            try:
                with open(self.dependency_file, 'r') as f:
                    self.dependencies = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load dependency cache: {e}")
                
        if self.hash_file.exists():
            try:
                with open(self.hash_file, 'r') as f:
                    self.file_hashes = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load hash cache: {e}")
                
    def save_cache(self):
        """Save dependency cache to disk."""
        try:
            with open(self.dependency_file, 'w') as f:
                json.dump(self.dependencies, f, indent=2)
                
            with open(self.hash_file, 'w') as f:
                json.dump(self.file_hashes, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save dependency cache: {e}")
            
    def get_file_hash(self, filepath: str) -> str:
        """Calculate hash of file contents."""
        path = Path(filepath)
        if not path.exists():
            return ""
            
        hasher = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""
            
    def has_file_changed(self, filepath: str) -> bool:
        """Check if file has changed since last build."""
        current_hash = self.get_file_hash(filepath)
        cached_hash = self.file_hashes.get(filepath, "")
        
        changed = current_hash != cached_hash
        
        # Update cache
        if current_hash:
            self.file_hashes[filepath] = current_hash
            
        return changed
        
    def add_dependency(self, target: str, source_file: str, dependencies: List[str]):
        """Add dependency information for a target."""
        if target not in self.dependencies:
            self.dependencies[target] = {}
            
        self.dependencies[target][source_file] = {
            'dependencies': dependencies,
            'timestamp': time.time()
        }
        
    def get_dependencies(self, target: str, source_file: str) -> List[str]:
        """Get dependencies for a source file in a target."""
        return (self.dependencies
                .get(target, {})
                .get(source_file, {})
                .get('dependencies', []))
                
    def needs_rebuild(self, target: str, sources: List[str]) -> bool:
        """Check if target needs to be rebuilt."""
        # Check if any source files have changed
        for source in sources:
            if self.has_file_changed(source):
                self.logger.debug(f"Source file changed: {source}")
                return True
                
            # Check dependencies of this source file
            deps = self.get_dependencies(target, source)
            for dep in deps:
                if self.has_file_changed(dep):
                    self.logger.debug(f"Dependency file changed: {dep}")
                    return True
                    
        return False


class VerilatorBuildSystem:
    """
    Advanced build system for Verilator-based projects.
    
    Provides dependency tracking, incremental compilation, and
    multi-target build support for complex verification projects.
    """
    
    def __init__(self, config: BuildConfig):
        """
        Initialize build system.
        
        Args:
            config: Build configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Set up directories
        self.root_dir = Path(config.root_dir)
        self.build_dir = self.root_dir / config.build_dir
        self.cache_dir = self.root_dir / config.cache_dir
        
        for directory in [self.build_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Initialize dependency tracking
        self.dep_tracker = DependencyTracker(str(self.cache_dir))
        
        # Build targets
        self.targets = {}
        self.build_order = []
        
        # Build state
        self.build_stats = {
            'targets_built': 0,
            'targets_skipped': 0,
            'build_time': 0.0,
            'errors': []
        }
        
    def add_target(self, target: BuildTarget):
        """Add a build target."""
        self.targets[target.name] = target
        self.logger.info(f"Added build target: {target.name}")
        
        # Update build order
        self._calculate_build_order()
        
    def _calculate_build_order(self):
        """Calculate build order based on dependencies."""
        # Topological sort of targets
        visited = set()
        temp_visited = set()
        self.build_order = []
        
        def visit(target_name: str):
            if target_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {target_name}")
                
            if target_name not in visited:
                temp_visited.add(target_name)
                
                target = self.targets[target_name]
                for dep in target.dependencies:
                    if dep in self.targets:
                        visit(dep)
                        
                temp_visited.remove(target_name)
                visited.add(target_name)
                self.build_order.append(target_name)
                
        for target_name in self.targets:
            if target_name not in visited:
                visit(target_name)
                
        self.logger.debug(f"Build order: {self.build_order}")
        
    def build_target(self, target_name: str, force: bool = False) -> bool:
        """
        Build a specific target.
        
        Args:
            target_name: Name of target to build
            force: Force rebuild even if not needed
            
        Returns:
            True if build successful, False otherwise
        """
        if target_name not in self.targets:
            self.logger.error(f"Target {target_name} not found")
            return False
            
        target = self.targets[target_name]
        start_time = time.time()
        
        # Check if rebuild needed
        if not force and self.config.incremental:
            if not self.dep_tracker.needs_rebuild(target_name, target.sources):
                self.logger.info(f"Target {target_name} is up to date")
                self.build_stats['targets_skipped'] += 1
                return True
                
        self.logger.info(f"Building target: {target_name}")
        
        # Create target-specific build directory
        target_build_dir = self.build_dir / target_name
        target_build_dir.mkdir(parents=True, exist_ok=True)
        
        # Build dependencies first
        for dep_name in target.dependencies:
            if dep_name in self.targets:
                if not self.build_target(dep_name, force):
                    self.logger.error(f"Failed to build dependency: {dep_name}")
                    return False
                    
        # Build the target
        success = self._compile_target(target, target_build_dir)
        
        if success:
            self.build_stats['targets_built'] += 1
            build_time = time.time() - start_time
            self.build_stats['build_time'] += build_time
            self.logger.info(f"Target {target_name} built successfully ({build_time:.2f}s)")
        else:
            self.build_stats['errors'].append(f"Failed to build {target_name}")
            
        return success
        
    def _compile_target(self, target: BuildTarget, build_dir: Path) -> bool:
        """Compile a specific target."""
        cmd = [self.config.verilator_path]
        
        # Basic options
        cmd.extend(["--cc", "--exe", "-sv"])
        
        # Build directory
        cmd.extend(["-Mdir", str(build_dir)])
        
        # Global compile arguments
        cmd.extend(self.config.global_compile_args)
        
        # Target-specific compile arguments
        cmd.extend(target.compile_args)
        
        # Global defines
        for define, value in self.config.global_defines.items():
            if value:
                cmd.extend(["-D", f"{define}={value}"])
            else:
                cmd.extend(["-D", define])
                
        # Global includes
        for include_dir in self.config.global_includes:
            cmd.extend(["-I", include_dir])
            
        # Source files
        for source in target.sources:
            source_path = Path(source)
            if not source_path.is_absolute():
                source_path = self.root_dir / source_path
            cmd.append(str(source_path))
            
        # Run compilation
        try:
            log_file = build_dir / "compile.log"
            
            if self.config.verbose:
                self.logger.debug(f"Compile command: {' '.join(cmd)}")
                
            with open(log_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    cwd=self.root_dir,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    timeout=300
                )
                
            if result.returncode == 0:
                # Update dependency tracking
                self._update_dependencies(target, build_dir)
                return True
            else:
                self.logger.error(f"Compilation failed for {target.name}")
                self._log_compile_errors(log_file)
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Compilation timed out for {target.name}")
            return False
        except Exception as e:
            self.logger.error(f"Compilation error for {target.name}: {e}")
            return False
            
    def _update_dependencies(self, target: BuildTarget, build_dir: Path):
        """Update dependency information after successful build."""
        # Parse Verilator dependency file if it exists
        dep_file = build_dir / f"V{target.name}.d"
        if dep_file.exists():
            try:
                with open(dep_file, 'r') as f:
                    content = f.read()
                    
                # Parse make-style dependency file
                deps = self._parse_dependency_file(content)
                
                for source in target.sources:
                    source_deps = deps.get(source, [])
                    self.dep_tracker.add_dependency(target.name, source, source_deps)
                    
            except Exception as e:
                self.logger.warning(f"Failed to parse dependency file: {e}")
                
        # Save dependency cache
        self.dep_tracker.save_cache()
        
    def _parse_dependency_file(self, content: str) -> Dict[str, List[str]]:
        """Parse make-style dependency file."""
        dependencies = {}
        
        lines = content.split('\n')
        current_target = None
        current_deps = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if ':' in line and not line.startswith('\t'):
                # New target line
                if current_target:
                    dependencies[current_target] = current_deps
                    
                parts = line.split(':', 1)
                current_target = parts[0].strip()
                deps_part = parts[1].strip()
                
                if deps_part:
                    current_deps = [d.strip() for d in deps_part.split() if d.strip()]
                else:
                    current_deps = []
            elif line.startswith('\t') or line.startswith(' '):
                # Continuation line
                deps = [d.strip() for d in line.split() if d.strip()]
                current_deps.extend(deps)
                
        if current_target:
            dependencies[current_target] = current_deps
            
        return dependencies
        
    def _log_compile_errors(self, log_file: Path):
        """Log compilation errors."""
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    self.logger.error("Compilation output:")
                    self.logger.error(content)
            except Exception:
                pass
                
    def build_all(self, force: bool = False) -> bool:
        """
        Build all targets in dependency order.
        
        Args:
            force: Force rebuild of all targets
            
        Returns:
            True if all builds successful, False otherwise
        """
        self.logger.info("Building all targets")
        start_time = time.time()
        
        # Reset build stats
        self.build_stats = {
            'targets_built': 0,
            'targets_skipped': 0,
            'build_time': 0.0,
            'errors': []
        }
        
        success = True
        for target_name in self.build_order:
            if not self.build_target(target_name, force):
                success = False
                if not self.config.verbose:  # Stop on first error unless verbose
                    break
                    
        total_time = time.time() - start_time
        
        self.logger.info(f"Build completed in {total_time:.2f}s")
        self.logger.info(f"Targets built: {self.build_stats['targets_built']}")
        self.logger.info(f"Targets skipped: {self.build_stats['targets_skipped']}")
        
        if self.build_stats['errors']:
            self.logger.error(f"Build errors: {len(self.build_stats['errors'])}")
            for error in self.build_stats['errors']:
                self.logger.error(f"  {error}")
                
        return success
        
    def clean(self, target_name: str = None):
        """
        Clean build artifacts.
        
        Args:
            target_name: Specific target to clean, or None for all
        """
        if target_name:
            target_build_dir = self.build_dir / target_name
            if target_build_dir.exists():
                shutil.rmtree(target_build_dir)
                self.logger.info(f"Cleaned target: {target_name}")
        else:
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
                self.build_dir.mkdir(parents=True, exist_ok=True)
                
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                
            self.logger.info("Cleaned all build artifacts")
            
    def get_build_info(self) -> Dict[str, Any]:
        """Get build system information."""
        return {
            'project_name': self.config.project_name,
            'root_dir': str(self.root_dir),
            'build_dir': str(self.build_dir),
            'targets': list(self.targets.keys()),
            'build_order': self.build_order,
            'incremental_enabled': self.config.incremental,
            'build_stats': self.build_stats
        }
        
    def create_build_script(self, script_path: str = None) -> str:
        """
        Create a build script for the project.
        
        Args:
            script_path: Path to create script, defaults to root_dir/build.py
            
        Returns:
            Path to created script
        """
        script_path = script_path or str(self.root_dir / "build.py")
        
        script_content = f'''#!/usr/bin/env python3
"""
Auto-generated build script for {self.config.project_name}
Generated by BICSdifftest framework
"""

import sys
import argparse
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent))

from sim.verilator.build_system import VerilatorBuildSystem, BuildConfig, BuildTarget

def create_build_system():
    """Create and configure the build system."""
    config = BuildConfig(
        project_name="{self.config.project_name}",
        root_dir="{self.root_dir}",
        build_dir="{self.config.build_dir}",
        cache_dir="{self.config.cache_dir}",
        global_compile_args={self.config.global_compile_args},
        global_defines={self.config.global_defines},
        global_includes={self.config.global_includes},
        parallel_jobs={self.config.parallel_jobs},
        incremental={self.config.incremental}
    )
    
    build_system = VerilatorBuildSystem(config)
    
    # Add targets (customize this section)
    # Example:
    # build_system.add_target(BuildTarget(
    #     name="example",
    #     sources=["rtl/example.sv"],
    #     compile_args=["--trace"]
    # ))
    
    return build_system

def main():
    """Main build script entry point."""
    parser = argparse.ArgumentParser(description="Build script for {self.config.project_name}")
    parser.add_argument("target", nargs="?", help="Target to build (default: all)")
    parser.add_argument("--clean", action="store_true", help="Clean before building")
    parser.add_argument("--force", action="store_true", help="Force rebuild")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create build system
    build_system = create_build_system()
    
    if args.verbose:
        build_system.config.verbose = True
        
    # Clean if requested
    if args.clean:
        build_system.clean(args.target)
        
    # Build
    if args.target:
        success = build_system.build_target(args.target, args.force)
    else:
        success = build_system.build_all(args.force)
        
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        # Make executable
        os.chmod(script_path, 0o755)
        
        self.logger.info(f"Created build script at {script_path}")
        return script_path