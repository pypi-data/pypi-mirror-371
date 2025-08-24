"""
Comprehensive test runner for the differential testing framework.

This module provides automated test execution, result collection,
and report generation for differential tests.
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import concurrent.futures
import logging

# Add project root to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Framework imports
from config.config_manager import ConfigManager, TestConfig
from sim.verilator import VerilatorRunner, VerilatorConfig, SimulationManager
from scripts.logger import setup_logging, LogConfig, get_logger, LogLevel
from scripts.report_generator import ReportGenerator


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Result of a test execution."""
    test_name: str
    config_name: str
    status: TestStatus
    start_time: float
    end_time: Optional[float] = None
    
    # Execution details
    compilation_time: float = 0.0
    simulation_time: float = 0.0
    total_time: float = 0.0
    
    # Test statistics
    total_vectors: int = 0
    passed_vectors: int = 0
    failed_vectors: int = 0
    
    # Output files
    log_file: Optional[str] = None
    wave_file: Optional[str] = None
    report_file: Optional[str] = None
    
    # Error information
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.end_time:
            self.total_time = self.end_time - self.start_time


@dataclass
class TestRunnerConfig:
    """Configuration for test runner."""
    # Execution options
    parallel_jobs: int = 1
    timeout_seconds: int = 600
    continue_on_error: bool = False
    
    # Output options
    work_dir: str = "test_work"
    reports_dir: str = "reports"
    logs_dir: str = "logs"
    
    # Tool options
    verilator_path: str = "verilator"
    make_path: str = "make"
    python_path: str = "python3"
    
    # Filtering options
    test_filter: Optional[str] = None
    config_filter: Optional[str] = None
    exclude_tests: List[str] = field(default_factory=list)
    
    # Reporting options
    generate_html_report: bool = True
    generate_json_report: bool = True
    generate_junit_xml: bool = False
    
    # Cleanup options
    cleanup_on_success: bool = False
    cleanup_on_failure: bool = False


class TestRunner:
    """
    Comprehensive test runner for differential testing framework.
    
    Manages test discovery, execution, and result collection with support
    for parallel execution and comprehensive reporting.
    """
    
    def __init__(self, config: TestRunnerConfig = None):
        """
        Initialize test runner.
        
        Args:
            config: Test runner configuration
        """
        self.config = config or TestRunnerConfig()
        
        # Setup directories
        self.work_dir = Path(self.config.work_dir)
        self.reports_dir = Path(self.config.reports_dir)
        self.logs_dir = Path(self.config.logs_dir)
        
        for directory in [self.work_dir, self.reports_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.logger = get_logger("TestRunner")
        
        # Test execution state
        self.discovered_tests = []
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
        # Statistics
        self.stats = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'error_tests': 0
        }
        
    def discover_tests(self, test_dirs: List[str] = None) -> List[Dict[str, Any]]:
        """
        Discover available tests.
        
        Args:
            test_dirs: Directories to search for tests
            
        Returns:
            List of discovered test information
        """
        if test_dirs is None:
            test_dirs = ["examples", "testbench/tests"]
            
        self.logger.info(f"Discovering tests in: {test_dirs}")
        
        discovered = []
        
        for test_dir in test_dirs:
            test_path = Path(test_dir)
            if not test_path.exists():
                self.logger.warning(f"Test directory not found: {test_path}")
                continue
                
            # Find test configurations
            for config_file in test_path.rglob("*.yaml"):
                if "config" in config_file.name.lower() or "test" in config_file.name.lower():
                    try:
                        test_config = self.config_manager.load_config(config_file)
                        
                        # Find corresponding testbench files
                        testbench_files = list(test_path.rglob("test_*.py"))
                        
                        test_info = {
                            'name': test_config.name,
                            'config_file': str(config_file),
                            'config': test_config,
                            'testbench_files': [str(f) for f in testbench_files],
                            'test_dir': str(test_path)
                        }
                        
                        # Apply filters
                        if self._should_include_test(test_info):
                            discovered.append(test_info)
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to load config {config_file}: {e}")
                        
        self.discovered_tests = discovered
        self.logger.info(f"Discovered {len(discovered)} tests")
        
        return discovered
        
    def _should_include_test(self, test_info: Dict[str, Any]) -> bool:
        """Check if test should be included based on filters."""
        test_name = test_info['name']
        
        # Check exclusions
        if test_name in self.config.exclude_tests:
            return False
            
        # Check test filter
        if self.config.test_filter:
            if self.config.test_filter.lower() not in test_name.lower():
                return False
                
        # Check config filter  
        if self.config.config_filter:
            if self.config.config_filter.lower() not in str(test_info['config_file']).lower():
                return False
                
        return True
        
    def run_all_tests(self) -> List[TestResult]:
        """
        Run all discovered tests.
        
        Returns:
            List of test results
        """
        if not self.discovered_tests:
            self.discover_tests()
            
        self.logger.info(f"Running {len(self.discovered_tests)} tests")
        self.start_time = time.time()
        
        # Execute tests
        if self.config.parallel_jobs > 1:
            results = self._run_tests_parallel()
        else:
            results = self._run_tests_sequential()
            
        self.end_time = time.time()
        self.test_results = results
        
        # Update statistics
        self._update_statistics()
        
        # Generate reports
        self._generate_reports()
        
        return results
        
    def _run_tests_sequential(self) -> List[TestResult]:
        """Run tests sequentially."""
        results = []
        
        for i, test_info in enumerate(self.discovered_tests):
            self.logger.info(f"Running test {i+1}/{len(self.discovered_tests)}: {test_info['name']}")
            
            try:
                result = self._run_single_test(test_info)
                results.append(result)
                
                if not self.config.continue_on_error and result.status == TestStatus.FAILED:
                    self.logger.error("Stopping execution due to test failure")
                    break
                    
            except Exception as e:
                self.logger.error(f"Error running test {test_info['name']}: {e}")
                
                error_result = TestResult(
                    test_name=test_info['name'],
                    config_name=str(test_info['config_file']),
                    status=TestStatus.ERROR,
                    start_time=time.time(),
                    end_time=time.time(),
                    error_message=str(e)
                )
                results.append(error_result)
                
                if not self.config.continue_on_error:
                    break
                    
        return results
        
    def _run_tests_parallel(self) -> List[TestResult]:
        """Run tests in parallel."""
        results = [None] * len(self.discovered_tests)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.parallel_jobs) as executor:
            # Submit all tests
            future_to_index = {}
            for i, test_info in enumerate(self.discovered_tests):
                future = executor.submit(self._run_single_test, test_info)
                future_to_index[future] = i
                
            # Collect results
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                test_info = self.discovered_tests[index]
                
                try:
                    result = future.result()
                    results[index] = result
                    
                    self.logger.info(f"Completed test {test_info['name']}: {result.status.value}")
                    
                except Exception as e:
                    self.logger.error(f"Error in test {test_info['name']}: {e}")
                    
                    error_result = TestResult(
                        test_name=test_info['name'],
                        config_name=str(test_info['config_file']),
                        status=TestStatus.ERROR,
                        start_time=time.time(),
                        end_time=time.time(),
                        error_message=str(e)
                    )
                    results[index] = error_result
                    
        # Filter out None results
        return [r for r in results if r is not None]
        
    def _run_single_test(self, test_info: Dict[str, Any]) -> TestResult:
        """Run a single test."""
        test_name = test_info['name']
        test_config = test_info['config']
        
        self.logger.info(f"Starting test: {test_name}")
        
        result = TestResult(
            test_name=test_name,
            config_name=str(test_info['config_file']),
            status=TestStatus.RUNNING,
            start_time=time.time()
        )
        
        # Create test-specific work directory
        test_work_dir = self.work_dir / f"test_{test_name}"
        test_work_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Setup logging for this test
            test_log_file = self.logs_dir / f"{test_name}.log"
            result.log_file = str(test_log_file)
            
            # Create Verilator configuration
            verilator_config = VerilatorConfig(
                top_module=test_config.top_module,
                verilog_sources=test_config.verilog_sources,
                testbench_module="",  # Using cocotb
                cocotb_module=f"test_{test_name.lower()}",
                compile_args=test_config.verilator.compile_args,
                sim_args=test_config.verilator.sim_args,
                work_dir=str(test_work_dir),
                enable_waves=test_config.verilator.enable_waves,
                wave_format=test_config.verilator.wave_format,
                debug_mode=test_config.verilator.debug_mode
            )
            
            # Run test using simulation manager
            with SimulationManager(f"TestRunner_{test_name}") as sim_manager:
                
                # Create and submit simulation job
                from sim.verilator.simulation_manager import SimulationJob
                
                job = SimulationJob(
                    job_id=f"test_{test_name}",
                    config=verilator_config,
                    test_module=f"test_{test_name.lower()}"
                )
                
                job_id = sim_manager.submit_job(job)
                sim_result = sim_manager.wait_for_job(job_id, timeout=self.config.timeout_seconds)
                
                if sim_result and sim_result.test_passed:
                    result.status = TestStatus.PASSED
                    result.compilation_time = sim_result.compilation_time
                    result.simulation_time = sim_result.simulation_time
                    
                    # Extract test statistics if available
                    if sim_result.metadata:
                        result.total_vectors = sim_result.metadata.get('total_vectors', 0)
                        result.passed_vectors = sim_result.metadata.get('passed_vectors', 0)
                        result.failed_vectors = sim_result.metadata.get('failed_vectors', 0)
                        
                else:
                    result.status = TestStatus.FAILED
                    if sim_result:
                        result.error_message = sim_result.error_message
                        result.error_details = sim_result.debug_data
                    else:
                        result.error_message = "Test timed out"
                        
            # Set wave file path if waves enabled
            if test_config.verilator.enable_waves:
                wave_file = test_work_dir / f"waves.{test_config.verilator.wave_format}"
                if wave_file.exists():
                    result.wave_file = str(wave_file)
                    
        except Exception as e:
            self.logger.error(f"Test {test_name} failed with exception: {e}")
            result.status = TestStatus.ERROR
            result.error_message = str(e)
            
        finally:
            result.end_time = time.time()
            
            # Cleanup if configured
            if (result.status == TestStatus.PASSED and self.config.cleanup_on_success) or \
               (result.status != TestStatus.PASSED and self.config.cleanup_on_failure):
                self._cleanup_test(test_work_dir)
                
        self.logger.info(f"Test {test_name} completed: {result.status.value} "
                        f"({result.total_time:.2f}s)")
        
        return result
        
    def _cleanup_test(self, test_work_dir: Path):
        """Clean up test artifacts."""
        try:
            import shutil
            if test_work_dir.exists():
                shutil.rmtree(test_work_dir)
                self.logger.debug(f"Cleaned up {test_work_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup {test_work_dir}: {e}")
            
    def _update_statistics(self):
        """Update test statistics."""
        self.stats = {
            'total_tests': len(self.test_results),
            'passed_tests': sum(1 for r in self.test_results if r.status == TestStatus.PASSED),
            'failed_tests': sum(1 for r in self.test_results if r.status == TestStatus.FAILED),
            'skipped_tests': sum(1 for r in self.test_results if r.status == TestStatus.SKIPPED),
            'error_tests': sum(1 for r in self.test_results if r.status == TestStatus.ERROR)
        }
        
    def _generate_reports(self):
        """Generate test reports."""
        if not self.test_results:
            return
            
        self.logger.info("Generating test reports")
        
        # Create report generator
        report_gen = ReportGenerator(
            test_results=self.test_results,
            output_dir=self.reports_dir,
            runner_stats=self.stats
        )
        
        # Generate reports based on configuration
        if self.config.generate_json_report:
            json_report = self.reports_dir / "test_results.json"
            report_gen.generate_json_report(str(json_report))
            
        if self.config.generate_html_report:
            html_report = self.reports_dir / "test_results.html"
            report_gen.generate_html_report(str(html_report))
            
        if self.config.generate_junit_xml:
            junit_report = self.reports_dir / "junit_results.xml"
            report_gen.generate_junit_xml(str(junit_report))
            
    def print_summary(self):
        """Print test execution summary."""
        if not self.test_results:
            self.logger.info("No tests executed")
            return
            
        total_time = self.end_time - self.start_time if (self.end_time and self.start_time) else 0
        
        print("\n" + "="*80)
        print("TEST EXECUTION SUMMARY")
        print("="*80)
        
        print(f"Total Tests:     {self.stats['total_tests']}")
        print(f"Passed:          {self.stats['passed_tests']}")
        print(f"Failed:          {self.stats['failed_tests']}")
        print(f"Skipped:         {self.stats['skipped_tests']}")
        print(f"Errors:          {self.stats['error_tests']}")
        
        if self.stats['total_tests'] > 0:
            pass_rate = (self.stats['passed_tests'] / self.stats['total_tests']) * 100
            print(f"Pass Rate:       {pass_rate:.1f}%")
            
        print(f"Total Time:      {total_time:.2f}s")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if r.status in [TestStatus.FAILED, TestStatus.ERROR]]
        if failed_tests:
            print("\nFAILED TESTS:")
            for result in failed_tests:
                print(f"  - {result.test_name}: {result.error_message or 'Unknown error'}")
                
        print("="*80)


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="BICSdifftest Test Runner")
    
    # Test selection
    parser.add_argument("--test-dirs", nargs="*", default=["examples"],
                       help="Directories to search for tests")
    parser.add_argument("--test-filter", help="Filter tests by name")
    parser.add_argument("--config-filter", help="Filter tests by config file")
    parser.add_argument("--exclude", nargs="*", default=[],
                       help="Tests to exclude")
    
    # Execution options
    parser.add_argument("--parallel", "-j", type=int, default=1,
                       help="Number of parallel jobs")
    parser.add_argument("--timeout", type=int, default=600,
                       help="Test timeout in seconds")
    parser.add_argument("--continue-on-error", action="store_true",
                       help="Continue execution after test failures")
    
    # Output options
    parser.add_argument("--work-dir", default="test_work",
                       help="Working directory for tests")
    parser.add_argument("--reports-dir", default="reports", 
                       help="Reports output directory")
    parser.add_argument("--logs-dir", default="logs",
                       help="Logs output directory")
    
    # Report options
    parser.add_argument("--no-html", action="store_true",
                       help="Disable HTML report generation")
    parser.add_argument("--no-json", action="store_true", 
                       help="Disable JSON report generation")
    parser.add_argument("--junit-xml", action="store_true",
                       help="Generate JUnit XML report")
    
    # Cleanup options
    parser.add_argument("--cleanup-success", action="store_true",
                       help="Clean up artifacts on test success")
    parser.add_argument("--cleanup-failure", action="store_true",
                       help="Clean up artifacts on test failure")
    
    # Logging
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level_map = {
        'DEBUG': LogLevel.DEBUG,
        'INFO': LogLevel.INFO,
        'WARNING': LogLevel.WARNING,
        'ERROR': LogLevel.ERROR,
        'CRITICAL': LogLevel.CRITICAL
    }
    
    log_config = LogConfig(
        level=log_level_map.get(args.log_level, LogLevel.INFO),
        console_output=True,
        file_output=True,
        log_dir=args.logs_dir,
        log_file="test_runner.log"
    )
    
    setup_logging(log_config)
    logger = get_logger("main")
    
    # Create runner configuration
    runner_config = TestRunnerConfig(
        parallel_jobs=args.parallel,
        timeout_seconds=args.timeout,
        continue_on_error=args.continue_on_error,
        work_dir=args.work_dir,
        reports_dir=args.reports_dir,
        logs_dir=args.logs_dir,
        test_filter=args.test_filter,
        config_filter=args.config_filter,
        exclude_tests=args.exclude,
        generate_html_report=not args.no_html,
        generate_json_report=not args.no_json,
        generate_junit_xml=args.junit_xml,
        cleanup_on_success=args.cleanup_success,
        cleanup_on_failure=args.cleanup_failure
    )
    
    # Create and run tests
    runner = TestRunner(runner_config)
    
    try:
        logger.info("Starting test discovery")
        runner.discover_tests(args.test_dirs)
        
        logger.info("Starting test execution")
        results = runner.run_all_tests()
        
        # Print summary
        runner.print_summary()
        
        # Exit with appropriate code
        failed_count = runner.stats['failed_tests'] + runner.stats['error_tests']
        sys.exit(0 if failed_count == 0 else 1)
        
    except KeyboardInterrupt:
        logger.warning("Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()