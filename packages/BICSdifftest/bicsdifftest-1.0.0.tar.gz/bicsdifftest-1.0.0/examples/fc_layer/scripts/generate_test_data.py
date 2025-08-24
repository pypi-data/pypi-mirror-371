#!/usr/bin/env python3
"""
Test data generation script for FC Layer verification.

This script generates comprehensive test datasets including:
- Pre-trained weight matrices
- Systematic input patterns  
- Expected outputs for validation
- Edge case scenarios
"""

import numpy as np
import torch
import pickle
import json
from pathlib import Path
import argparse

def generate_test_weights(input_size=100, output_size=10, seed=42):
    """
    Generate realistic weight matrices and biases.
    
    Args:
        input_size: Number of input neurons
        output_size: Number of output neurons
        seed: Random seed for reproducibility
        
    Returns:
        weights: (input_size, output_size) weight matrix
        biases: (output_size,) bias vector
    """
    np.random.seed(seed)
    
    # Xavier/Glorot initialization for stable gradients
    xavier_std = np.sqrt(2.0 / (input_size + output_size))
    
    weights = np.random.normal(0, xavier_std, (input_size, output_size))
    biases = np.random.normal(0, 0.01, output_size)  # Small bias initialization
    
    # Ensure values are within reasonable fixed-point range
    # For Q8.8 format: range is approximately [-128, 127.996]
    max_weight = 10.0  # Conservative limit for Q8.8
    weights = np.clip(weights, -max_weight, max_weight)
    biases = np.clip(biases, -max_weight, max_weight)
    
    return weights, biases

def generate_systematic_inputs(input_size=100, data_width=16, frac_bits=8):
    """
    Generate systematic test input patterns.
    
    Returns:
        Dictionary with various input pattern categories
    """
    max_val = (1 << (data_width - 1)) - 1
    min_val = -(1 << (data_width - 1))
    frac_scale = 1 << frac_bits
    
    # Convert to fixed-point range
    max_fp = float(max_val) / frac_scale
    min_fp = float(min_val) / frac_scale
    
    test_inputs = {}
    
    # 1. All zeros
    test_inputs['all_zeros'] = np.zeros(input_size)
    
    # 2. All maximum positive
    test_inputs['all_max_pos'] = np.full(input_size, max_fp)
    
    # 3. All maximum negative  
    test_inputs['all_max_neg'] = np.full(input_size, min_fp)
    
    # 4. Alternating pattern
    alternating = np.zeros(input_size)
    alternating[::2] = max_fp
    alternating[1::2] = min_fp
    test_inputs['alternating'] = alternating
    
    # 5. Single hot inputs (one-hot encoding style)
    for i in range(min(10, input_size)):  # First 10 inputs
        single_hot = np.zeros(input_size)
        single_hot[i] = max_fp
        test_inputs[f'single_hot_{i}'] = single_hot
    
    # 6. Gradient patterns
    gradient = np.linspace(min_fp, max_fp, input_size)
    test_inputs['gradient_ascending'] = gradient
    test_inputs['gradient_descending'] = gradient[::-1]
    
    # 7. Random but controlled patterns
    np.random.seed(123)
    test_inputs['random_normal'] = np.clip(
        np.random.normal(0, 1, input_size), min_fp, max_fp
    )
    test_inputs['random_uniform'] = np.random.uniform(min_fp, max_fp, input_size)
    
    # 8. Sparse patterns (mostly zeros with few non-zeros)
    sparse_10 = np.zeros(input_size)
    sparse_indices = np.random.choice(input_size, 10, replace=False)
    sparse_10[sparse_indices] = np.random.uniform(min_fp, max_fp, 10)
    test_inputs['sparse_10_percent'] = sparse_10
    
    return test_inputs

def compute_reference_outputs(weights, biases, inputs):
    """
    Compute reference outputs using floating-point arithmetic.
    
    Args:
        weights: Weight matrix (input_size, output_size)
        biases: Bias vector (output_size,)  
        inputs: Dictionary of input patterns
        
    Returns:
        Dictionary of reference outputs for each input pattern
    """
    reference_outputs = {}
    
    for pattern_name, input_data in inputs.items():
        # Standard linear layer computation: output = input @ weights + biases
        output = np.dot(input_data, weights) + biases
        reference_outputs[pattern_name] = output
    
    return reference_outputs

def compute_fixed_point_reference_outputs(weights, biases, inputs, data_width=16, frac_bits=8):
    """
    Compute reference outputs using bit-exact fixed-point arithmetic.
    This matches the Golden Model and hardware implementation exactly.
    
    Args:
        weights: Weight matrix (input_size, output_size) - already quantized
        biases: Bias vector (output_size,) - already quantized
        inputs: Dictionary of input patterns - already quantized
        data_width: Total bit width
        frac_bits: Number of fractional bits
        
    Returns:
        Dictionary of fixed-point reference outputs for each input pattern
    """
    frac_scale = 1 << frac_bits  # 256 for Q8.8
    max_int = (1 << (data_width - 1)) - 1  # 32767
    min_int = -(1 << (data_width - 1))     # -32768
    
    def fixed_point_multiply(a_float, b_float):
        """Fixed-point multiplication matching Golden Model."""
        # Convert to integers
        a_int = int(a_float * frac_scale)
        b_int = int(b_float * frac_scale) 
        
        # Saturate inputs
        a_int = max(min_int, min(max_int, a_int))
        b_int = max(min_int, min(max_int, b_int))
        
        # Multiply and scale
        mult_result = (a_int * b_int) >> frac_bits
        
        # Saturate result
        mult_result = max(min_int, min(max_int, mult_result))
        
        # Convert back to float
        return float(mult_result) / frac_scale
    
    def saturate_output(value):
        """Saturate final output to data width."""
        value_int = int(value * frac_scale)
        value_int = max(min_int, min(max_int, value_int))
        return float(value_int) / frac_scale
    
    reference_outputs = {}
    
    for pattern_name, input_data in inputs.items():
        input_size = len(input_data)
        output_size = len(biases)
        output = np.zeros(output_size)
        
        # For each output neuron
        for j in range(output_size):
            # Initialize with bias
            accumulator = biases[j]
            
            # MAC operations
            for i in range(input_size):
                mult_result = fixed_point_multiply(input_data[i], weights[i, j])
                accumulator += mult_result
            
            # Saturate final result
            output[j] = saturate_output(accumulator)
        
        reference_outputs[pattern_name] = output
    
    return reference_outputs

def quantize_for_hardware(values, data_width=16, frac_bits=8):
    """
    Quantize floating-point values to fixed-point representation.
    
    Args:
        values: Floating-point values to quantize
        data_width: Total bit width
        frac_bits: Number of fractional bits
        
    Returns:
        Quantized values as integers and as floating-point equivalents
    """
    frac_scale = 1 << frac_bits
    max_int = (1 << (data_width - 1)) - 1
    min_int = -(1 << (data_width - 1))
    
    # Scale to integer
    scaled = np.round(values * frac_scale)
    
    # Saturate to range
    saturated = np.clip(scaled, min_int, max_int).astype(int)
    
    # Convert back to floating-point for comparison
    quantized_float = saturated.astype(float) / frac_scale
    
    return saturated, quantized_float

def generate_comprehensive_test_suite(output_dir="test_data", input_size=100, output_size=10):
    """
    Generate comprehensive test suite for FC Layer.
    
    Args:
        output_dir: Directory to save test data
        input_size: Number of input neurons
        output_size: Number of output neurons
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating test suite for {input_size}x{output_size} FC Layer...")
    
    # 1. Generate weight matrices
    print("Generating weights and biases...")
    weights_float, biases_float = generate_test_weights(input_size, output_size)
    
    # Quantize weights and biases for hardware
    weights_int, weights_quant = quantize_for_hardware(weights_float)
    biases_int, biases_quant = quantize_for_hardware(biases_float)
    
    # 2. Generate test inputs
    print("Generating test input patterns...")
    test_inputs = generate_systematic_inputs(input_size)
    
    # 3. Compute reference outputs (using quantized weights for accuracy)
    print("Computing reference outputs...")
    reference_outputs_float = compute_reference_outputs(weights_float, biases_float, test_inputs)
    
    # First quantize test inputs for fixed-point computation
    quantized_test_inputs = {}
    for pattern_name, input_data in test_inputs.items():
        input_int, input_quant = quantize_for_hardware(input_data)
        quantized_test_inputs[pattern_name] = input_quant
    
    # Compute bit-exact fixed-point reference outputs
    reference_outputs_fixed_point = compute_fixed_point_reference_outputs(
        weights_quant, biases_quant, quantized_test_inputs
    )
    
    # 4. Prepare quantized inputs for hardware
    quantized_inputs = {}
    for pattern_name, input_data in test_inputs.items():
        input_int, input_quant = quantize_for_hardware(input_data)
        quantized_inputs[pattern_name] = {
            'integer': input_int.tolist(),
            'float_equiv': input_quant.tolist(),
            'original_float': input_data.tolist()
        }
    
    # 5. Prepare quantized outputs (use fixed-point computed outputs)
    quantized_outputs = {}
    for pattern_name, output_data in reference_outputs_fixed_point.items():
        # Fixed-point outputs are already quantized, but convert to integer representation
        output_int, output_quant = quantize_for_hardware(output_data)
        quantized_outputs[pattern_name] = {
            'integer': output_int.tolist(),
            'float_equiv': output_quant.tolist(),
            'original_float': reference_outputs_float[pattern_name].tolist()  # Keep original float for comparison
        }
    
    # 6. Save all test data
    test_data = {
        'metadata': {
            'input_size': input_size,
            'output_size': output_size,
            'data_width': 16,
            'frac_bits': 8,
            'num_test_patterns': len(test_inputs),
            'generation_seed': 42
        },
        'weights': {
            'integer': weights_int.tolist(),
            'float_equiv': weights_quant.tolist(), 
            'original_float': weights_float.tolist()
        },
        'biases': {
            'integer': biases_int.tolist(),
            'float_equiv': biases_quant.tolist(),
            'original_float': biases_float.tolist()
        },
        'test_inputs': quantized_inputs,
        'reference_outputs': quantized_outputs
    }
    
    # Save as JSON for easy parsing
    json_file = output_path / "fc_layer_test_suite.json"
    with open(json_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    print(f"Test suite saved to: {json_file}")
    
    # Also save as pickle for Python convenience  
    pickle_file = output_path / "fc_layer_test_suite.pkl"
    with open(pickle_file, 'wb') as f:
        pickle.dump(test_data, f)
    print(f"Test suite also saved as: {pickle_file}")
    
    # 7. Generate summary report
    report_file = output_path / "test_suite_report.txt"
    with open(report_file, 'w') as f:
        f.write("FC Layer Test Suite Generation Report\\n")
        f.write("=" * 40 + "\\n\\n")
        f.write(f"Configuration:\\n")
        f.write(f"  - Input size: {input_size}\\n")
        f.write(f"  - Output size: {output_size}\\n")
        f.write(f"  - Data width: 16 bits (Q8.8 fixed-point)\\n")
        f.write(f"  - Weight range: [{weights_float.min():.4f}, {weights_float.max():.4f}]\\n")
        f.write(f"  - Bias range: [{biases_float.min():.4f}, {biases_float.max():.4f}]\\n\\n")
        
        f.write(f"Generated Test Patterns:\\n")
        for pattern_name, _ in test_inputs.items():
            f.write(f"  - {pattern_name}\\n")
        
        f.write(f"\\nQuantization Analysis:\\n")
        weight_error = np.mean(np.abs(weights_float - weights_quant))
        bias_error = np.mean(np.abs(biases_float - biases_quant))
        f.write(f"  - Average weight quantization error: {weight_error:.6f}\\n")
        f.write(f"  - Average bias quantization error: {bias_error:.6f}\\n")
        
        f.write(f"\\nOutput Analysis:\\n")
        for pattern_name in list(reference_outputs_float.keys())[:5]:  # First 5 patterns
            float_out = reference_outputs_float[pattern_name]
            fixed_point_out = reference_outputs_fixed_point[pattern_name]
            error = np.mean(np.abs(float_out - fixed_point_out))
            f.write(f"  - {pattern_name}: float vs fixed-point avg error = {error:.6f}\\n")
    
    print(f"Generation report saved to: {report_file}")
    print("\\nTest suite generation completed successfully!")
    
    return test_data

def main():
    parser = argparse.ArgumentParser(description="Generate FC Layer test data")
    parser.add_argument('--input-size', type=int, default=100, help='Input layer size')
    parser.add_argument('--output-size', type=int, default=10, help='Output layer size') 
    parser.add_argument('--output-dir', type=str, default='test_data', help='Output directory')
    
    args = parser.parse_args()
    
    generate_comprehensive_test_suite(
        output_dir=args.output_dir,
        input_size=args.input_size,
        output_size=args.output_size
    )

if __name__ == "__main__":
    main()