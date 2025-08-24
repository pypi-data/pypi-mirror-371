"""
Verification components for systematic testing and coverage collection.

This module provides reusable components for data driving, response checking,
and coverage collection in differential testing scenarios.
"""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb.queue import Queue

import random
import numpy as np
import torch
from typing import Dict, Any, Optional, List, Union, Callable, Iterator
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from abc import ABC, abstractmethod


class DataPatternType(Enum):
    """Types of data patterns for test generation."""
    RANDOM = "random"
    SEQUENTIAL = "sequential"
    CORNER_CASES = "corner_cases"
    CUSTOM = "custom"
    EXHAUSTIVE = "exhaustive"


@dataclass
class DataConstraints:
    """Constraints for data generation."""
    min_value: int = 0
    max_value: int = 2**32 - 1
    bit_width: int = 32
    signed: bool = False
    special_values: List[int] = field(default_factory=list)
    exclude_values: List[int] = field(default_factory=list)
    distribution: str = "uniform"  # uniform, gaussian, exponential


@dataclass
class TestCoveragePoint:
    """Coverage point definition."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    description: str = ""
    weight: float = 1.0
    hit_count: int = 0
    target_hits: int = 1


class DataDriver:
    """
    Data driver for systematic stimulus generation.
    
    This class generates test data according to specified patterns
    and constraints, suitable for differential testing scenarios.
    """
    
    def __init__(self, name: str, constraints: DataConstraints):
        """
        Initialize data driver.
        
        Args:
            name: Driver name
            constraints: Data generation constraints
        """
        self.name = name
        self.constraints = constraints
        self.logger = logging.getLogger(f"cocotb.{name}")
        self.seed = None
        
        # Pattern generators
        self.pattern_generators = {
            DataPatternType.RANDOM: self._random_pattern,
            DataPatternType.SEQUENTIAL: self._sequential_pattern,
            DataPatternType.CORNER_CASES: self._corner_case_pattern,
            DataPatternType.EXHAUSTIVE: self._exhaustive_pattern
        }
        
    def set_seed(self, seed: int):
        """Set random seed for reproducible generation."""
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        
    def generate_data(self, pattern_type: DataPatternType, 
                     count: int = 100) -> List[int]:
        """
        Generate test data according to pattern type.
        
        Args:
            pattern_type: Type of pattern to generate
            count: Number of values to generate
            
        Returns:
            List of generated values
        """
        if pattern_type in self.pattern_generators:
            generator = self.pattern_generators[pattern_type]
            data = list(generator(count))
        else:
            raise ValueError(f"Unknown pattern type: {pattern_type}")
            
        self.logger.info(f"Generated {len(data)} values using {pattern_type.value} pattern")
        return data
        
    def _random_pattern(self, count: int) -> Iterator[int]:
        """Generate random values within constraints."""
        for _ in range(count):
            if self.constraints.distribution == "uniform":
                value = random.randint(self.constraints.min_value, 
                                     self.constraints.max_value)
            elif self.constraints.distribution == "gaussian":
                mean = (self.constraints.min_value + self.constraints.max_value) // 2
                std = (self.constraints.max_value - self.constraints.min_value) // 6
                value = int(np.random.normal(mean, std))
                value = np.clip(value, self.constraints.min_value, 
                              self.constraints.max_value)
            else:
                value = random.randint(self.constraints.min_value,
                                     self.constraints.max_value)
                                     
            # Apply exclusions
            while value in self.constraints.exclude_values:
                value = random.randint(self.constraints.min_value,
                                     self.constraints.max_value)
                                     
            yield value
            
    def _sequential_pattern(self, count: int) -> Iterator[int]:
        """Generate sequential values."""
        start = self.constraints.min_value
        step = max(1, (self.constraints.max_value - self.constraints.min_value) // count)
        
        current = start
        for _ in range(count):
            if current > self.constraints.max_value:
                current = start
                
            if current not in self.constraints.exclude_values:
                yield current
                
            current += step
            
    def _corner_case_pattern(self, count: int) -> Iterator[int]:
        """Generate corner case values."""
        corner_cases = [
            self.constraints.min_value,
            self.constraints.max_value,
            0,
            -1 if self.constraints.signed else self.constraints.max_value,
            1,
            self.constraints.max_value // 2
        ]
        
        # Add bit pattern corner cases
        bit_patterns = [
            0xAAAA & ((1 << self.constraints.bit_width) - 1),  # Alternating
            0x5555 & ((1 << self.constraints.bit_width) - 1),  # Alternating inverse
            (1 << (self.constraints.bit_width - 1)),           # MSB only
            1,                                                 # LSB only
        ]
        corner_cases.extend(bit_patterns)
        
        # Add special values
        corner_cases.extend(self.constraints.special_values)
        
        # Filter valid values
        valid_corners = [
            v for v in corner_cases 
            if self.constraints.min_value <= v <= self.constraints.max_value
            and v not in self.constraints.exclude_values
        ]
        
        # Generate pattern
        generated = 0
        while generated < count:
            for value in valid_corners:
                if generated >= count:
                    break
                yield value
                generated += 1
                
            # Fill remaining with random if needed
            if generated < count:
                remaining = count - generated
                for value in self._random_pattern(remaining):
                    yield value
                    generated += 1
                break
                
    def _exhaustive_pattern(self, count: int) -> Iterator[int]:
        """Generate exhaustive values (limited by count)."""
        range_size = self.constraints.max_value - self.constraints.min_value + 1
        
        if range_size <= count:
            # Can generate all values
            for value in range(self.constraints.min_value, 
                             self.constraints.max_value + 1):
                if value not in self.constraints.exclude_values:
                    yield value
        else:
            # Sample from range
            step = range_size // count
            current = self.constraints.min_value
            
            for _ in range(count):
                if current not in self.constraints.exclude_values:
                    yield current
                current += step
                if current > self.constraints.max_value:
                    current = self.constraints.min_value
                    
    def generate_test_vectors(self, signal_names: List[str], 
                            pattern_type: DataPatternType,
                            count: int = 100) -> List[Dict[str, int]]:
        """
        Generate complete test vectors for multiple signals.
        
        Args:
            signal_names: Names of signals to generate data for
            pattern_type: Pattern type to use
            count: Number of test vectors to generate
            
        Returns:
            List of test vector dictionaries
        """
        vectors = []
        
        for i in range(count):
            vector = {}
            for signal_name in signal_names:
                # Generate independent data for each signal
                data_gen = self.pattern_generators[pattern_type](1)
                vector[signal_name] = next(data_gen)
                
            vectors.append(vector)
            
        return vectors


class ResponseChecker:
    """
    Response checker for validating DUT outputs.
    
    This class provides mechanisms to check DUT responses
    against expected values with configurable tolerance.
    """
    
    def __init__(self, name: str, tolerance_config: Dict[str, Any] = None):
        """
        Initialize response checker.
        
        Args:
            name: Checker name
            tolerance_config: Tolerance configuration
        """
        self.name = name
        self.logger = logging.getLogger(f"cocotb.{name}")
        
        # Default tolerance configuration
        self.tolerance_config = {
            'absolute_tolerance': 0,
            'relative_tolerance': 0.0,
            'bit_exact': True,
            'ignore_x_z': False
        }
        
        if tolerance_config:
            self.tolerance_config.update(tolerance_config)
            
        # Statistics
        self.check_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.error_history = []
        
    def check_value(self, signal_name: str, expected: int, actual: int, 
                   metadata: Dict[str, Any] = None) -> bool:
        """
        Check a single value against expected.
        
        Args:
            signal_name: Name of signal being checked
            expected: Expected value
            actual: Actual value from DUT
            metadata: Additional metadata for logging
            
        Returns:
            True if check passed, False otherwise
        """
        self.check_count += 1
        
        # Handle X/Z states if configured
        if self.tolerance_config['ignore_x_z']:
            # Convert X/Z to 0 for comparison
            try:
                actual_clean = int(str(actual).replace('x', '0').replace('z', '0'), 2)
            except:
                actual_clean = actual
        else:
            actual_clean = actual
            
        # Perform comparison based on tolerance settings
        if self.tolerance_config['bit_exact']:
            passed = (expected == actual_clean)
            error = abs(expected - actual_clean) if isinstance(actual_clean, int) else float('inf')
        else:
            # Use tolerance-based comparison
            abs_error = abs(expected - actual_clean)
            
            # Absolute tolerance check
            abs_ok = abs_error <= self.tolerance_config['absolute_tolerance']
            
            # Relative tolerance check
            if expected != 0:
                rel_error = abs_error / abs(expected)
                rel_ok = rel_error <= self.tolerance_config['relative_tolerance']
            else:
                rel_ok = abs_ok
                
            passed = abs_ok or rel_ok
            error = abs_error
            
        # Update statistics
        if passed:
            self.pass_count += 1
            self.logger.debug(f"PASS: {signal_name} = {actual} (expected {expected})")
        else:
            self.fail_count += 1
            self.logger.error(f"FAIL: {signal_name} = {actual} (expected {expected}, error = {error})")
            
            # Record error details
            error_record = {
                'signal': signal_name,
                'expected': expected,
                'actual': actual,
                'error': error,
                'timestamp': time.time(),
                'metadata': metadata or {}
            }
            self.error_history.append(error_record)
            
        return passed
        
    def check_multiple(self, expected_values: Dict[str, int], 
                      actual_values: Dict[str, int],
                      metadata: Dict[str, Any] = None) -> Dict[str, bool]:
        """
        Check multiple values simultaneously.
        
        Args:
            expected_values: Dictionary of expected values
            actual_values: Dictionary of actual values
            metadata: Additional metadata
            
        Returns:
            Dictionary of check results per signal
        """
        results = {}
        
        for signal_name, expected in expected_values.items():
            if signal_name in actual_values:
                actual = actual_values[signal_name]
                results[signal_name] = self.check_value(
                    signal_name, expected, actual, metadata
                )
            else:
                self.logger.error(f"Signal {signal_name} not found in actual values")
                results[signal_name] = False
                self.fail_count += 1
                
        return results
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get checker statistics."""
        pass_rate = (self.pass_count / self.check_count * 100) if self.check_count > 0 else 0
        
        return {
            'total_checks': self.check_count,
            'passed': self.pass_count,
            'failed': self.fail_count,
            'pass_rate': pass_rate,
            'recent_errors': self.error_history[-10:] if self.error_history else []
        }
        
    def reset_statistics(self):
        """Reset all statistics."""
        self.check_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.error_history.clear()


class CoverageCollector:
    """
    Coverage collector for tracking test coverage metrics.
    
    This class monitors test execution and collects coverage
    information to ensure comprehensive verification.
    """
    
    def __init__(self, name: str):
        """
        Initialize coverage collector.
        
        Args:
            name: Collector name
        """
        self.name = name
        self.logger = logging.getLogger(f"cocotb.{name}")
        
        # Coverage points
        self.coverage_points = {}
        
        # Coverage data
        self.total_samples = 0
        self.coverage_history = []
        
    def add_coverage_point(self, point: TestCoveragePoint):
        """Add a coverage point to monitor."""
        self.coverage_points[point.name] = point
        self.logger.info(f"Added coverage point: {point.name}")
        
    def sample_coverage(self, test_data: Dict[str, Any]):
        """
        Sample coverage points with current test data.
        
        Args:
            test_data: Current test inputs/outputs
        """
        self.total_samples += 1
        sample_hits = []
        
        for name, point in self.coverage_points.items():
            try:
                if point.condition(test_data):
                    point.hit_count += 1
                    sample_hits.append(name)
                    self.logger.debug(f"Coverage point hit: {name}")
            except Exception as e:
                self.logger.warning(f"Error evaluating coverage point {name}: {e}")
                
        # Record coverage state
        coverage_state = {
            'sample': self.total_samples,
            'hits': sample_hits,
            'timestamp': time.time()
        }
        self.coverage_history.append(coverage_state)
        
    def get_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive coverage report."""
        total_points = len(self.coverage_points)
        hit_points = sum(1 for point in self.coverage_points.values() 
                        if point.hit_count >= point.target_hits)
        
        coverage_percentage = (hit_points / total_points * 100) if total_points > 0 else 0
        
        point_details = {}
        for name, point in self.coverage_points.items():
            point_details[name] = {
                'description': point.description,
                'hit_count': point.hit_count,
                'target_hits': point.target_hits,
                'weight': point.weight,
                'achieved': point.hit_count >= point.target_hits,
                'hit_rate': (point.hit_count / self.total_samples * 100) if self.total_samples > 0 else 0
            }
            
        return {
            'overall_coverage': coverage_percentage,
            'total_points': total_points,
            'hit_points': hit_points,
            'total_samples': self.total_samples,
            'points': point_details,
            'weighted_coverage': self._calculate_weighted_coverage()
        }
        
    def _calculate_weighted_coverage(self) -> float:
        """Calculate weighted coverage based on point weights."""
        total_weight = sum(point.weight for point in self.coverage_points.values())
        if total_weight == 0:
            return 0.0
            
        achieved_weight = sum(
            point.weight for point in self.coverage_points.values()
            if point.hit_count >= point.target_hits
        )
        
        return (achieved_weight / total_weight) * 100
        
    def export_coverage_data(self, filename: str):
        """Export coverage data to file."""
        report = self.get_coverage_report()
        
        import json
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"Coverage data exported to {filename}")
        
    def create_standard_coverage_points(self, signal_names: List[str],
                                      bit_widths: Dict[str, int] = None) -> List[TestCoveragePoint]:
        """
        Create standard coverage points for given signals.
        
        Args:
            signal_names: Names of signals to create coverage for
            bit_widths: Bit widths for each signal
            
        Returns:
            List of created coverage points
        """
        points = []
        bit_widths = bit_widths or {}
        
        for signal_name in signal_names:
            width = bit_widths.get(signal_name, 32)
            max_val = (1 << width) - 1
            
            # Corner value coverage points
            corner_points = [
                (f"{signal_name}_zero", lambda data, s=signal_name: data.get(s, 0) == 0),
                (f"{signal_name}_max", lambda data, s=signal_name, m=max_val: data.get(s, 0) == m),
                (f"{signal_name}_mid", lambda data, s=signal_name, m=max_val: data.get(s, 0) == m//2),
                (f"{signal_name}_msb", lambda data, s=signal_name, w=width: data.get(s, 0) & (1 << (w-1)) != 0),
                (f"{signal_name}_lsb", lambda data, s=signal_name: data.get(s, 0) & 1 != 0),
            ]
            
            for name, condition in corner_points:
                point = TestCoveragePoint(
                    name=name,
                    condition=condition,
                    description=f"Coverage for {signal_name} corner case"
                )
                points.append(point)
                
        return points