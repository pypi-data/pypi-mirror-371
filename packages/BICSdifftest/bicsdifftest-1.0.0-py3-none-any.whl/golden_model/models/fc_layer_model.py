"""
Golden model for Fully Connected Layer design.

This module implements a PyTorch-based golden model that mirrors
the functionality of the fc_layer Verilog module with exact fixed-point arithmetic.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Any, Tuple, Optional, List
import logging
import copy

# Import base classes
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from golden_model.base import GoldenModelBase, PipelinedGoldenModel


class FCLayerGoldenModel(GoldenModelBase):
    """
    PyTorch golden model for the Fully Connected Layer design.
    
    This model implements the same functionality as the Verilog fc_layer module
    with fixed-point arithmetic and identical computation flow.
    """
    
    def __init__(self, input_size: int = 100, output_size: int = 10, 
                 data_width: int = 16, frac_bits: int = 8, device: str = "cpu"):
        """
        Initialize FC Layer golden model.
        
        Args:
            input_size: Number of input neurons
            output_size: Number of output neurons  
            data_width: Bit width for data (16 bits)
            frac_bits: Number of fractional bits (8 bits)
            device: Device to run computations on
        """
        super().__init__("FCLayerGoldenModel", device)
        
        self.input_size = input_size
        self.output_size = output_size
        self.data_width = data_width
        self.frac_bits = frac_bits
        self.weight_width = data_width  # Same as data width
        
        # Fixed-point parameters
        self.max_int_value = (1 << (data_width - 1)) - 1
        self.min_int_value = -(1 << (data_width - 1))
        self.frac_scale = 1 << frac_bits
        
        # Model parameters (initialized to zero, will be loaded)
        self.weights = torch.zeros((input_size, output_size), dtype=torch.float32)
        self.biases = torch.zeros(output_size, dtype=torch.float32)
        
        # State tracking
        self.mode = 0  # 0: weight loading, 1: inference
        self.weights_loaded = False
        self.biases_loaded = False
        
        # Debug state
        self.current_state = 0  # FSM state
        self.input_counter = 0
        self.output_counter = 0
        self.accumulator = 0
        
        self.logger.info(f"Initialized FC Layer: {input_size}x{output_size}, "
                        f"{data_width}-bit data, {frac_bits} fractional bits")
    
    def _forward_impl(self, inputs: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """
        Forward pass of the FC Layer golden model.
        
        Args:
            inputs: Dictionary containing mode, input_data, weights, biases, etc.
            
        Returns:
            Dictionary containing outputs and debug information
        """
        # Extract inputs
        mode = int(inputs.get('mode', 1))  # Default to inference mode
        valid = bool(inputs.get('valid', False))
        
        # Save input checkpoint
        input_data_dict = {
            'mode': mode,
            'valid': valid,
            'input_data': inputs.get('input_data', None),
            'weight_data': inputs.get('weight_data', None),
            'weight_addr': inputs.get('weight_addr', None),
            'weight_we': inputs.get('weight_we', False),
            'bias_data': inputs.get('bias_data', None),
            'bias_addr': inputs.get('bias_addr', None),
            'bias_we': inputs.get('bias_we', False)
        }
        self.add_checkpoint('inputs', input_data_dict)
        
        if not valid:
            return self._create_idle_output()
        
        # Handle different modes
        if mode == 0:
            # Weight/bias loading mode
            return self._handle_weight_loading(inputs)
        else:
            # Inference mode  
            return self._handle_inference(inputs)
    
    def _handle_weight_loading(self, inputs: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """Handle weight and bias loading."""
        outputs = self._create_idle_output()
        
        # Weight loading
        if inputs.get('weight_we', False):
            weight_addr = int(inputs.get('weight_addr', 0))
            weight_data = inputs.get('weight_data', 0)
            
            # Decode address (same encoding as Verilog)
            input_idx = (weight_addr >> 3) & 0x7F  # Upper 7 bits for input index
            output_idx = weight_addr & 0x07        # Lower 3 bits for output index
            
            if input_idx < self.input_size and output_idx < self.output_size:
                # Convert to fixed-point representation
                fixed_weight = self._to_fixed_point(weight_data)
                self.weights[input_idx, output_idx] = fixed_weight
                
                self.add_checkpoint('weight_loading', {
                    'input_idx': input_idx,
                    'output_idx': output_idx,
                    'raw_data': weight_data,
                    'fixed_point': fixed_weight
                })
        
        # Bias loading
        if inputs.get('bias_we', False):
            bias_addr = int(inputs.get('bias_addr', 0))
            bias_data = inputs.get('bias_data', 0)
            
            if bias_addr < self.output_size:
                # Convert to fixed-point representation
                fixed_bias = self._to_fixed_point(bias_data)
                self.biases[bias_addr] = fixed_bias
                
                self.add_checkpoint('bias_loading', {
                    'bias_addr': bias_addr,
                    'raw_data': bias_data,
                    'fixed_point': fixed_bias
                })
        
        # Update ready state
        outputs['ready'] = torch.tensor(True)
        outputs['debug_state'] = torch.tensor(1, dtype=torch.int32)  # LOAD_WEIGHTS state
        
        return outputs
    
    def _handle_inference(self, inputs: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """Handle inference computation."""
        # Get input data
        input_data = inputs.get('input_data', None)
        if input_data is None:
            return self._create_idle_output()
        
        # Convert input to tensor if needed and apply fixed-point conversion
        if isinstance(input_data, (list, np.ndarray)):
            input_tensor = torch.tensor(input_data, dtype=torch.float32)
        elif isinstance(input_data, torch.Tensor):
            input_tensor = input_data.float()
        else:
            return self._create_idle_output()
        
        # Ensure correct shape
        if input_tensor.shape[-1] != self.input_size:
            self.logger.error(f"Input size mismatch: expected {self.input_size}, got {input_tensor.shape[-1]}")
            return self._create_idle_output()
        
        # Flatten to 1D if needed
        if len(input_tensor.shape) > 1:
            input_tensor = input_tensor.flatten()[:self.input_size]
        
        # Convert inputs to fixed-point
        input_fixed = torch.tensor([self._to_fixed_point(x.item()) for x in input_tensor])
        
        self.add_checkpoint('inference_input', {
            'raw_input': input_tensor,
            'fixed_point_input': input_fixed
        })
        
        # Simulate the hardware computation flow
        outputs = self._simulate_hardware_computation(input_fixed)
        
        return outputs
    
    def _simulate_hardware_computation(self, input_fixed: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Simulate the exact hardware computation flow with pipeline stages.
        """
        output_results = torch.zeros(self.output_size, dtype=torch.float32)
        debug_accumulators = []
        debug_states = []
        
        # For each output neuron
        for output_idx in range(self.output_size):
            # Initialize accumulator with bias (sign-extended)
            bias_val = self.biases[output_idx].item()
            accumulator = self._extend_for_accumulation(bias_val)
            
            self.add_checkpoint(f'output_{output_idx}_init', {
                'bias': bias_val,
                'initial_accumulator': accumulator
            })
            
            # Accumulate: MAC operation for each input
            for input_idx in range(self.input_size):
                input_val = input_fixed[input_idx].item()
                weight_val = self.weights[input_idx, output_idx].item()
                
                # Multiply (fixed-point multiplication)
                mult_result = self._fixed_point_multiply(input_val, weight_val)
                
                # Add to accumulator
                accumulator = self._fixed_point_add(accumulator, mult_result)
                
                # Debug checkpoint for first few operations
                if input_idx < 3:  # Save first 3 for debugging
                    self.add_checkpoint(f'mac_op_{output_idx}_{input_idx}', {
                        'input': input_val,
                        'weight': weight_val,
                        'mult_result': mult_result,
                        'accumulator': accumulator
                    })
            
            debug_accumulators.append(accumulator)
            
            # Saturate result to output width
            final_result = self._saturate_to_output(accumulator)
            output_results[output_idx] = final_result
            
            self.add_checkpoint(f'output_{output_idx}_final', {
                'accumulator': accumulator,
                'saturated_result': final_result
            })
        
        # Create output dictionary
        outputs = {
            'output_data': output_results,
            'valid': torch.tensor(True),
            'ready': torch.tensor(False),  # Not ready during computation
            'debug_state': torch.tensor(5, dtype=torch.int32),  # OUTPUT state
            'debug_accumulator': torch.tensor(debug_accumulators[0] if debug_accumulators else 0, dtype=torch.float32),
            'debug_addr_counter': torch.tensor((self.input_size - 1) << 3 | (self.output_size - 1), dtype=torch.int32),
            'debug_flags': torch.tensor([1, 0, 0, 1], dtype=torch.int32)  # [computation_done, overflow, underflow, valid]
        }
        
        self.add_checkpoint('final_outputs', outputs)
        
        return outputs
    
    def _to_fixed_point(self, value: float) -> float:
        """
        Convert floating point value to fixed-point representation.
        
        Args:
            value: Floating point value
            
        Returns:
            Fixed-point value as float (for easier computation)
        """
        if isinstance(value, torch.Tensor):
            value = value.item()
        
        # Scale and round
        scaled = value * self.frac_scale
        rounded = round(scaled)
        
        # Saturate to data width
        rounded = max(self.min_int_value, min(self.max_int_value, rounded))
        
        # Convert back to float for computation
        return float(rounded) / self.frac_scale
    
    def _extend_for_accumulation(self, value: float) -> float:
        """Extend value for accumulation (simulate wider accumulator)."""
        # In hardware, we use a wider accumulator to prevent overflow during MAC
        return value
    
    def _fixed_point_multiply(self, a: float, b: float) -> float:
        """
        Fixed-point multiplication matching hardware behavior exactly.
        This implements the same logic as the Verilog: mult >>> FRAC_BITS
        """
        # Convert to integer representation (same as hardware)
        a_int = int(a * self.frac_scale)
        b_int = int(b * self.frac_scale)
        
        # Clamp to data width first (same as hardware would do)
        a_int = max(self.min_int_value, min(self.max_int_value, a_int))
        b_int = max(self.min_int_value, min(self.max_int_value, b_int))
        
        # Multiply to get full precision result
        mult_result_full = a_int * b_int
        
        # Arithmetic right shift (>>> in Verilog)
        # Python's >> on signed integers is already arithmetic right shift
        result_scaled = mult_result_full >> self.frac_bits
        
        # Saturate to data width
        result_scaled = max(self.min_int_value, min(self.max_int_value, result_scaled))
        
        # Convert back to float
        return float(result_scaled) / self.frac_scale
    
    def _fixed_point_add(self, a: float, b: float) -> float:
        """Fixed-point addition."""
        return a + b  # Addition is straightforward in fixed-point
    
    def _saturate_to_output(self, value: float) -> float:
        """
        Saturate accumulator value to output data width.
        """
        # Convert to integer for saturation check
        value_int = int(value * self.frac_scale)
        
        # Check for overflow/underflow
        if value_int > self.max_int_value:
            saturated_int = self.max_int_value
        elif value_int < self.min_int_value:
            saturated_int = self.min_int_value
        else:
            saturated_int = value_int
        
        # Convert back to float
        return float(saturated_int) / self.frac_scale
    
    def _create_idle_output(self) -> Dict[str, torch.Tensor]:
        """Create output for idle/invalid states."""
        return {
            'output_data': torch.zeros(self.output_size, dtype=torch.float32),
            'valid': torch.tensor(False),
            'ready': torch.tensor(True),
            'debug_state': torch.tensor(0, dtype=torch.int32),  # IDLE state
            'debug_accumulator': torch.tensor(0.0, dtype=torch.float32),
            'debug_addr_counter': torch.tensor(0, dtype=torch.int32),
            'debug_flags': torch.tensor([0, 0, 0, 0], dtype=torch.int32)  # All flags false
        }
    
    def load_weights_from_tensor(self, weight_tensor: torch.Tensor, bias_tensor: torch.Tensor):
        """
        Load weights and biases from tensors (utility function for testing).
        
        Args:
            weight_tensor: Tensor of shape (input_size, output_size)
            bias_tensor: Tensor of shape (output_size,)
        """
        assert weight_tensor.shape == (self.input_size, self.output_size)
        assert bias_tensor.shape == (self.output_size,)
        
        # Convert to fixed-point
        for i in range(self.input_size):
            for j in range(self.output_size):
                self.weights[i, j] = self._to_fixed_point(weight_tensor[i, j].item())
        
        for j in range(self.output_size):
            self.biases[j] = self._to_fixed_point(bias_tensor[j].item())
        
        self.weights_loaded = True
        self.biases_loaded = True
        
        self.add_checkpoint('tensor_loading', {
            'original_weights': weight_tensor,
            'original_biases': bias_tensor,
            'fixed_weights': self.weights.clone(),
            'fixed_biases': self.biases.clone()
        })
    
    def get_current_weights(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get current weights and biases."""
        return self.weights.clone(), self.biases.clone()


class FCLayerTestVectorGenerator:
    """Generate test vectors for FC Layer verification."""
    
    def __init__(self, input_size: int = 100, output_size: int = 10, 
                 data_width: int = 16, frac_bits: int = 8):
        self.input_size = input_size
        self.output_size = output_size
        self.data_width = data_width
        self.frac_bits = frac_bits
        
        # Fixed-point parameters
        self.max_value = (1 << (data_width - 1)) - 1
        self.min_value = -(1 << (data_width - 1))
        self.frac_scale = 1 << frac_bits
        
    def generate_weight_loading_vectors(self, seed: int = 42) -> List[Dict[str, Any]]:
        """Generate test vectors for weight loading."""
        np.random.seed(seed)
        test_vectors = []
        
        # Generate random weights and biases
        weights = np.random.randn(self.input_size, self.output_size) * 0.1
        biases = np.random.randn(self.output_size) * 0.01
        
        # Convert to fixed-point integers for loading
        weight_ints = np.clip(weights * self.frac_scale, self.min_value, self.max_value).astype(int)
        bias_ints = np.clip(biases * self.frac_scale, self.min_value, self.max_value).astype(int)
        
        # Create weight loading vectors
        for i in range(self.input_size):
            for j in range(self.output_size):
                addr = (i << 3) | j  # Encode address as in hardware
                test_vectors.append({
                    'mode': 0,
                    'valid': True,
                    'weight_addr': addr,
                    'weight_data': int(weight_ints[i, j]),
                    'weight_we': True,
                    'bias_we': False,
                    'test_type': 'weight_loading',
                    'expected_input_idx': i,
                    'expected_output_idx': j
                })
        
        # Create bias loading vectors
        for j in range(self.output_size):
            test_vectors.append({
                'mode': 0,
                'valid': True,
                'bias_addr': j,
                'bias_data': int(bias_ints[j]),
                'bias_we': True,
                'weight_we': False,
                'test_type': 'bias_loading'
            })
        
        return test_vectors, weights, biases
    
    def generate_inference_vectors(self, count: int = 100, seed: int = 42) -> List[Dict[str, Any]]:
        """Generate inference test vectors."""
        np.random.seed(seed)
        test_vectors = []
        
        for i in range(count):
            # Generate random input
            input_data = np.random.randn(self.input_size) * 0.5
            
            # Convert to fixed-point range for realistic testing
            input_fixed = np.clip(input_data * self.frac_scale, self.min_value, self.max_value) / self.frac_scale
            
            test_vectors.append({
                'mode': 1,
                'valid': True,
                'input_data': input_fixed.tolist(),
                'weight_we': False,
                'bias_we': False,
                'test_type': 'inference'
            })
        
        return test_vectors
    
    def generate_corner_case_vectors(self) -> List[Dict[str, Any]]:
        """Generate corner case test vectors."""
        test_vectors = []
        
        # Corner case values
        corner_values = [
            0.0,           # Zero
            1.0 / self.frac_scale,    # Minimum positive
            -1.0 / self.frac_scale,   # Minimum negative  
            self.max_value / self.frac_scale,  # Maximum positive
            self.min_value / self.frac_scale,  # Maximum negative (most negative)
        ]
        
        for corner_val in corner_values:
            # All inputs set to corner value
            input_data = [corner_val] * self.input_size
            
            test_vectors.append({
                'mode': 1,
                'valid': True,
                'input_data': input_data,
                'weight_we': False,
                'bias_we': False,
                'test_type': 'corner_case',
                'corner_value': corner_val
            })
        
        # All zeros
        test_vectors.append({
            'mode': 1,
            'valid': True,
            'input_data': [0.0] * self.input_size,
            'test_type': 'all_zeros'
        })
        
        # Single non-zero input
        for i in range(min(5, self.input_size)):  # Test first 5 inputs
            input_data = [0.0] * self.input_size
            input_data[i] = 1.0 / self.frac_scale  # Set one input to minimum positive
            
            test_vectors.append({
                'mode': 1,
                'valid': True,
                'input_data': input_data,
                'test_type': 'single_input',
                'active_input': i
            })
        
        return test_vectors
    
    def generate_comprehensive_test_suite(self) -> Tuple[List[Dict[str, Any]], np.ndarray, np.ndarray]:
        """Generate a comprehensive test suite including all test types."""
        
        # Generate weight loading vectors and get the weights/biases
        weight_vectors, weights, biases = self.generate_weight_loading_vectors()
        
        # Generate inference vectors
        inference_vectors = self.generate_inference_vectors(50)  # Reduced for manageable testing
        
        # Generate corner cases
        corner_vectors = self.generate_corner_case_vectors()
        
        # Combine all vectors
        all_vectors = weight_vectors + inference_vectors + corner_vectors
        
        return all_vectors, weights, biases