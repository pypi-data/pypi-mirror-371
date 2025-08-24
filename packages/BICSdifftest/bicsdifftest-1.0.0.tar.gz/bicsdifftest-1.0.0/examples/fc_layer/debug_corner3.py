#!/usr/bin/env python3
"""
Corner 3 (all_max_pos) debugging script for FC Layer differential testing.
This script helps debug the specific failure in the corner_3 test case.
"""

import sys
import os
from pathlib import Path
import torch
import numpy as np

# Add framework to Python path
framework_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(framework_root))

from golden_model.models.fc_layer_model import FCLayerGoldenModel, FCLayerTestVectorGenerator

def debug_corner3():
    """Debug the corner_3 test case in detail."""
    print("=== Corner 3 (all_max_pos) Debugging ===")
    
    # Configuration matching test setup
    config = {
        'input_size': 100,
        'output_size': 10,
        'data_width': 16,
        'frac_bits': 8
    }
    
    # Create golden model
    golden_model = FCLayerGoldenModel(**config)
    
    # Generate test vectors
    vector_generator = FCLayerTestVectorGenerator(**config)
    
    # Generate weights and load into golden model
    weight_vectors, weights, biases = vector_generator.generate_weight_loading_vectors(seed=42)
    golden_model.load_weights_from_tensor(
        torch.tensor(weights, dtype=torch.float32),
        torch.tensor(biases, dtype=torch.float32)
    )
    
    print(f"Loaded weights: {weights.shape}, biases: {biases.shape}")
    print(f"Weight range: [{weights.min():.6f}, {weights.max():.6f}]")
    print(f"Bias range: [{biases.min():.6f}, {biases.max():.6f}]")
    
    # Generate corner case vectors
    corner_vectors = vector_generator.generate_corner_case_vectors()
    
    # Find corner_3 (all_max_pos)
    corner_3_vector = corner_vectors[3]  # Index 3 is "all_max_pos"
    
    print(f"\n=== Corner 3 Test Vector ===")
    print(f"Test type: {corner_3_vector.get('test_type', 'unknown')}")
    print(f"Corner value: {corner_3_vector.get('corner_value', 'unknown')}")
    print(f"Input shape: {len(corner_3_vector['input_data'])}")
    print(f"Input value (first): {corner_3_vector['input_data'][0]}")
    print(f"Input value (last): {corner_3_vector['input_data'][-1]}")
    
    # Convert input to fixed-point integers
    frac_scale = 1 << config['frac_bits']  # 256
    max_val = (1 << (config['data_width'] - 1)) - 1  # 32767
    min_val = -(1 << (config['data_width'] - 1))  # -32768
    
    input_ints = []
    for val in corner_3_vector['input_data']:
        int_val = int(val * frac_scale)
        int_val = max(min_val, min(max_val, int_val))  # Saturate
        input_ints.append(int_val)
    
    print(f"Fixed-point input (first): {input_ints[0]} (0x{input_ints[0]:04X})")
    print(f"Fixed-point input (all same): {all(x == input_ints[0] for x in input_ints)}")
    
    # Run golden model
    golden_outputs = golden_model(corner_3_vector)
    golden_checkpoints = golden_model.get_all_checkpoints()
    
    final_outputs = golden_checkpoints.get('final_outputs', {})
    output_data = final_outputs.get('output_data', torch.tensor([]))
    
    print(f"\n=== Golden Model Results ===")
    print(f"Output shape: {output_data.shape}")
    print("Output values:")
    for i, val in enumerate(output_data):
        print(f"  Output[{i}]: {val:.6f}")
    
    # Manual calculation verification
    print(f"\n=== Manual Calculation Verification ===")
    input_val = corner_3_vector['input_data'][0]  # 127.99609375
    print(f"Input value: {input_val}")
    
    for i in range(config['output_size']):
        # Calculate expected output manually
        bias = biases[i]
        weight_sum = sum(weights[j, i] for j in range(config['input_size']))
        manual_result = input_val * weight_sum + bias
        
        print(f"Output[{i}]:")
        print(f"  Bias: {bias:.6f}")
        print(f"  Weight sum: {weight_sum:.6f}")
        print(f"  Manual calc: {input_val:.6f} * {weight_sum:.6f} + {bias:.6f} = {manual_result:.6f}")
        print(f"  Golden model: {output_data[i]:.6f}")
        print(f"  Difference: {abs(manual_result - output_data[i].item()):.6f}")
        
        # Check if saturation is expected
        if manual_result > 127.99609375:
            print(f"  -> Should saturate to 127.99609375")
        elif manual_result < -128.0:
            print(f"  -> Should saturate to -128.0")
        
        print()
    
    # Analyze potential hardware issues
    print(f"\n=== Hardware Analysis ===")
    print(f"Q{config['data_width'] - config['frac_bits']}.{config['frac_bits']} format")
    print(f"Max positive value: {max_val / frac_scale}")
    print(f"Min negative value: {min_val / frac_scale}")
    print(f"Input magnitude: {input_val}")
    print(f"MAC operations per output: {config['input_size']}")
    print(f"Maximum possible accumulation (all positive): {input_val * config['input_size'] * (max_val / frac_scale)}")
    print(f"Maximum possible accumulation (all negative): {input_val * config['input_size'] * (min_val / frac_scale)}")
    
    # Check for potential overflow in intermediate calculations
    print(f"\n=== Overflow Analysis ===")
    for i in range(config['output_size']):
        weight_sum = sum(weights[j, i] for j in range(config['input_size']))
        intermediate_sum = input_val * weight_sum
        final_result = intermediate_sum + biases[i]
        
        print(f"Output[{i}]:")
        print(f"  Intermediate sum: {intermediate_sum:.6f}")
        print(f"  Final result: {final_result:.6f}")
        
        if abs(intermediate_sum) > 32767 / 256:  # Check if intermediate exceeds 16-bit
            print(f"  WARNING: Intermediate sum may overflow 16-bit accumulator!")
        
        if final_result > 127.99609375 or final_result < -128.0:
            print(f"  SATURATION: Result should be clamped")

def compare_with_reference():
    """Compare with reference outputs from test data."""
    print("\n=== Reference Comparison ===")
    
    # Expected reference outputs for all_max_pos from test data
    expected_float = [
        5.515625,
        5.5078125,
        -83.99609375,
        127.99609375,  # Saturated
        127.99609375,  # Saturated  
        -54.49609375,
        -81.48828125,
        64.0078125,
        52.01171875,
        102.4921875
    ]
    
    expected_original = [
        6.257951521509599,
        4.457935066507703,
        -83.7243727724202,
        188.07081554668744,  # Before saturation
        137.21339088961088,  # Before saturation
        -56.172520198033595,
        -82.44036075572848,
        65.62151777535684,
        53.81095046145411,
        100.60517668973291
    ]
    
    print("Expected outputs (after fixed-point conversion):")
    for i, val in enumerate(expected_float):
        print(f"  Output[{i}]: {val}")
    
    print("\nExpected outputs (before saturation):")
    for i, val in enumerate(expected_original):
        print(f"  Output[{i}]: {val}")
        if val > 127.99609375 or val < -128.0:
            saturated = max(-128.0, min(127.99609375, val))
            print(f"    -> Saturated to: {saturated}")

if __name__ == "__main__":
    debug_corner3()
    compare_with_reference()