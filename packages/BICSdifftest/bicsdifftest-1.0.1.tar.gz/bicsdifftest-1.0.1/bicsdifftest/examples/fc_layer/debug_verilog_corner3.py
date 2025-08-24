#!/usr/bin/env python3
"""
Debug Verilog corner_3 issue by simulating hardware arithmetic exactly.
"""

import json
import numpy as np

def simulate_verilog_computation():
    """Simulate the exact Verilog computation for corner_3."""
    print("=== Verilog Hardware Simulation for corner_3 ===")
    
    # Load test data
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    weights_int = np.array(test_data['weights']['integer'])
    biases_int = np.array(test_data['biases']['integer'])
    input_int = test_data['test_inputs']['all_max_pos']['integer']
    expected_int = test_data['reference_outputs']['all_max_pos']['integer']
    expected_float = test_data['reference_outputs']['all_max_pos']['float_equiv']
    
    print(f"Input (integer): {input_int[0]} (all same)")
    print(f"Input (16-bit hex): 0x{input_int[0]:04X}")
    
    # Constants from Verilog
    DATA_WIDTH = 16
    WEIGHT_WIDTH = 16
    FRAC_BITS = 8
    ADDR_WIDTH = 10
    INPUT_SIZE = 100
    OUTPUT_SIZE = 10
    
    # Simulate hardware computation for each output
    for output_idx in range(OUTPUT_SIZE):
        print(f"\n--- Output[{output_idx}] Simulation ---")
        
        # Initialize accumulator with bias (sign-extended to wider width)
        bias_val = biases_int[output_idx]
        if bias_val < 0:
            bias_val += (1 << 16)  # Convert to unsigned representation
        
        # Sign-extend bias to accumulator width
        acc_width = DATA_WIDTH + WEIGHT_WIDTH + ADDR_WIDTH  # 16+16+10=42 bits
        if biases_int[output_idx] < 0:
            # Negative bias - sign extend with 1s
            accumulator = (((1 << (acc_width - DATA_WIDTH)) - 1) << DATA_WIDTH) | bias_val
        else:
            # Positive bias - sign extend with 0s  
            accumulator = bias_val
        
        print(f"Initial bias: {biases_int[output_idx]} -> accumulator: 0x{accumulator:011X}")
        
        # MAC computation
        for input_idx in range(min(5, INPUT_SIZE)):  # Show first 5 for debugging
            input_val = input_int[input_idx]
            weight_val = weights_int[input_idx, output_idx]
            
            # Convert to signed if negative (two's complement)
            if input_val >= (1 << (DATA_WIDTH - 1)):
                input_signed = input_val - (1 << DATA_WIDTH)
            else:
                input_signed = input_val
                
            if weight_val >= (1 << (WEIGHT_WIDTH - 1)):
                weight_signed = weight_val - (1 << WEIGHT_WIDTH)
            else:
                weight_signed = weight_val
            
            # Full precision multiply (32-bit result)
            mult_result_full = input_signed * weight_signed
            print(f"  MAC {input_idx}: {input_signed} * {weight_signed} = {mult_result_full}")
            
            # Scale down by FRAC_BITS (this is the key operation!)
            # Verilog: mult_result = mult_result_full[DATA_WIDTH+FRAC_BITS-1:FRAC_BITS];
            # This should be: mult_result_full[23:8] for 16-bit result
            if mult_result_full >= 0:
                mult_scaled = mult_result_full >> FRAC_BITS
            else:
                # Arithmetic right shift for negative numbers
                mult_scaled = -((-mult_result_full) >> FRAC_BITS)
                if (-mult_result_full) & ((1 << FRAC_BITS) - 1):  # Check if there were fractional bits
                    mult_scaled -= 1  # Round towards negative infinity
            
            print(f"    Scaled: {mult_scaled}")
            
            # Add to accumulator
            accumulator += mult_scaled
        
        # Full MAC computation (all 100 inputs)
        accumulator_full = biases_int[output_idx]
        for input_idx in range(INPUT_SIZE):
            input_val = input_int[input_idx]  
            weight_val = weights_int[input_idx, output_idx]
            
            # Convert to signed
            if input_val >= (1 << (DATA_WIDTH - 1)):
                input_signed = input_val - (1 << DATA_WIDTH)
            else:
                input_signed = input_val
                
            if weight_val >= (1 << (WEIGHT_WIDTH - 1)):
                weight_signed = weight_val - (1 << WEIGHT_WIDTH)
            else:
                weight_signed = weight_val
            
            # Full multiply and scale
            mult_result_full = input_signed * weight_signed
            mult_scaled = mult_result_full >> FRAC_BITS  # Arithmetic right shift
            accumulator_full += mult_scaled
        
        print(f"Final accumulator: {accumulator_full}")
        
        # Saturation logic (Verilog lines 229-245)
        # Check if result fits in 16 bits
        if accumulator_full > 32767:
            final_result = 32767  # Saturate to max positive
            print(f"  -> OVERFLOW: saturated to 32767")
        elif accumulator_full < -32768:
            final_result = -32768  # Saturate to max negative
            print(f"  -> UNDERFLOW: saturated to -32768")
        else:
            final_result = accumulator_full
            print(f"  -> No saturation needed")
        
        # Convert to float equivalent
        final_float = final_result / 256.0
        
        print(f"Final result (int): {final_result}")
        print(f"Final result (float): {final_float:.6f}")
        print(f"Expected (int): {expected_int[output_idx]}")
        print(f"Expected (float): {expected_float[output_idx]:.6f}")
        print(f"Error: {abs(final_float - expected_float[output_idx]):.6f}")

def analyze_potential_verilog_bugs():
    """Analyze potential bugs in the Verilog implementation."""
    print(f"\n=== Potential Verilog Bugs ===")
    
    issues = [
        "1. Bit slice in mult_result: [DATA_WIDTH+FRAC_BITS-1:FRAC_BITS] = [23:8]",
        "   - This gives a 16-bit result, but might not handle sign extension correctly",
        "2. Accumulator sign extension: bias sign extension might be wrong",
        "3. Saturation logic: The overflow check might be incorrect",
        "4. Arithmetic right shift: >> might not work correctly for signed values",
        "5. Two's complement conversion: The hardware might use different representation"
    ]
    
    for issue in issues:
        print(issue)
    
    print(f"\nMost likely issue: Fixed-point arithmetic implementation mismatch")
    print(f"Hardware probably outputs different values than Golden Model expects")
    
    # Show the bit manipulation details
    print(f"\n=== Bit Manipulation Analysis ===")
    print(f"mult_result_full is 32 bits (DATA_WIDTH + WEIGHT_WIDTH)")
    print(f"mult_result should extract bits [23:8] to get 16-bit scaled result")
    print(f"But for negative numbers, this might not preserve sign correctly")
    
    # Example with corner_3 values
    input_val = 32767  # 0x7FFF
    weight_example = 11  # Small positive weight
    mult_full = input_val * weight_example  # 360337
    mult_scaled = mult_full >> 8  # 1407
    
    print(f"\nExample: {input_val} * {weight_example} = {mult_full}")
    print(f"Scaled: {mult_full} >> 8 = {mult_scaled}")
    print(f"As 16-bit: {mult_scaled & 0xFFFF}")

if __name__ == "__main__":
    simulate_verilog_computation()
    analyze_potential_verilog_bugs()