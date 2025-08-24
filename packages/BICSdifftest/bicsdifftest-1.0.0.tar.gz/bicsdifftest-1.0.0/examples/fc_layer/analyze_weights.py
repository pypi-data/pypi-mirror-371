#!/usr/bin/env python3
"""
Analyze weights and biases loading for corner_3 debugging.
"""

import json
import numpy as np
import torch

def analyze_test_data():
    """Analyze the test data JSON file."""
    print("=== Test Data Analysis ===")
    
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    # Extract weights and biases
    weights_int = np.array(test_data['weights']['integer'])
    weights_float = np.array(test_data['weights']['float_equiv'])
    weights_original = np.array(test_data['weights']['original_float'])
    
    biases_int = np.array(test_data['biases']['integer'])
    biases_float = np.array(test_data['biases']['float_equiv'])
    biases_original = np.array(test_data['biases']['original_float'])
    
    print(f"Weights shape: {weights_int.shape}")
    print(f"Biases shape: {biases_int.shape}")
    
    # Get all_max_pos test case
    all_max_pos_input = np.array(test_data['test_inputs']['all_max_pos']['float_equiv'])
    all_max_pos_expected = np.array(test_data['reference_outputs']['all_max_pos']['float_equiv'])
    all_max_pos_original = np.array(test_data['reference_outputs']['all_max_pos']['original_float'])
    
    print(f"\nAll max pos input: {all_max_pos_input[0]} (all same: {np.all(all_max_pos_input == all_max_pos_input[0])})")
    
    print(f"\nExpected outputs (fixed-point):")
    for i, val in enumerate(all_max_pos_expected):
        print(f"  Output[{i}]: {val}")
    
    print(f"\nExpected outputs (original):")
    for i, val in enumerate(all_max_pos_original):
        print(f"  Output[{i}]: {val}")
    
    # Manual calculation with test data weights
    print(f"\n=== Manual Calculation with Test Data ===")
    input_val = all_max_pos_input[0]  # 127.99609375
    
    for i in range(len(all_max_pos_expected)):
        # Sum weights for this output
        weight_sum = 0.0
        for j in range(weights_float.shape[0]):
            weight_sum += weights_float[j, i]
        
        bias = biases_float[i]
        manual_result = input_val * weight_sum + bias
        
        print(f"Output[{i}]:")
        print(f"  Weight sum: {weight_sum:.6f}")
        print(f"  Bias: {bias:.6f}")
        print(f"  Manual: {input_val:.6f} * {weight_sum:.6f} + {bias:.6f} = {manual_result:.6f}")
        print(f"  Expected (fixed-point): {all_max_pos_expected[i]:.6f}")
        print(f"  Expected (original): {all_max_pos_original[i]:.6f}")
        print(f"  Difference (manual vs fixed-point): {abs(manual_result - all_max_pos_expected[i]):.6f}")
        
        # Check saturation
        if all_max_pos_original[i] > 127.99609375:
            print(f"  -> Original {all_max_pos_original[i]:.6f} saturated to 127.99609375")
        elif all_max_pos_original[i] < -128.0:
            print(f"  -> Original {all_max_pos_original[i]:.6f} saturated to -128.0")
        
        print()

def test_fixed_point_conversion():
    """Test fixed-point conversion accuracy."""
    print("=== Fixed-Point Conversion Test ===")
    
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    # Test conversion accuracy
    weights_int = np.array(test_data['weights']['integer'])
    weights_float = np.array(test_data['weights']['float_equiv'])
    weights_original = np.array(test_data['weights']['original_float'])
    
    frac_scale = 256  # 2^8
    
    print(f"Testing first few weights:")
    for i in range(min(5, weights_int.shape[0])):
        for j in range(min(3, weights_int.shape[1])):
            int_val = weights_int[i, j]
            float_val = weights_float[i, j]
            orig_val = weights_original[i, j]
            
            # Convert integer to float
            converted_float = float(int_val) / frac_scale
            
            print(f"Weight[{i}][{j}]:")
            print(f"  Integer: {int_val}")
            print(f"  Float equiv: {float_val:.6f}")
            print(f"  Original: {orig_val:.6f}")
            print(f"  Converted: {converted_float:.6f}")
            print(f"  Match float equiv: {abs(converted_float - float_val) < 1e-6}")
            
            # Show quantization error
            quant_error = abs(orig_val - float_val)
            print(f"  Quantization error: {quant_error:.6f}")
            print()

if __name__ == "__main__":
    analyze_test_data()
    test_fixed_point_conversion()