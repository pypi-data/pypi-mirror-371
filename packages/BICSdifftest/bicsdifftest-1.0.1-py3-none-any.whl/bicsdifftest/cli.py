#!/usr/bin/env python3
"""
BICSdifftest CLI - Command Line Interface for the Differential Testing Framework

This module provides the main entry point for the BICSdifftest command-line tool,
allowing users to create workspaces, run tests, and manage configurations.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import pkg_resources

# Import using relative imports within the package
try:
    from .scripts.test_runner import main as run_tests
except ImportError:
    run_tests = None
try:
    from .config.config_manager import ConfigManager
except ImportError:
    ConfigManager = None


class BICSdifftestCLI:
    """Main CLI class for BICSdifftest framework."""
    
    def __init__(self):
        # 首先尝试从当前文件定位到源码根目录
        current_file = Path(__file__)
        if 'site-packages' in str(current_file):
            # 如果是从安装的包运行，尝试找到源码目录
            possible_roots = [
                Path('/home/yanggl/code/BICSdifftest'),
                Path.cwd(),
                current_file.parent.parent  # 最后的fallback
            ]
            for root in possible_roots:
                if root.exists() and (root / 'bicsdifftest' / 'examples').exists():
                    self.framework_root = root
                    break
            else:
                self.framework_root = current_file.parent.parent
        else:
            # 如果是从源码运行，使用相对路径
            self.framework_root = current_file.parent.parent
        
    def create_workspace(self, workspace_name: str, target_dir: Optional[str] = None, force: bool = False) -> bool:
        """
        Create a new BICSdifftest workspace by copying the entire framework.
        
        Args:
            workspace_name: Name of the workspace to create
            target_dir: Target directory (default: current directory)
            force: Overwrite existing workspace if it exists
            
        Returns:
            True if workspace was created successfully, False otherwise
        """
        if target_dir is None:
            target_dir = os.getcwd()
            
        target_path = Path(target_dir)
        workspace_path = target_path / workspace_name
        
        # Validate workspace name
        if not self._is_valid_workspace_name(workspace_name):
            print(f"Error: Invalid workspace name '{workspace_name}'")
            print("Workspace name must be a valid directory name (alphanumeric, underscore, dash)")
            return False
            
        # Check if workspace already exists
        if workspace_path.exists():
            if not force:
                print(f"Error: Workspace '{workspace_name}' already exists at {workspace_path}")
                print("Use --force to overwrite existing workspace")
                return False
            else:
                print(f"Warning: Overwriting existing workspace at {workspace_path}")
                shutil.rmtree(workspace_path)
        
        try:
            # Copy the entire BICSdifftest framework
            print(f"Copying BICSdifftest framework from {self.framework_root} to {workspace_path}...")
            
            # 检查是否会造成递归复制
            if workspace_path.is_relative_to(self.framework_root):
                print(f"Error: Cannot create workspace inside framework directory")
                print(f"Framework root: {self.framework_root}")
                print(f"Workspace path: {workspace_path}")
                return False
            
            # 手动复制只复制必要的目录
            workspace_path.mkdir(parents=True, exist_ok=True)
            
            # 只复制关键目录
            essential_dirs = ['bicsdifftest', 'README.md', 'README_ZH.md', 'pyproject.toml']
            
            for item_name in essential_dirs:
                source_item = self.framework_root / item_name
                dest_item = workspace_path / item_name
                
                if source_item.exists():
                    if source_item.is_file():
                        print(f"Copying file: {item_name}")
                        shutil.copy2(source_item, dest_item)
                    elif source_item.is_dir():
                        print(f"Copying directory: {item_name}")
                        def ignore_func(dir_path, files):
                            ignore = []
                            for file in files:
                                if (file.startswith('.') or 
                                    file in ['__pycache__', 'logs', 'sim_build', 'test_work'] or
                                    file.endswith('.pyc') or file.endswith('.pyo')):
                                    ignore.append(file)
                            return ignore
                        shutil.copytree(source_item, dest_item, ignore=ignore_func)
            
            print(f"Successfully created BICSdifftest workspace: {workspace_path}")
            print(f"\nNext steps:")
            print(f"1. cd {workspace_name}")
            print(f"2. Add your hardware designs to the 'bicsdifftest/examples/' directory")
            print(f"3. Modify existing examples or create new ones")  
            print(f"4. Run tests directly from the bicsdifftest/examples/ directory")
            return True
            
        except Exception as e:
            print(f"Error creating workspace: {e}")
            return False
    
    def _is_valid_workspace_name(self, name: str) -> bool:
        """Check if workspace name is valid."""
        if not name or name.startswith('.') or name.startswith('-'):
            return False
        # Allow alphanumeric, underscore, and dash
        return all(c.isalnum() or c in '_-' for c in name)
    
    def _copy_framework_to_workspace(self, workspace_path: Path):
        """Copy the entire BICSdifftest framework to the workspace directory."""
        # Create the workspace directory
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Copying BICSdifftest framework from {self.framework_root} to {workspace_path}...")
        
        # Define directories and files to exclude during copy
        exclude_patterns = {
            '__pycache__',
            '.git',
            '.gitignore', 
            'dist',
            'build',
            '*.egg-info',
            'test_env',
            '.pytest_cache',
            'node_modules',
            '*.pyc',
            '*.pyo',
            '.DS_Store',
            'Thumbs.db',
            'logs',  # Exclude logs to start fresh
            'sim_build',  # Exclude build artifacts
            'test_work'   # Exclude temp work directory
        }
        
        # Copy the entire framework directory
        self._copy_directory_filtered(self.framework_root, workspace_path, exclude_patterns)
        
        print("Framework copied successfully!")
        print(f"Cleaned up build artifacts and temporary files.")
    
    def _copy_directory_filtered(self, source_dir: Path, dest_dir: Path, exclude_patterns: set):
        """Copy directory contents with filtering to exclude unwanted files/directories."""
        import fnmatch
        
        for item in source_dir.iterdir():
            # Check if item should be excluded
            should_exclude = False
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(item.name, pattern) or item.name in exclude_patterns:
                    should_exclude = True
                    break
            
            if should_exclude:
                print(f"Excluding: {item.name}")
                continue
            
            dest_item = dest_dir / item.name
            
            if item.is_dir():
                # Recursively copy directories
                dest_item.mkdir(exist_ok=True)
                self._copy_directory_filtered(item, dest_item, exclude_patterns)
            else:
                # Copy files
                shutil.copy2(item, dest_item)



def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="BICSdifftest - Differential Testing Framework for Verilog Hardware",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  bicsdifftest build my_project          # Create workspace in current directory
  bicsdifftest build my_project --force  # Overwrite existing workspace
  bicsdifftest test                      # Run tests in current workspace
  bicsdifftest test --parallel 4         # Run tests with 4 parallel jobs
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build command
    build_parser = subparsers.add_parser(
        'build', 
        help='Create a new BICSdifftest workspace'
    )
    build_parser.add_argument(
        'workspace_name',
        help='Name of the workspace to create'
    )
    build_parser.add_argument(
        '--target-dir',
        help='Target directory (default: current directory)'
    )
    build_parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing workspace'
    )
    
    # Test command
    test_parser = subparsers.add_parser(
        'test',
        help='Run tests in current workspace'
    )
    test_parser.add_argument('--parallel', '-j', type=int, default=1, help='Number of parallel jobs')
    test_parser.add_argument('--test-filter', help='Filter tests by name')
    test_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    test_parser.add_argument('--continue-on-error', action='store_true', help='Continue after failures')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    cli = BICSdifftestCLI()
    
    if args.command == 'build':
        success = cli.create_workspace(
            args.workspace_name,
            args.target_dir,
            args.force
        )
        return 0 if success else 1
        
    elif args.command == 'test':
        # Run tests using the existing test runner
        sys.argv = ['test_runner.py']
        if args.parallel > 1:
            sys.argv.extend(['--parallel', str(args.parallel)])
        if args.test_filter:
            sys.argv.extend(['--test-filter', args.test_filter])
        if args.verbose:
            sys.argv.extend(['--log-level', 'DEBUG'])
        if args.continue_on_error:
            sys.argv.append('--continue-on-error')
            
        return run_tests()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())