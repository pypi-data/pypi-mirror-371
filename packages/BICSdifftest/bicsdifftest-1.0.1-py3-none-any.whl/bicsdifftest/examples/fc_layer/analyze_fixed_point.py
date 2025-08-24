#!/usr/bin/env python3
"""
Analyze fixed-point computation differences for corner_3 debugging.
"""

import json
import numpy as np
import torch
from decimal import Decimal, getcontext

# Set high precision for decimal calculations
getcontext().prec = 50

def analyze_fixed_point_precision():
    """Analyze fixed-point precision issues."""
    print("=== Fixed-Point Precision Analysis ===")
    
    # Load test data
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    # Extract weights and biases (using fixed-point equivalent)
    weights_int = np.array(test_data['weights']['integer'])
    weights_float = np.array(test_data['weights']['float_equiv'])
    biases_int = np.array(test_data['biases']['integer'])
    biases_float = np.array(test_data['biases']['float_equiv'])
    
    # All max positive input
    input_val = 127.99609375  # All inputs are this value
    input_int = 32767  # 0x7FFF
    expected_outputs = test_data['reference_outputs']['all_max_pos']['float_equiv']
    
    print(f"Input value: {input_val} (int: {input_int})")
    print(f"Fixed-point format: Q8.8 (16-bit, 8 fractional bits)")
    print(f"Scale factor: 256")
    
    # Different computation methods
    methods = {
        'method_1_float': "Pure floating-point MAC",
        'method_2_int_mac': "Integer MAC with final scaling", 
        'method_3_mixed': "Mixed precision with intermediate scaling",
        'method_4_decimal': "High-precision decimal arithmetic"
    }
    
    for output_idx in range(min(3, len(expected_outputs))):  # First 3 outputs
        print(f"\n=== Output[{output_idx}] Analysis ===")
        
        # Extract weights for this output
        output_weights_int = weights_int[:, output_idx]
        output_weights_float = weights_float[:, output_idx]
        bias_int = biases_int[output_idx]
        bias_float = biases_float[output_idx]
        
        expected = expected_outputs[output_idx]
        print(f"Expected result: {expected:.6f}")
        
        # Method 1: Pure floating-point
        result_1 = input_val * np.sum(output_weights_float) + bias_float
        print(f"Method 1 (float): {result_1:.6f} | Diff: {abs(result_1 - expected):.6f}")
        
        # Method 2: Integer MAC with final scaling
        # Simulate exact hardware: all computations in integer domain
        acc_int = 0
        for weight_int in output_weights_int:
            mac_result = input_int * weight_int  # 16-bit * 16-bit = 32-bit
            acc_int += mac_result
        acc_int += bias_int * 256  # Scale bias to match accumulator
        
        # Convert back to float (divide by scale^2 since we have two scale factors)
        result_2 = float(acc_int) / (256 * 256)
        print(f"Method 2 (int MAC): {result_2:.6f} | Diff: {abs(result_2 - expected):.6f}")
        
        # Method 3: Mixed precision (Golden Model style)
        # This simulates what the Golden Model might be doing
        acc_mixed = 0.0
        for weight_float in output_weights_float:
            # Convert input and weight back to int, multiply, then to float
            input_scaled = int(input_val * 256)
            weight_scaled = int(weight_float * 256)
            mac_int = input_scaled * weight_scaled
            mac_float = float(mac_int) / (256 * 256)
            acc_mixed += mac_float
        result_3 = acc_mixed + bias_float
        print(f"Method 3 (mixed): {result_3:.6f} | Diff: {abs(result_3 - expected):.6f}")
        
        # Method 4: High-precision decimal
        input_decimal = Decimal('127.99609375')
        bias_decimal = Decimal(str(bias_float))
        weight_sum_decimal = sum(Decimal(str(w)) for w in output_weights_float)
        result_4 = float(input_decimal * weight_sum_decimal + bias_decimal)
        print(f"Method 4 (decimal): {result_4:.6f} | Diff: {abs(result_4 - expected):.6f}")
        
        # Show intermediate values
        print(f"  Weight sum (float): {np.sum(output_weights_float):.8f}")
        print(f"  Weight sum (from int): {np.sum(output_weights_int) / 256:.8f}")
        print(f"  Bias (float): {bias_float:.8f}")
        print(f"  Bias (from int): {bias_int / 256:.8f}")
        
        # Check for saturation
        if result_1 > 127.99609375 or result_1 < -128.0:
            saturated = max(-128.0, min(127.99609375, result_1))
            print(f"  -> Should saturate to: {saturated:.6f}")

def analyze_quantization_errors():
    """Analyze quantization errors in weights and biases."""
    print("\n=== Quantization Error Analysis ===")
    
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    weights_int = np.array(test_data['weights']['integer'])
    weights_float = np.array(test_data['weights']['float_equiv']) 
    weights_original = np.array(test_data['weights']['original_float'])
    
    biases_int = np.array(test_data['biases']['integer'])
    biases_float = np.array(test_data['biases']['float_equiv'])
    biases_original = np.array(test_data['biases']['original_float'])
    
    # Analyze weight quantization errors
    weight_errors = np.abs(weights_original - weights_float)
    print(f"Weight quantization errors:")
    print(f"  Mean: {np.mean(weight_errors):.8f}")
    print(f"  Max: {np.max(weight_errors):.8f}")
    print(f"  Std: {np.std(weight_errors):.8f}")
    
    # Analyze bias quantization errors  
    bias_errors = np.abs(biases_original - biases_float)
    print(f"Bias quantization errors:")
    print(f"  Mean: {np.mean(bias_errors):.8f}")
    print(f"  Max: {np.max(bias_errors):.8f}")
    print(f"  Std: {np.std(bias_errors):.8f}")
    
    # Show cumulative effect for corner_3
    input_val = 127.99609375
    print(f"\nCumulative effect analysis for input {input_val}:")
    
    for output_idx in range(3):
        weight_error_sum = np.sum(weight_errors[:, output_idx])
        bias_error = bias_errors[output_idx]
        
        # Error contribution to final output
        error_contribution = input_val * weight_error_sum + bias_error
        
        print(f"Output[{output_idx}]:")
        print(f"  Weight error sum: {weight_error_sum:.8f}")
        print(f"  Bias error: {bias_error:.8f}")
        print(f"  Total error contribution: {error_contribution:.8f}")

def suggest_fixes():
    """Suggest potential fixes for the precision mismatch."""
    print("\n=== Suggested Fixes ===")
    
    fixes = [
        "1. Adjust tolerance in test framework to account for quantization errors",
        "2. Use identical fixed-point computation method in Golden Model",
        "3. Implement bit-exact hardware simulation in Golden Model",
        "4. Use double precision for intermediate calculations",
        "5. Implement proper rounding instead of truncation",
        "6. Match exact hardware MAC operation sequence"
    ]
    
    for fix in fixes:
        print(f"  {fix}")
    
    # Calculate reasonable tolerance based on observed differences
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    expected = test_data['reference_outputs']['all_max_pos']['float_equiv']
    
    # Use our debug results (approximate differences observed)
    observed_diffs = [0.207031, 0.183594, 0.191406]  # From debug output
    max_diff = max(observed_diffs)
    suggested_tolerance = max_diff * 1.1  # 10% margin
    
    print(f"\nSuggested tolerance for corner_3: {suggested_tolerance:.6f}")
    print(f"Current differences observed: {observed_diffs}")

if __name__ == "__main__":
    analyze_fixed_point_precision()
    analyze_quantization_errors()
    suggest_fixes()