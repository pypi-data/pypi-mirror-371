#!/usr/bin/env python3
"""
Test Golden Model MAC operations in detail.
"""

import sys
import json
import numpy as np
import torch
from pathlib import Path

# Add framework to Python path
framework_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(framework_root))

from golden_model.models.fc_layer_model import FCLayerGoldenModel

def test_fixed_point_multiply():
    """Test the fixed-point multiply operation."""
    print("=== Fixed-Point Multiply Test ===")
    
    config = {
        'input_size': 100,
        'output_size': 10,
        'data_width': 16,
        'frac_bits': 8
    }
    
    golden_model = FCLayerGoldenModel(**config)
    
    # Test multiplication with known values
    input_val = 127.99609375  # 0x7FFF / 256
    weight_val = 0.04296875   # 11/256 = 0x000B
    
    print(f"Input: {input_val} (int: {int(input_val * 256)})")
    print(f"Weight: {weight_val} (int: {int(weight_val * 256)})")
    
    # Golden Model multiplication
    gm_result = golden_model._fixed_point_multiply(input_val, weight_val)
    
    # Manual calculation
    input_int = int(input_val * 256)  # 32767
    weight_int = int(weight_val * 256)  # 11
    mult_full = input_int * weight_int  # 360337
    mult_scaled = mult_full >> 8  # 1407 
    manual_result = mult_scaled / 256.0  # 5.49609375
    
    # Expected result (floating point)
    expected = input_val * weight_val
    
    print(f"Golden Model result: {gm_result}")
    print(f"Manual calculation: {manual_result}")
    print(f"Expected (float): {expected}")
    print(f"Difference (GM vs Manual): {abs(gm_result - manual_result)}")
    print(f"Difference (GM vs Expected): {abs(gm_result - expected)}")

def test_mac_operation():
    """Test a complete MAC operation."""
    print("\n=== MAC Operation Test ===")
    
    # Load test data 
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    weights_float = np.array(test_data['weights']['float_equiv'])
    biases_float = np.array(test_data['biases']['float_equiv'])
    
    config = {
        'input_size': 100,
        'output_size': 10,
        'data_width': 16,
        'frac_bits': 8
    }
    
    golden_model = FCLayerGoldenModel(**config)
    
    # Load weights
    weights_tensor = torch.tensor(weights_float, dtype=torch.float32)
    biases_tensor = torch.tensor(biases_float, dtype=torch.float32)
    golden_model.load_weights_from_tensor(weights_tensor, biases_tensor)
    
    # Test first output with all max positive inputs
    input_val = 127.99609375
    output_idx = 0
    
    print(f"Testing Output[{output_idx}] with input {input_val}")
    
    # Golden Model MAC (step by step)
    accumulator = biases_float[output_idx]  # Start with bias
    print(f"Initial accumulator (bias): {accumulator}")
    
    for i in range(min(5, weights_float.shape[0])):  # First 5 weights
        weight = weights_float[i, output_idx]
        
        # Golden Model multiply
        mult_gm = golden_model._fixed_point_multiply(input_val, weight)
        
        # Manual multiply
        input_int = int(input_val * 256)
        weight_int = int(weight * 256)
        mult_manual = (input_int * weight_int >> 8) / 256.0
        
        # Float multiply
        mult_float = input_val * weight
        
        accumulator += mult_gm
        
        print(f"  Weight[{i}]: {weight:.6f}")
        print(f"    GM mult: {mult_gm:.6f}")
        print(f"    Manual:  {mult_manual:.6f}")
        print(f"    Float:   {mult_float:.6f}")
        print(f"    Accumulator: {accumulator:.6f}")
    
    # Full computation
    full_acc = biases_float[output_idx]
    for i in range(weights_float.shape[0]):
        weight = weights_float[i, output_idx]
        mult_result = golden_model._fixed_point_multiply(input_val, weight)
        full_acc += mult_result
    
    print(f"\nFull MAC result: {full_acc:.6f}")
    
    # Compare with expected
    expected = test_data['reference_outputs']['all_max_pos']['float_equiv'][output_idx]
    print(f"Expected result: {expected:.6f}")
    print(f"Difference: {abs(full_acc - expected):.6f}")

def diagnose_precision_loss():
    """Diagnose where precision is being lost."""
    print("\n=== Precision Loss Diagnosis ===")
    
    config = {
        'input_size': 100,
        'output_size': 10,
        'data_width': 16,
        'frac_bits': 8
    }
    
    golden_model = FCLayerGoldenModel(**config)
    
    # Test cases that might cause precision issues
    test_cases = [
        (127.99609375, 0.00390625, "Max input, small weight"),
        (127.99609375, 0.99609375, "Max input, large weight"),
        (0.00390625, 0.99609375, "Small input, large weight"),
        (127.99609375, -0.99609375, "Max input, large negative weight")
    ]
    
    for input_val, weight_val, description in test_cases:
        print(f"\n{description}:")
        print(f"  Input: {input_val} | Weight: {weight_val}")
        
        # Golden Model
        gm_result = golden_model._fixed_point_multiply(input_val, weight_val)
        
        # Integer simulation (what hardware does)
        input_int = int(input_val * 256)
        weight_int = int(weight_val * 256)
        
        # Check saturation in Golden Model
        saturated_input = max(-32768, min(32767, input_int))
        saturated_weight = max(-32768, min(32767, weight_int))
        
        mult_full = saturated_input * saturated_weight
        mult_scaled = mult_full >> 8
        saturated_result = max(-32768, min(32767, mult_scaled))
        hw_result = saturated_result / 256.0
        
        # Float reference
        float_result = input_val * weight_val
        
        print(f"  Input int: {input_int} -> saturated: {saturated_input}")
        print(f"  Weight int: {weight_int} -> saturated: {saturated_weight}")
        print(f"  Mult full: {mult_full}")
        print(f"  Mult scaled: {mult_scaled} -> saturated: {saturated_result}")
        print(f"  Golden Model: {gm_result:.8f}")
        print(f"  HW simulation: {hw_result:.8f}")
        print(f"  Float reference: {float_result:.8f}")
        print(f"  GM vs HW: {abs(gm_result - hw_result):.8f}")
        print(f"  GM vs Float: {abs(gm_result - float_result):.8f}")

if __name__ == "__main__":
    test_fixed_point_multiply()
    test_mac_operation() 
    diagnose_precision_loss()