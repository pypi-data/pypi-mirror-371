#!/usr/bin/env python3
"""
Debug hardware directly by running a minimal CocoTB test.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.types import LogicArray
import json
import numpy as np

async def load_weights_and_biases(dut, weights, biases):
    """Load weights and biases into hardware."""
    # Set mode to weight loading
    dut.mode_i.value = 0
    dut.valid_i.value = 1
    await RisingEdge(dut.clk)
    
    # Load weights
    for i in range(100):  # INPUT_SIZE
        for j in range(10):  # OUTPUT_SIZE
            # Encode address: input_idx in upper 7 bits, output_idx in lower 3 bits
            addr = (i << 3) | j
            dut.weight_addr_i.value = addr
            dut.weight_data_i.value = int(weights[i, j])
            dut.weight_we_i.value = 1
            await RisingEdge(dut.clk)
    
    dut.weight_we_i.value = 0
    
    # Load biases  
    for j in range(10):  # OUTPUT_SIZE
        dut.bias_addr_i.value = j
        dut.bias_data_i.value = int(biases[j])
        dut.bias_we_i.value = 1
        await RisingEdge(dut.clk)
    
    dut.bias_we_i.value = 0
    await RisingEdge(dut.clk)

async def run_inference(dut, inputs):
    """Run inference and capture outputs."""
    # Set mode to inference
    dut.mode_i.value = 1
    dut.valid_i.value = 1
    
    # Set inputs
    for i in range(100):
        dut.input_data_i[i].value = int(inputs[i])
    
    await RisingEdge(dut.clk)
    dut.valid_i.value = 0
    
    # Wait for computation to complete
    timeout = 0
    while timeout < 10000:
        await RisingEdge(dut.clk)
        if dut.valid_o.value == 1:
            break
        timeout += 1
    
    if timeout >= 10000:
        cocotb.log.error("Timeout waiting for computation to complete")
        return None
    
    # Capture outputs
    outputs = []
    for i in range(10):
        val = int(dut.output_data_o[i].value)
        # Convert from unsigned to signed if necessary
        if val >= 32768:
            val -= 65536
        outputs.append(val)
    
    return outputs

@cocotb.test()
async def test_hardware_debug(dut):
    """Debug hardware with corner_3 test case."""
    cocotb.log.info("=== Hardware Debug Test ===")
    
    # Start clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start(start_high=False))
    
    # Reset
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Load test data
    with open('test_output/fc_layer_test_suite.json', 'r') as f:
        test_data = json.load(f)
    
    weights_int = np.array(test_data['weights']['integer'])
    biases_int = np.array(test_data['biases']['integer'])
    corner3_input_int = test_data['test_inputs']['all_max_pos']['integer']
    expected_outputs_int = test_data['reference_outputs']['all_max_pos']['integer']
    expected_outputs_float = test_data['reference_outputs']['all_max_pos']['float_equiv']
    
    cocotb.log.info(f"Loading weights: shape {weights_int.shape}")
    cocotb.log.info(f"Loading biases: shape {biases_int.shape}")
    
    # Load weights and biases
    await load_weights_and_biases(dut, weights_int, biases_int)
    cocotb.log.info("Weights and biases loaded")
    
    # Run corner_3 inference
    cocotb.log.info(f"Running inference with all inputs = {corner3_input_int[0]}")
    hw_outputs = await run_inference(dut, corner3_input_int)
    
    if hw_outputs is None:
        cocotb.log.error("Failed to get hardware outputs")
        return
    
    cocotb.log.info("=== Hardware vs Expected Comparison ===")
    for i in range(10):
        hw_int = hw_outputs[i]
        hw_float = hw_int / 256.0
        exp_int = expected_outputs_int[i]
        exp_float = expected_outputs_float[i]
        error = abs(hw_float - exp_float)
        
        cocotb.log.info(f"Output[{i}]:")
        cocotb.log.info(f"  Hardware: {hw_int} ({hw_float:.6f})")
        cocotb.log.info(f"  Expected: {exp_int} ({exp_float:.6f})")
        cocotb.log.info(f"  Error: {error:.6f}")
        
        if error > 0.01:
            cocotb.log.error(f"  -> MISMATCH!")
        else:
            cocotb.log.info(f"  -> OK")
    
    # Also check debug signals
    cocotb.log.info("=== Debug Signals ===")
    cocotb.log.info(f"Debug state: 0x{int(dut.debug_state_o.value):08X}")
    cocotb.log.info(f"Debug accumulator: {int(dut.debug_accumulator_o.value)}")
    cocotb.log.info(f"Debug addr counter: 0x{int(dut.debug_addr_counter_o.value):04X}")
    cocotb.log.info(f"Debug flags: 0x{int(dut.debug_flags_o.value):02X}")
    
    # Calculate expected vs actual totals
    hw_total = sum(hw_outputs)
    exp_total = sum(expected_outputs_int)
    cocotb.log.info(f"Total hardware outputs: {hw_total}")
    cocotb.log.info(f"Total expected outputs: {exp_total}")
    cocotb.log.info(f"Total difference: {hw_total - exp_total}")