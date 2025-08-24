"""
FPU Golden Model for differential testing.

This module provides the PyTorch-based golden model for the FPU design.
The FPU in this example implements a simple max operation between two 32-bit inputs.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Union
import logging
import struct

from ..base.golden_model_base import GoldenModelBase


class FPUGoldenModel(GoldenModelBase):
    """
    Golden model for the FPU design.
    
    This FPU performs a simple max operation: result = max(a, b)
    where a and b are 32-bit unsigned integers.
    """
    
    def __init__(self, data_width: int = 32):
        """
        Initialize FPU Golden Model.
        
        Args:
            data_width: Data width in bits (default: 32)
        """
        super().__init__()
        self.data_width = data_width
        self.max_value = (1 << data_width) - 1
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Initialized FPU Golden Model with {data_width}-bit data width")
    
    def _forward_impl(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forward pass implementation of the FPU golden model.
        
        Args:
            inputs: Dictionary containing 'a' and 'b' values
            
        Returns:
            Dictionary with 'result' key containing the maximum value
        """
        self.checkpoint_manager.clear_checkpoints()
        
        # Extract inputs
        a = inputs.get('a', 0)
        b = inputs.get('b', 0)
        
        # Save input checkpoint
        self.checkpoint_manager.save_checkpoint('inputs', {
            'a': torch.tensor(a, dtype=torch.int64),
            'b': torch.tensor(b, dtype=torch.int64)
        })
        
        # Ensure inputs are within valid range
        a = self._clamp_to_range(a)
        b = self._clamp_to_range(b)
        
        # Save clamped inputs
        self.checkpoint_manager.save_checkpoint('clamped_inputs', {
            'a': torch.tensor(a, dtype=torch.int64),
            'b': torch.tensor(b, dtype=torch.int64)
        })
        
        # Perform max operation
        result = max(a, b)
        
        # Save intermediate computation
        self.checkpoint_manager.save_checkpoint('comparison', {
            'a_greater': torch.tensor(a > b, dtype=torch.bool),
            'selected_value': torch.tensor(result, dtype=torch.int64)
        })
        
        # Final result
        result_tensor = torch.tensor(result, dtype=torch.int64)
        
        # Save final outputs
        outputs = {'result': result_tensor}
        self.checkpoint_manager.save_checkpoint('final_outputs', outputs)
        
        self.logger.debug(f"FPU computation: max({a}, {b}) = {result}")
        
        return outputs
    
    def _clamp_to_range(self, value: int) -> int:
        """Clamp value to valid range for the data width."""
        return max(0, min(self.max_value, value))
    
    def reset(self) -> None:
        """Reset the golden model to initial state."""
        self.checkpoint_manager.clear_checkpoints()
        self.logger.debug("FPU Golden Model reset")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model configuration."""
        return {
            'model_type': 'FPU',
            'operation': 'max',
            'data_width': self.data_width,
            'max_value': self.max_value
        }


class FPUTestVectorGenerator:
    """Generate test vectors for FPU differential testing."""
    
    def __init__(self, data_width: int = 32):
        """
        Initialize test vector generator.
        
        Args:
            data_width: Data width in bits
        """
        self.data_width = data_width
        self.max_value = (1 << data_width) - 1
        self.logger = logging.getLogger(__name__)
        
    def generate_random_vectors(self, count: int = 10, seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate random test vectors.
        
        Args:
            count: Number of test vectors to generate
            seed: Random seed for reproducibility
            
        Returns:
            List of test vector dictionaries
        """
        if seed is not None:
            np.random.seed(seed)
            torch.manual_seed(seed)
        
        vectors = []
        for i in range(count):
            a = np.random.randint(0, self.max_value + 1, dtype=np.uint32)
            b = np.random.randint(0, self.max_value + 1, dtype=np.uint32)
            
            vectors.append({
                'a': int(a),
                'b': int(b),
                'test_type': 'random',
                'test_id': f'random_{i}'
            })
        
        self.logger.info(f"Generated {count} random test vectors")
        return vectors
    
    def generate_corner_case_vectors(self) -> List[Dict[str, Any]]:
        """
        Generate corner case test vectors.
        
        Returns:
            List of corner case test vectors
        """
        vectors = []
        
        # Corner cases for max operation
        corner_cases = [
            # Both zero
            (0, 0, 'both_zero'),
            # One zero, one non-zero
            (0, 1, 'zero_vs_one'),
            (1, 0, 'one_vs_zero'),
            # Maximum value cases
            (self.max_value, 0, 'max_vs_zero'),
            (0, self.max_value, 'zero_vs_max'),
            (self.max_value, self.max_value, 'both_max'),
            # Equal non-zero values
            (100, 100, 'equal_values'),
            (self.max_value // 2, self.max_value // 2, 'equal_mid'),
            # Adjacent values
            (100, 101, 'adjacent_low_high'),
            (101, 100, 'adjacent_high_low'),
            # Powers of 2
            (1024, 2048, 'power_of_2'),
            (2048, 1024, 'power_of_2_reverse')
        ]
        
        for i, (a, b, case_name) in enumerate(corner_cases):
            vectors.append({
                'a': int(a),
                'b': int(b),
                'test_type': 'corner_case',
                'test_id': f'corner_{case_name}_{i}'
            })
        
        self.logger.info(f"Generated {len(vectors)} corner case test vectors")
        return vectors
    
    def generate_simple_test_pair(self) -> Dict[str, Any]:
        """
        Generate a simple test pair for basic validation.
        
        Returns:
            Simple test vector dictionary
        """
        # Simple case: 100 vs 200, should return 200
        return {
            'a': 100,
            'b': 200,
            'test_type': 'simple',
            'test_id': 'simple_100_200'
        }
    
    def generate_all_vectors(self, random_count: int = 10, seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate all types of test vectors.
        
        Args:
            random_count: Number of random vectors to generate
            seed: Random seed for reproducibility
            
        Returns:
            List of all test vectors
        """
        vectors = []
        
        # Add simple test
        vectors.append(self.generate_simple_test_pair())
        
        # Add corner cases
        vectors.extend(self.generate_corner_case_vectors())
        
        # Add random tests
        vectors.extend(self.generate_random_vectors(random_count, seed))
        
        self.logger.info(f"Generated total {len(vectors)} test vectors")
        return vectors