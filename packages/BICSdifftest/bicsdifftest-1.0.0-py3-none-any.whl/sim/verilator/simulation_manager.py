"""
Simulation manager for coordinating Verilator simulations with golden models.

This module provides high-level management of simulation runs, result collection,
and integration with the differential testing framework.
"""

import os
import time
import json
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import concurrent.futures
from abc import ABC, abstractmethod

# Framework imports
from .verilator_runner import VerilatorRunner, VerilatorConfig
from .build_system import VerilatorBuildSystem, BuildConfig


class SimulationState(Enum):
    """Simulation execution states."""
    PENDING = "pending"
    COMPILING = "compiling"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class SimulationResult:
    """Result of a simulation run."""
    simulation_id: str
    state: SimulationState
    start_time: float
    end_time: Optional[float] = None
    return_code: Optional[int] = None
    stdout_log: str = ""
    stderr_log: str = ""
    
    # Differential testing results
    golden_model_results: Optional[Dict[str, Any]] = None
    comparison_results: Optional[Dict[str, Any]] = None
    test_passed: bool = False
    
    # Performance metrics
    compilation_time: float = 0.0
    simulation_time: float = 0.0
    memory_usage: Optional[float] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_time(self) -> float:
        """Get total execution time."""
        if self.end_time:
            return self.end_time - self.start_time
        return 0.0
        
    @property
    def is_complete(self) -> bool:
        """Check if simulation is complete."""
        return self.state in [SimulationState.COMPLETED, SimulationState.FAILED, 
                            SimulationState.TIMEOUT, SimulationState.CANCELLED]


class SimulationJob:
    """Represents a simulation job with configuration and callbacks."""
    
    def __init__(self, job_id: str, config: VerilatorConfig, 
                 test_module: str = None, callbacks: Dict[str, Callable] = None):
        """
        Initialize simulation job.
        
        Args:
            job_id: Unique job identifier
            config: Verilator configuration
            test_module: Cocotb test module to run
            callbacks: Callback functions for different events
        """
        self.job_id = job_id
        self.config = config
        self.test_module = test_module
        self.callbacks = callbacks or {}
        
        # Job state
        self.result = SimulationResult(
            simulation_id=job_id,
            state=SimulationState.PENDING,
            start_time=time.time()
        )
        
        self.runner = None
        self.logger = logging.getLogger(f"SimJob.{job_id}")
        
    def execute(self) -> SimulationResult:
        """Execute the simulation job."""
        try:
            self.result.start_time = time.time()
            self._call_callback('on_start')
            
            # Create runner
            self.runner = VerilatorRunner(self.config)
            
            # Compilation phase
            self.result.state = SimulationState.COMPILING
            self._call_callback('on_compile_start')
            
            compile_start = time.time()
            if not self.runner.compile():
                self.result.state = SimulationState.FAILED
                self.result.end_time = time.time()
                self._call_callback('on_compile_failed')
                return self.result
                
            self.result.compilation_time = time.time() - compile_start
            self._call_callback('on_compile_complete')
            
            # Simulation phase
            self.result.state = SimulationState.RUNNING
            self._call_callback('on_sim_start')
            
            sim_start = time.time()
            if self.test_module:
                success = self.runner.run_cocotb_test(self.test_module)
            else:
                success = self.runner.run_simulation(self.job_id)
                
            self.result.simulation_time = time.time() - sim_start
            
            if success:
                self.result.state = SimulationState.COMPLETED
                self.result.test_passed = True
                self._call_callback('on_sim_complete')
            else:
                self.result.state = SimulationState.FAILED
                self._call_callback('on_sim_failed')
                
        except Exception as e:
            self.logger.error(f"Job execution failed: {e}")
            self.result.state = SimulationState.FAILED
            self.result.metadata['error'] = str(e)
            self._call_callback('on_error', error=e)
            
        finally:
            self.result.end_time = time.time()
            self._call_callback('on_complete')
            
        return self.result
        
    def _call_callback(self, event: str, **kwargs):
        """Call callback if registered."""
        if event in self.callbacks:
            try:
                self.callbacks[event](self, **kwargs)
            except Exception as e:
                self.logger.warning(f"Callback {event} failed: {e}")


class SimulationManager:
    """
    Manager for coordinating multiple simulation runs.
    
    Provides job scheduling, result collection, and integration
    with the differential testing framework.
    """
    
    def __init__(self, name: str = "SimulationManager", max_workers: int = None):
        """
        Initialize simulation manager.
        
        Args:
            name: Manager name for logging
            max_workers: Maximum parallel workers
        """
        self.name = name
        self.logger = logging.getLogger(f"SimMgr.{name}")
        
        # Worker pool
        self.max_workers = max_workers or min(4, (os.cpu_count() or 1) + 4)
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix=f"SimWorker-{name}"
        )
        
        # Job management
        self.jobs = {}
        self.results = {}
        self.job_queue = []
        
        # Statistics
        self.stats = {
            'jobs_submitted': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'total_compile_time': 0.0,
            'total_simulation_time': 0.0
        }
        
        # Configuration
        self.config = {
            'auto_cleanup': True,
            'result_retention': 100,  # Keep last N results
            'log_level': 'INFO'
        }
        
    def submit_job(self, job: SimulationJob) -> str:
        """
        Submit a simulation job for execution.
        
        Args:
            job: Simulation job to submit
            
        Returns:
            Job ID
        """
        self.jobs[job.job_id] = job
        self.stats['jobs_submitted'] += 1
        
        # Submit to executor
        future = self.executor.submit(job.execute)
        future.add_done_callback(lambda f: self._job_completed(job.job_id, f))
        
        self.logger.info(f"Submitted job: {job.job_id}")
        return job.job_id
        
    def _job_completed(self, job_id: str, future: concurrent.futures.Future):
        """Handle job completion."""
        try:
            result = future.result()
            self.results[job_id] = result
            
            # Update statistics
            if result.state == SimulationState.COMPLETED:
                self.stats['jobs_completed'] += 1
            else:
                self.stats['jobs_failed'] += 1
                
            self.stats['total_compile_time'] += result.compilation_time
            self.stats['total_simulation_time'] += result.simulation_time
            
            self.logger.info(f"Job completed: {job_id} ({result.state.value})")
            
            # Cleanup if configured
            if self.config['auto_cleanup']:
                self._cleanup_job(job_id)
                
        except Exception as e:
            self.logger.error(f"Job {job_id} completed with exception: {e}")
            
    def _cleanup_job(self, job_id: str):
        """Clean up job resources."""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            if job.runner:
                # Clean up build artifacts for completed jobs
                try:
                    job.runner.clean()
                except Exception as e:
                    self.logger.warning(f"Cleanup failed for {job_id}: {e}")
                    
    def get_job_status(self, job_id: str) -> Optional[SimulationState]:
        """Get status of a job."""
        if job_id in self.jobs:
            return self.jobs[job_id].result.state
        elif job_id in self.results:
            return self.results[job_id].state
        return None
        
    def get_job_result(self, job_id: str) -> Optional[SimulationResult]:
        """Get result of a job."""
        return self.results.get(job_id)
        
    def wait_for_job(self, job_id: str, timeout: float = None) -> Optional[SimulationResult]:
        """
        Wait for a job to complete.
        
        Args:
            job_id: Job ID to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            SimulationResult if completed, None if timeout
        """
        start_time = time.time()
        
        while True:
            if job_id in self.results:
                return self.results[job_id]
                
            if timeout and (time.time() - start_time) > timeout:
                return None
                
            time.sleep(0.1)
            
    def wait_for_all(self, timeout: float = None) -> Dict[str, SimulationResult]:
        """
        Wait for all submitted jobs to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Dictionary of job results
        """
        start_time = time.time()
        
        while len(self.results) < len(self.jobs):
            if timeout and (time.time() - start_time) > timeout:
                break
            time.sleep(0.1)
            
        return self.results.copy()
        
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running job.
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            True if cancelled, False if not found or already complete
        """
        if job_id in self.jobs:
            job = self.jobs[job_id]
            if not job.result.is_complete:
                job.result.state = SimulationState.CANCELLED
                job.result.end_time = time.time()
                self.logger.info(f"Cancelled job: {job_id}")
                return True
                
        return False
        
    def run_differential_test(self, 
                            verilog_sources: List[str],
                            golden_model: Any,
                            test_vectors: List[Dict[str, Any]],
                            top_module: str,
                            test_name: str = "difftest") -> List[SimulationResult]:
        """
        Run differential test comparing hardware against golden model.
        
        Args:
            verilog_sources: List of Verilog source files
            golden_model: Golden model instance
            test_vectors: List of test input vectors
            top_module: Name of top-level module
            test_name: Name for the test
            
        Returns:
            List of simulation results
        """
        self.logger.info(f"Running differential test: {test_name}")
        
        results = []
        
        for i, test_vector in enumerate(test_vectors):
            job_id = f"{test_name}_vector_{i}"
            
            # Create Verilator configuration
            config = VerilatorConfig(
                top_module=top_module,
                verilog_sources=verilog_sources,
                testbench_module="",  # Will use cocotb
                cocotb_module=f"testbench.tests.{test_name}",
                work_dir=f"sim_work/{job_id}",
                enable_waves=True
            )
            
            # Create job with differential testing callbacks
            callbacks = {
                'on_sim_complete': lambda job: self._run_golden_model_comparison(
                    job, golden_model, test_vector
                )
            }
            
            job = SimulationJob(job_id, config, callbacks=callbacks)
            job.result.metadata['test_vector'] = test_vector
            
            # Submit job
            self.submit_job(job)
            
        # Wait for all jobs to complete
        all_results = self.wait_for_all(timeout=600)  # 10 minute timeout
        
        # Collect results for this test
        for i in range(len(test_vectors)):
            job_id = f"{test_name}_vector_{i}"
            if job_id in all_results:
                results.append(all_results[job_id])
                
        return results
        
    def _run_golden_model_comparison(self, job: SimulationJob, 
                                   golden_model: Any, test_vector: Dict[str, Any]):
        """Run golden model and compare with hardware results."""
        try:
            # Run golden model
            golden_output = golden_model(test_vector)
            job.result.golden_model_results = {
                'output': golden_output.tolist() if hasattr(golden_output, 'tolist') else golden_output,
                'checkpoints': golden_model.get_all_checkpoints()
            }
            
            # TODO: Add hardware result extraction and comparison
            # This would need to be integrated with the specific testbench
            
        except Exception as e:
            self.logger.error(f"Golden model comparison failed for {job.job_id}: {e}")
            job.result.metadata['golden_model_error'] = str(e)
            
    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive test report.
        
        Args:
            output_file: Optional file to save report
            
        Returns:
            Report data
        """
        report = {
            'manager_name': self.name,
            'timestamp': time.time(),
            'statistics': self.stats.copy(),
            'configuration': self.config.copy(),
            'jobs': {},
            'summary': {}
        }
        
        # Add job details
        for job_id, result in self.results.items():
            report['jobs'][job_id] = {
                'state': result.state.value,
                'test_passed': result.test_passed,
                'total_time': result.total_time,
                'compilation_time': result.compilation_time,
                'simulation_time': result.simulation_time,
                'metadata': result.metadata
            }
            
        # Calculate summary
        total_jobs = len(self.results)
        passed_jobs = sum(1 for r in self.results.values() if r.test_passed)
        
        report['summary'] = {
            'total_jobs': total_jobs,
            'passed_jobs': passed_jobs,
            'failed_jobs': total_jobs - passed_jobs,
            'pass_rate': (passed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            'average_compile_time': (self.stats['total_compile_time'] / total_jobs) if total_jobs > 0 else 0,
            'average_simulation_time': (self.stats['total_simulation_time'] / total_jobs) if total_jobs > 0 else 0
        }
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"Report saved to {output_file}")
            
        return report
        
    def cleanup(self):
        """Clean up manager resources."""
        self.logger.info("Cleaning up simulation manager")
        
        # Cancel any pending jobs
        for job_id, job in self.jobs.items():
            if not job.result.is_complete:
                self.cancel_job(job_id)
                
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Clear data
        self.jobs.clear()
        self.results.clear()
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()