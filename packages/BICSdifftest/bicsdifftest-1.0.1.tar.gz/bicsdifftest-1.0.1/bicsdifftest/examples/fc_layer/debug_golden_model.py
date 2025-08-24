#!/usr/bin/env python3
"""
Debug Golden Model by loading weights directly from test data.
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

def debug_with_test_weights():
    """Debug using exact weights from test data."""
    print("=== Debug Golden Model with Test Data Weights ===")
    
    # Load test data
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    # Extract weights and biases 
    weights_float = np.array(test_data['weights']['float_equiv'])  # Use fixed-point equivalent
    biases_float = np.array(test_data['biases']['float_equiv'])    # Use fixed-point equivalent
    
    print(f"Loaded weights: {weights_float.shape}")
    print(f"Loaded biases: {biases_float.shape}")
    
    # Configuration
    config = {
        'input_size': 100,
        'output_size': 10,
        'data_width': 16,
        'frac_bits': 8
    }
    
    # Create golden model
    golden_model = FCLayerGoldenModel(**config)
    
    # Load weights directly from test data (weights_float is already (input_size, output_size))
    weights_tensor = torch.tensor(weights_float, dtype=torch.float32)  # Shape: (input_size, output_size)
    biases_tensor = torch.tensor(biases_float, dtype=torch.float32)    # Shape: (output_size,)
    
    print(f"Weight tensor shape: {weights_tensor.shape}")
    print(f"Bias tensor shape: {biases_tensor.shape}")
    
    # Load weights using the direct method
    golden_model.load_weights_from_tensor(weights_tensor, biases_tensor)
    
    # Get all_max_pos test vector
    all_max_pos_input = test_data['test_inputs']['all_max_pos']['float_equiv']
    all_max_pos_expected = test_data['reference_outputs']['all_max_pos']['float_equiv']
    
    # Create test vector in expected format (Golden Model expects valid=True and mode=1 for inference)
    test_vector = {
        'input_data': all_max_pos_input,
        'valid': True,
        'mode': 1,  # Inference mode
        'test_type': 'corner_case',
        'corner_value': all_max_pos_input[0]
    }
    
    print(f"\nTesting with input: {all_max_pos_input[0]} (all same)")
    print(f"Input length: {len(all_max_pos_input)}")
    print(f"Input type: {type(all_max_pos_input)}")
    print(f"Test vector: {test_vector}")
    
    # Check if weights are loaded
    print(f"Weights loaded: {golden_model.weights_loaded}")
    print(f"Golden model input size: {golden_model.input_size}")
    print(f"Golden model output size: {golden_model.output_size}")
    
    # Run golden model
    golden_outputs = golden_model(test_vector)
    print(f"Golden outputs type: {type(golden_outputs)}")
    print(f"Golden outputs: {golden_outputs}")
    
    golden_checkpoints = golden_model.get_all_checkpoints()
    print(f"Available checkpoints: {list(golden_checkpoints.keys())}")
    
    final_outputs = golden_checkpoints.get('final_outputs', {})
    print(f"Final outputs keys: {list(final_outputs.keys()) if final_outputs else 'None'}")
    
    output_data = final_outputs.get('output_data', torch.tensor([]))
    print(f"Output data shape: {output_data.shape}")
    print(f"Output data: {output_data}")
    
    # Also try to get from golden_outputs directly
    if isinstance(golden_outputs, dict) and 'output_data' in golden_outputs:
        output_data = golden_outputs['output_data']
        print(f"Using output from direct golden_outputs: {output_data}")
    
    if output_data.numel() == 0:
        print("❌ No output data found!")
        return False
    
    print(f"\n=== Golden Model Results ===")
    print("Golden Model vs Expected:")
    for i in range(len(all_max_pos_expected)):
        golden_val = output_data[i].item()
        expected_val = all_max_pos_expected[i]
        difference = abs(golden_val - expected_val)
        
        print(f"  Output[{i}]: Golden={golden_val:.6f}, Expected={expected_val:.6f}, Diff={difference:.6f}")
        
        if difference > 0.01:  # Tolerance
            print(f"    *** MISMATCH ***")
    
    # Check if we have exact match
    total_diff = sum(abs(output_data[i].item() - all_max_pos_expected[i]) for i in range(len(all_max_pos_expected)))
    print(f"\nTotal absolute difference: {total_diff:.6f}")
    
    if total_diff < 0.1:
        print("✅ Golden Model matches expected outputs!")
        return True
    else:
        print("❌ Golden Model does not match expected outputs")
        return False

def debug_weight_loading():
    """Debug weight loading process."""
    print("\n=== Debug Weight Loading Process ===")
    
    # Load test data
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    # Check weight format in test data
    weights_int = np.array(test_data['weights']['integer'])
    weights_float = np.array(test_data['weights']['float_equiv'])
    biases_int = np.array(test_data['biases']['integer'])
    biases_float = np.array(test_data['biases']['float_equiv'])
    
    print(f"Test data weights shape: {weights_int.shape}")
    print(f"Test data biases shape: {biases_int.shape}")
    
    # Show how weights should be arranged
    print(f"\nWeight arrangement:")
    print(f"  weights_int[input_idx, output_idx] -> weight from input_idx to output_idx")
    print(f"  For PyTorch Linear layer: weight[output_idx, input_idx]")
    
    # Check the transpose
    weights_transposed = weights_float.T  # Should be (output_size, input_size)
    print(f"Transposed shape: {weights_transposed.shape}")
    
    # Verify with manual calculation
    input_val = 127.99609375
    print(f"\nManual verification:")
    
    for i in range(min(3, len(biases_float))):  # Just first 3 outputs
        # Method 1: sum weights from original data
        weight_sum_1 = sum(weights_float[j, i] for j in range(weights_float.shape[0]))
        
        # Method 2: sum weights from transposed data  
        weight_sum_2 = sum(weights_transposed[i, j] for j in range(weights_transposed.shape[1]))
        
        result_1 = input_val * weight_sum_1 + biases_float[i]
        result_2 = input_val * weight_sum_2 + biases_float[i]
        expected = test_data['reference_outputs']['all_max_pos']['float_equiv'][i]
        
        print(f"  Output[{i}]:")
        print(f"    Method 1 (original): {result_1:.6f}")
        print(f"    Method 2 (transposed): {result_2:.6f}")
        print(f"    Expected: {expected:.6f}")
        print(f"    Match method 1: {abs(result_1 - expected) < 0.01}")
        print(f"    Match method 2: {abs(result_2 - expected) < 0.01}")

if __name__ == "__main__":
    debug_weight_loading()
    success = debug_with_test_weights()
    
    if success:
        print("\n🎉 Corner 3 debugging successful!")
        print("Golden Model now produces correct results for all_max_pos test case.")
    else:
        print("\n🔍 Further investigation needed...")