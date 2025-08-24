"""
Utility classes for golden model operations and data comparison.

This module provides helper classes for data formatting, tensor comparison,
and other common operations needed in differential testing.
"""

import torch
import numpy as np
from typing import Dict, Any, Optional, Union, Tuple, List
import logging
from dataclasses import dataclass
from enum import Enum
import math


class ComparisonMode(Enum):
    """Comparison modes for tensor/data comparison."""
    EXACT = "exact"
    ABSOLUTE_TOLERANCE = "abs_tol"
    RELATIVE_TOLERANCE = "rel_tol"
    ULP_TOLERANCE = "ulp_tol"
    BIT_ACCURATE = "bit_accurate"


@dataclass
class ComparisonResult:
    """Result of a data comparison operation."""
    passed: bool
    mode: ComparisonMode
    max_error: float
    mean_error: float
    mismatch_count: int
    total_elements: int
    error_details: Optional[Dict[str, Any]] = None


class TensorComparator:
    """
    Advanced tensor comparison utilities for hardware verification.
    
    Provides multiple comparison modes suitable for different types of
    hardware verification scenarios.
    """
    
    def __init__(self, default_mode: ComparisonMode = ComparisonMode.ABSOLUTE_TOLERANCE,
                 default_tolerance: float = 1e-6):
        """
        Initialize tensor comparator.
        
        Args:
            default_mode: Default comparison mode
            default_tolerance: Default tolerance value
        """
        self.default_mode = default_mode
        self.default_tolerance = default_tolerance
        self.logger = logging.getLogger(__name__)
    
    def compare(self, golden: Union[torch.Tensor, np.ndarray], 
                hardware: Union[torch.Tensor, np.ndarray, int, float],
                mode: Optional[ComparisonMode] = None,
                tolerance: Optional[float] = None,
                name: str = "comparison") -> ComparisonResult:
        """
        Compare golden model output with hardware output.
        
        Args:
            golden: Golden model output
            hardware: Hardware output
            mode: Comparison mode to use
            tolerance: Tolerance value for comparison
            name: Name for logging purposes
            
        Returns:
            ComparisonResult with detailed comparison information
        """
        mode = mode or self.default_mode
        tolerance = tolerance or self.default_tolerance
        
        # Convert inputs to consistent format
        golden_tensor = self._to_tensor(golden)
        hardware_tensor = self._to_tensor(hardware)
        
        # Ensure same shape
        if golden_tensor.shape != hardware_tensor.shape:
            self.logger.error(f"{name}: Shape mismatch - Golden: {golden_tensor.shape}, "
                            f"Hardware: {hardware_tensor.shape}")
            return ComparisonResult(
                passed=False,
                mode=mode,
                max_error=float('inf'),
                mean_error=float('inf'),
                mismatch_count=-1,
                total_elements=golden_tensor.numel(),
                error_details={'error': 'Shape mismatch'}
            )
        
        # Perform comparison based on mode
        if mode == ComparisonMode.EXACT:
            result = self._exact_comparison(golden_tensor, hardware_tensor)
        elif mode == ComparisonMode.ABSOLUTE_TOLERANCE:
            result = self._absolute_tolerance_comparison(golden_tensor, hardware_tensor, tolerance)
        elif mode == ComparisonMode.RELATIVE_TOLERANCE:
            result = self._relative_tolerance_comparison(golden_tensor, hardware_tensor, tolerance)
        elif mode == ComparisonMode.ULP_TOLERANCE:
            result = self._ulp_tolerance_comparison(golden_tensor, hardware_tensor, tolerance)
        elif mode == ComparisonMode.BIT_ACCURATE:
            result = self._bit_accurate_comparison(golden_tensor, hardware_tensor)
        else:
            raise ValueError(f"Unknown comparison mode: {mode}")
        
        # Log result
        if result.passed:
            self.logger.debug(f"{name}: PASS - {mode.value} (max_error: {result.max_error:.2e})")
        else:
            self.logger.error(f"{name}: FAIL - {mode.value} (max_error: {result.max_error:.2e}, "
                            f"mismatches: {result.mismatch_count}/{result.total_elements})")
        
        return result
    
    def _to_tensor(self, data: Union[torch.Tensor, np.ndarray, int, float]) -> torch.Tensor:
        """Convert input data to PyTorch tensor."""
        if isinstance(data, torch.Tensor):
            return data.detach().cpu()
        elif isinstance(data, np.ndarray):
            return torch.from_numpy(data)
        elif isinstance(data, (int, float)):
            return torch.tensor(data)
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
    
    def _exact_comparison(self, golden: torch.Tensor, hardware: torch.Tensor) -> ComparisonResult:
        """Exact equality comparison."""
        matches = torch.eq(golden, hardware)
        mismatch_count = (~matches).sum().item()
        
        if mismatch_count == 0:
            max_error = 0.0
            mean_error = 0.0
        else:
            diff = torch.abs(golden - hardware)
            max_error = diff.max().item()
            mean_error = diff.mean().item()
        
        return ComparisonResult(
            passed=(mismatch_count == 0),
            mode=ComparisonMode.EXACT,
            max_error=max_error,
            mean_error=mean_error,
            mismatch_count=mismatch_count,
            total_elements=golden.numel()
        )
    
    def _absolute_tolerance_comparison(self, golden: torch.Tensor, hardware: torch.Tensor, 
                                     tolerance: float) -> ComparisonResult:
        """Absolute tolerance comparison."""
        diff = torch.abs(golden - hardware)
        matches = diff <= tolerance
        mismatch_count = (~matches).sum().item()
        
        max_error = diff.max().item()
        mean_error = diff.mean().item()
        
        return ComparisonResult(
            passed=(mismatch_count == 0),
            mode=ComparisonMode.ABSOLUTE_TOLERANCE,
            max_error=max_error,
            mean_error=mean_error,
            mismatch_count=mismatch_count,
            total_elements=golden.numel()
        )
    
    def _relative_tolerance_comparison(self, golden: torch.Tensor, hardware: torch.Tensor,
                                     tolerance: float) -> ComparisonResult:
        """Relative tolerance comparison."""
        # Avoid division by zero
        golden_abs = torch.abs(golden)
        relative_diff = torch.abs(golden - hardware) / torch.clamp(golden_abs, min=1e-10)
        
        matches = relative_diff <= tolerance
        mismatch_count = (~matches).sum().item()
        
        max_error = relative_diff.max().item()
        mean_error = relative_diff.mean().item()
        
        return ComparisonResult(
            passed=(mismatch_count == 0),
            mode=ComparisonMode.RELATIVE_TOLERANCE,
            max_error=max_error,
            mean_error=mean_error,
            mismatch_count=mismatch_count,
            total_elements=golden.numel()
        )
    
    def _ulp_tolerance_comparison(self, golden: torch.Tensor, hardware: torch.Tensor,
                                ulp_tolerance: float) -> ComparisonResult:
        """ULP (Units in the Last Place) tolerance comparison."""
        # Convert to numpy for ULP calculation
        golden_np = golden.numpy()
        hardware_np = hardware.numpy()
        
        # Calculate ULP difference
        ulp_diff = np.abs(golden_np - hardware_np) / np.finfo(golden_np.dtype).eps
        
        matches = ulp_diff <= ulp_tolerance
        mismatch_count = (~matches).sum()
        
        max_error = ulp_diff.max()
        mean_error = ulp_diff.mean()
        
        return ComparisonResult(
            passed=(mismatch_count == 0),
            mode=ComparisonMode.ULP_TOLERANCE,
            max_error=float(max_error),
            mean_error=float(mean_error),
            mismatch_count=int(mismatch_count),
            total_elements=golden.numel()
        )
    
    def _bit_accurate_comparison(self, golden: torch.Tensor, hardware: torch.Tensor) -> ComparisonResult:
        """Bit-accurate comparison for integer types."""
        if golden.dtype.is_floating_point or hardware.dtype.is_floating_point:
            self.logger.warning("Bit-accurate comparison requested for non-integer types")
        
        # Convert to same integer type for comparison
        golden_int = golden.to(torch.int64)
        hardware_int = hardware.to(torch.int64)
        
        matches = torch.eq(golden_int, hardware_int)
        mismatch_count = (~matches).sum().item()
        
        if mismatch_count == 0:
            max_error = 0.0
            mean_error = 0.0
        else:
            diff = torch.abs(golden_int - hardware_int).float()
            max_error = diff.max().item()
            mean_error = diff.mean().item()
        
        return ComparisonResult(
            passed=(mismatch_count == 0),
            mode=ComparisonMode.BIT_ACCURATE,
            max_error=max_error,
            mean_error=mean_error,
            mismatch_count=mismatch_count,
            total_elements=golden.numel()
        )


class DataFormatter:
    """
    Data formatting utilities for hardware verification.
    
    Provides methods to format data for hardware simulation input and
    parse hardware simulation output.
    """
    
    @staticmethod
    def tensor_to_hex_string(tensor: torch.Tensor, width: int = 32) -> List[str]:
        """
        Convert tensor to hexadecimal string representation.
        
        Args:
            tensor: Input tensor
            width: Bit width for each element
            
        Returns:
            List of hexadecimal strings
        """
        # Convert to appropriate integer type
        if width <= 8:
            int_tensor = tensor.to(torch.uint8)
        elif width <= 16:
            int_tensor = tensor.to(torch.int16)
        elif width <= 32:
            int_tensor = tensor.to(torch.int32)
        else:
            int_tensor = tensor.to(torch.int64)
        
        # Convert to hex strings
        hex_strings = []
        for value in int_tensor.flatten():
            hex_str = f"{value.item():0{width//4}x}"
            hex_strings.append(hex_str)
        
        return hex_strings
    
    @staticmethod
    def hex_string_to_tensor(hex_strings: List[str], shape: Tuple[int, ...], 
                           dtype: torch.dtype = torch.int32) -> torch.Tensor:
        """
        Convert hexadecimal strings back to tensor.
        
        Args:
            hex_strings: List of hex strings
            shape: Desired tensor shape
            dtype: Target data type
            
        Returns:
            Reconstructed tensor
        """
        values = [int(hex_str, 16) for hex_str in hex_strings]
        tensor = torch.tensor(values, dtype=dtype)
        return tensor.reshape(shape)
    
    @staticmethod
    def tensor_to_binary_string(tensor: torch.Tensor, width: int = 32) -> List[str]:
        """
        Convert tensor to binary string representation.
        
        Args:
            tensor: Input tensor
            width: Bit width for each element
            
        Returns:
            List of binary strings
        """
        # Convert to appropriate integer type
        int_tensor = tensor.to(torch.int64)
        
        # Convert to binary strings
        binary_strings = []
        for value in int_tensor.flatten():
            # Handle negative numbers using two's complement
            if value.item() < 0:
                value_uint = (1 << width) + value.item()
            else:
                value_uint = value.item()
            
            binary_str = f"{value_uint:0{width}b}"
            binary_strings.append(binary_str)
        
        return binary_strings
    
    @staticmethod
    def create_test_vectors(tensor: torch.Tensor, format_type: str = "hex") -> Dict[str, Any]:
        """
        Create test vectors suitable for hardware simulation.
        
        Args:
            tensor: Input tensor
            format_type: Format type ("hex", "binary", "decimal")
            
        Returns:
            Dictionary with formatted test vectors and metadata
        """
        if format_type == "hex":
            vectors = DataFormatter.tensor_to_hex_string(tensor)
        elif format_type == "binary":
            vectors = DataFormatter.tensor_to_binary_string(tensor)
        elif format_type == "decimal":
            vectors = [str(x.item()) for x in tensor.flatten()]
        else:
            raise ValueError(f"Unknown format type: {format_type}")
        
        return {
            'vectors': vectors,
            'shape': list(tensor.shape),
            'dtype': str(tensor.dtype),
            'format': format_type,
            'element_count': tensor.numel()
        }


class DebugHelper:
    """
    Debugging utilities for differential testing.
    
    Provides methods to analyze mismatches and generate debug reports.
    """
    
    @staticmethod
    def analyze_mismatch(golden: torch.Tensor, hardware: torch.Tensor, 
                        threshold: float = 1e-6) -> Dict[str, Any]:
        """
        Analyze mismatches between golden and hardware outputs.
        
        Args:
            golden: Golden model output
            hardware: Hardware output
            threshold: Threshold for considering values as mismatched
            
        Returns:
            Dictionary with mismatch analysis
        """
        diff = torch.abs(golden - hardware)
        mismatches = diff > threshold
        
        analysis = {
            'total_elements': golden.numel(),
            'mismatch_count': mismatches.sum().item(),
            'mismatch_percentage': (mismatches.sum().item() / golden.numel()) * 100,
            'max_error': diff.max().item(),
            'mean_error': diff.mean().item(),
            'std_error': diff.std().item(),
            'mismatch_indices': torch.nonzero(mismatches).tolist()
        }
        
        # Add histogram of errors
        if analysis['mismatch_count'] > 0:
            mismatch_errors = diff[mismatches]
            analysis['error_histogram'] = {
                'bins': 10,
                'values': torch.histc(mismatch_errors, bins=10).tolist()
            }
        
        return analysis
    
    @staticmethod
    def generate_debug_report(comparisons: List[Tuple[str, ComparisonResult]], 
                            output_path: str) -> None:
        """
        Generate a comprehensive debug report.
        
        Args:
            comparisons: List of (name, ComparisonResult) tuples
            output_path: Path to save the report
        """
        report = {
            'summary': {
                'total_comparisons': len(comparisons),
                'passed': sum(1 for _, result in comparisons if result.passed),
                'failed': sum(1 for _, result in comparisons if not result.passed)
            },
            'comparisons': []
        }
        
        for name, result in comparisons:
            comparison_data = {
                'name': name,
                'passed': result.passed,
                'mode': result.mode.value,
                'max_error': result.max_error,
                'mean_error': result.mean_error,
                'mismatch_count': result.mismatch_count,
                'total_elements': result.total_elements,
                'mismatch_percentage': (result.mismatch_count / result.total_elements) * 100
            }
            
            if result.error_details:
                comparison_data['error_details'] = result.error_details
            
            report['comparisons'].append(comparison_data)
        
        # Write report
        import json
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)