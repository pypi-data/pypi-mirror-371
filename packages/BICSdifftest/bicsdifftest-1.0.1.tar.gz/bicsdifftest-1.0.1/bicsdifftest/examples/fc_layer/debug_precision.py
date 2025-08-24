#!/usr/bin/env python3
"""
Debug script to analyze the precision differences between hardware and software
implementations of the FC layer. This script performs step-by-step comparison
to identify the root cause of numerical mismatches.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import torch
import numpy as np
from golden_model.models.fc_layer_model import FCLayerGoldenModel, FCLayerTestVectorGenerator

class FixedPointDebugger:
    """Debug fixed-point arithmetic differences."""
    
    def __init__(self, data_width=16, frac_bits=8):
        self.data_width = data_width
        self.frac_bits = frac_bits
        self.frac_scale = 1 << frac_bits
        self.max_int = (1 << (data_width - 1)) - 1
        self.min_int = -(1 << (data_width - 1))
        
    def to_fixed_point_int(self, value):
        """Convert float to fixed-point integer (hardware representation)."""
        if isinstance(value, torch.Tensor):
            value = value.item()
        
        # Scale and round
        scaled = value * self.frac_scale
        rounded = round(scaled)
        
        # Saturate
        saturated = max(self.min_int, min(self.max_int, rounded))
        return int(saturated)
    
    def from_fixed_point_int(self, int_val):
        """Convert fixed-point integer back to float."""
        return float(int_val) / self.frac_scale
    
    def hardware_multiply(self, a_float, b_float):
        """Simulate hardware fixed-point multiplication exactly."""
        # Convert to integers
        a_int = self.to_fixed_point_int(a_float)
        b_int = self.to_fixed_point_int(b_float)
        
        # Multiply (results in 2*data_width bits)
        mult_result_full = a_int * b_int
        
        # Scale down by frac_bits (arithmetic right shift as in hardware)
        # This is what the hardware does: >>> frac_bits
        if mult_result_full >= 0:
            scaled_result = mult_result_full >> self.frac_bits
        else:
            # For negative numbers, arithmetic right shift
            scaled_result = -((-mult_result_full) >> self.frac_bits)
        
        # Saturate to data_width
        final_result = max(self.min_int, min(self.max_int, scaled_result))
        
        return self.from_fixed_point_int(final_result)
    
    def software_multiply_current(self, a_float, b_float):
        """Current software implementation from golden model."""
        # Convert to integer representation (same as golden model)
        a_int = int(a_float * self.frac_scale)
        b_int = int(b_float * self.frac_scale)
        
        # Clamp to data width first (same as hardware would do)
        a_int = max(self.min_int, min(self.max_int, a_int))
        b_int = max(self.min_int, min(self.max_int, b_int))
        
        # Multiply to get full precision result
        mult_result_full = a_int * b_int
        
        # Arithmetic right shift (>>> in Verilog)
        # Python's >> on signed integers is already arithmetic right shift
        result_scaled = mult_result_full >> self.frac_bits
        
        # Saturate to data width
        result_scaled = max(self.min_int, min(self.max_int, result_scaled))
        
        # Convert back to float
        return float(result_scaled) / self.frac_scale
    
    def compare_multiplications(self, test_cases):
        """Compare hardware and software multiplication implementations."""
        print("Comparing multiplication implementations:")
        print("=" * 80)
        
        for i, (a, b) in enumerate(test_cases):
            hw_result = self.hardware_multiply(a, b)
            sw_result = self.software_multiply_current(a, b)
            
            error = abs(hw_result - sw_result)
            
            print(f"Test {i+1}: {a:.6f} * {b:.6f}")
            print(f"  Hardware:  {hw_result:.6f}")
            print(f"  Software:  {sw_result:.6f}")
            print(f"  Error:     {error:.6f}")
            
            # Show intermediate calculations
            a_int = self.to_fixed_point_int(a)
            b_int = self.to_fixed_point_int(b)
            mult_full = a_int * b_int
            hw_scaled = mult_full >> self.frac_bits
            sw_scaled = mult_full // self.frac_scale
            
            print(f"  a_int={a_int}, b_int={b_int}")
            print(f"  mult_full={mult_full}")
            print(f"  hw_scaled (>>)={hw_scaled}, sw_scaled (//)={sw_scaled}")
            print()


def debug_fc_computation():
    """Debug FC layer computation step by step."""
    print("FC Layer Fixed-Point Computation Debug")
    print("=" * 60)
    
    # Parameters
    input_size = 100
    output_size = 10
    data_width = 16
    frac_bits = 8
    
    # Create debugger
    debugger = FixedPointDebugger(data_width, frac_bits)
    
    # Create golden model
    golden_model = FCLayerGoldenModel(input_size, output_size, data_width, frac_bits)
    
    # Generate simple test case
    np.random.seed(42)
    weights = np.random.randn(input_size, output_size) * 0.1
    biases = np.random.randn(output_size) * 0.01
    inputs = np.random.randn(input_size) * 0.5
    
    # Load weights into golden model
    golden_model.load_weights_from_tensor(
        torch.tensor(weights, dtype=torch.float32),
        torch.tensor(biases, dtype=torch.float32)
    )
    
    print(f"Test case statistics:")
    print(f"  Input range: [{np.min(inputs):.6f}, {np.max(inputs):.6f}]")
    print(f"  Weight range: [{np.min(weights):.6f}, {np.max(weights):.6f}]")
    print(f"  Bias range: [{np.min(biases):.6f}, {np.max(biases):.6f}]")
    print()
    
    # Test multiply operations with real values
    test_mult_cases = [
        (inputs[0], weights[0, 0]),
        (inputs[1], weights[1, 0]),
        (0.5, 0.1),
        (-0.3, 0.2),
        (1.0/256, 1.0/256),  # Small values
    ]
    
    debugger.compare_multiplications(test_mult_cases)
    
    # Simulate one neuron computation manually
    print("Manual neuron computation (output 0):")
    print("-" * 40)
    
    # Convert all inputs to fixed-point
    inputs_fixed = []
    for inp in inputs:
        inp_fixed = debugger.from_fixed_point_int(debugger.to_fixed_point_int(inp))
        inputs_fixed.append(inp_fixed)
    
    # Get fixed-point weights and bias for output 0
    weights_0 = golden_model.weights[:, 0].numpy()
    bias_0 = golden_model.biases[0].item()
    
    print(f"Bias 0: {bias_0:.6f}")
    
    # Manual MAC computation
    manual_accumulator = bias_0
    hw_accumulator = bias_0
    
    for i in range(min(5, input_size)):  # Show first 5 operations
        inp = inputs_fixed[i]
        weight = weights_0[i]
        
        # Software method (current golden model)
        sw_mult = debugger.software_multiply_current(inp, weight)
        manual_accumulator += sw_mult
        
        # Hardware method
        hw_mult = debugger.hardware_multiply(inp, weight)
        hw_accumulator += hw_mult
        
        print(f"  MAC {i}: {inp:.6f} * {weight:.6f}")
        print(f"    SW mult: {sw_mult:.6f}, HW mult: {hw_mult:.6f}, diff: {abs(sw_mult-hw_mult):.6f}")
        print(f"    SW acc:  {manual_accumulator:.6f}, HW acc:  {hw_accumulator:.6f}")
    
    print(f"\nAfter 5 operations:")
    print(f"  SW accumulator: {manual_accumulator:.6f}")
    print(f"  HW accumulator: {hw_accumulator:.6f}")
    print(f"  Difference: {abs(manual_accumulator - hw_accumulator):.6f}")
    
    # Run full golden model computation
    test_inputs = {
        'mode': 1,
        'valid': True,
        'input_data': inputs.tolist()
    }
    
    golden_outputs = golden_model(test_inputs)
    print(f"\nGolden model output 0: {golden_outputs['output_data'][0]:.6f}")
    
    # Let's check the golden model's internal weights and see what went wrong
    print(f"\nDebug golden model weights (first 5 for output 0):")
    stored_weights = golden_model.weights[:5, 0].numpy()
    expected_weights = weights_0[:5]
    for i in range(5):
        print(f"  Weight {i}: stored={stored_weights[i]:.6f}, expected={expected_weights[i]:.6f}")
        
    print(f"\nDebug golden model bias 0:")
    stored_bias = golden_model.biases[0].item()
    expected_bias = bias_0
    print(f"  Bias 0: stored={stored_bias:.6f}, expected={expected_bias:.6f}")
    
    # Compare with manual computation
    print(f"\nFinal comparison:")
    print(f"  Manual SW output 0: {manual_accumulator:.6f}")
    print(f"  Manual HW output 0: {hw_accumulator:.6f}")
    print(f"  Golden model output 0: {golden_outputs['output_data'][0]:.6f}")
    
    # Let's also check what the golden model thinks the input should be
    checkpoints = golden_model.get_all_checkpoints()
    if 'inference_input' in checkpoints:
        golden_input_fixed = checkpoints['inference_input']['fixed_point_input']
        print(f"\nGolden model input (first 5): {golden_input_fixed[:5].tolist()}")
        print(f"Manual input (first 5): {inputs_fixed[:5]}")
        
    # Check MAC operations in golden model
    if 'mac_op_0_0' in checkpoints:
        print(f"\nGolden model MAC operations (output 0):")
        for i in range(min(5, len(checkpoints))):
            checkpoint_key = f'mac_op_0_{i}'
            if checkpoint_key in checkpoints:
                mac_data = checkpoints[checkpoint_key]
                print(f"  MAC {i}: {mac_data['input']:.6f} * {mac_data['weight']:.6f} = {mac_data['mult_result']:.6f}, acc = {mac_data['accumulator']:.6f}")
    
    # Check final output details
    if 'output_0_final' in checkpoints:
        final_data = checkpoints['output_0_final']
        print(f"\nGolden model final output 0:")
        print(f"  Final accumulator: {final_data['accumulator']:.6f}")
        print(f"  Saturated result: {final_data['saturated_result']:.6f}")


if __name__ == "__main__":
    debug_fc_computation()