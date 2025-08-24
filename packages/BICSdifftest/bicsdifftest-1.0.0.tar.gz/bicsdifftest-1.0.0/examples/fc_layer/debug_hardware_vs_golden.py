#!/usr/bin/env python3
"""
Debug hardware vs Golden Model differences.
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

def compare_with_hardware_simulation():
    """Compare Golden Model with hardware simulation using test data."""
    print("=== Hardware vs Golden Model Analysis ===")
    
    # Load test data
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    # Extract test data for all_max_pos (corner_3)
    weights_float = np.array(test_data['weights']['float_equiv'])
    biases_float = np.array(test_data['biases']['float_equiv'])
    all_max_pos_input = test_data['test_inputs']['all_max_pos']['float_equiv']
    expected_outputs = test_data['reference_outputs']['all_max_pos']['float_equiv']
    
    print(f"Input: all values = {all_max_pos_input[0]}")
    print(f"Expected outputs (from test data): {expected_outputs}")
    
    # Create and configure Golden Model
    config = {
        'input_size': 100,
        'output_size': 10,
        'data_width': 16,
        'frac_bits': 8
    }
    
    golden_model = FCLayerGoldenModel(**config)
    weights_tensor = torch.tensor(weights_float, dtype=torch.float32)
    biases_tensor = torch.tensor(biases_float, dtype=torch.float32)
    golden_model.load_weights_from_tensor(weights_tensor, biases_tensor)
    
    # Run Golden Model
    test_vector = {
        'input_data': all_max_pos_input,
        'valid': True,
        'mode': 1
    }
    
    golden_outputs = golden_model(test_vector)
    golden_results = golden_outputs['output_data'].numpy()
    
    print(f"Golden Model outputs: {golden_results}")
    print(f"Golden vs Expected differences: {np.abs(golden_results - expected_outputs)}")
    
    # Since we modified the test generation to match Golden Model,
    # these should be nearly identical
    assert np.allclose(golden_results, expected_outputs, atol=1e-6), "Golden Model doesn't match test data!"
    print("✅ Golden Model matches test data perfectly")
    
    # The hardware error mentioned in log was max_error: 1.28e+02
    # This suggests hardware outputs are very different
    print(f"\n=== Hardware Error Analysis ===")
    print(f"Reported hardware error: 128 (1.28e+02)")
    print(f"This suggests hardware outputs are completely different from Golden Model")
    
    # Possible hardware outputs causing this error
    print(f"\nPossible scenarios:")
    print(f"1. Hardware outputs all zeros: max error would be ~128 (max expected value)")
    print(f"2. Hardware has wrong fixed-point scaling")
    print(f"3. Hardware MAC implementation differs from Golden Model")
    print(f"4. Hardware weight/bias loading is incorrect")
    print(f"5. Hardware input processing is wrong")
    
    # Let's simulate some of these scenarios
    zero_outputs = np.zeros(10)
    error_if_zero = np.max(np.abs(expected_outputs - zero_outputs))
    print(f"\nIf hardware outputs all zeros, error would be: {error_if_zero:.1f}")
    
    # Simulate wrong scaling (e.g., missing division by 256)
    scaled_outputs = np.array(expected_outputs) * 256
    error_if_wrong_scale = np.max(np.abs(expected_outputs - scaled_outputs))
    print(f"If hardware has wrong scaling (*256), error would be: {error_if_wrong_scale:.1f}")
    
    # Simulate using integer outputs without proper scaling
    expected_ints = np.array(test_data['reference_outputs']['all_max_pos']['integer'])
    error_if_int_as_float = np.max(np.abs(expected_outputs - expected_ints))
    print(f"If hardware returns integers as floats, error would be: {error_if_int_as_float:.1f}")

def analyze_specific_corner_3_values():
    """Analyze the specific values for corner_3."""
    print(f"\n=== Corner 3 Value Analysis ===")
    
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    expected_float = test_data['reference_outputs']['all_max_pos']['float_equiv']
    expected_int = test_data['reference_outputs']['all_max_pos']['integer']
    
    print(f"Expected outputs (float_equiv): {expected_float}")
    print(f"Expected outputs (integer): {expected_int}")
    
    # Convert integers back to float
    converted_back = [x / 256.0 for x in expected_int]
    print(f"Integer->Float conversion: {converted_back}")
    
    # Check if they match
    diff = np.abs(np.array(expected_float) - np.array(converted_back))
    print(f"Conversion differences: {diff}")
    print(f"Max conversion difference: {np.max(diff)}")

if __name__ == "__main__":
    compare_with_hardware_simulation()
    analyze_specific_corner_3_values()