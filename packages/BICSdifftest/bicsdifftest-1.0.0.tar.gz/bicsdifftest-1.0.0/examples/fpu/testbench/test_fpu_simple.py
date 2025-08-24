"""
Simple CocoTB testbench for FPU differential testing.

This testbench demonstrates a simplified approach for testing combinational logic
without relying on the full framework that assumes clocked designs.
"""

import cocotb
from cocotb.triggers import Timer
import sys
import os
from pathlib import Path
import torch
import numpy as np

# Add framework to Python path
framework_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(framework_root))

# Framework imports
from golden_model.models import FPUGoldenModel, FPUTestVectorGenerator
from golden_model.base.utils import TensorComparator, ComparisonMode


@cocotb.test()
async def test_fpu_simple_case(dut):
    """Test FPU with a simple case: max(100, 200) = 200."""
    cocotb.log.info("=== FPU Simple Test: max(100, 200) ===")
    
    # Create golden model
    golden_model = FPUGoldenModel(data_width=32)
    
    # Test case
    a_val = 100
    b_val = 200
    expected_result = 200
    
    # Apply inputs to DUT
    dut.a.value = a_val
    dut.b.value = b_val
    
    # Wait for combinational logic to settle
    await Timer(100, units='ns')
    
    # Capture DUT output
    dut_result = int(dut.result.value)
    
    # Run golden model
    golden_inputs = {'a': a_val, 'b': b_val}
    golden_outputs = golden_model(golden_inputs)
    golden_result = golden_outputs['result'].item()
    
    # Compare results
    cocotb.log.info(f"Inputs: a={a_val}, b={b_val}")
    cocotb.log.info(f"DUT result: {dut_result}")
    cocotb.log.info(f"Golden result: {golden_result}")
    cocotb.log.info(f"Expected: {expected_result}")
    
    # Check correctness
    assert dut_result == golden_result == expected_result, \
        f"Mismatch: DUT={dut_result}, Golden={golden_result}, Expected={expected_result}"
    
    cocotb.log.info("✅ Simple test PASSED!")


@cocotb.test()
async def test_fpu_corner_cases(dut):
    """Test FPU with corner cases."""
    cocotb.log.info("=== FPU Corner Cases Test ===")
    
    # Create golden model and test generator
    golden_model = FPUGoldenModel(data_width=32)
    generator = FPUTestVectorGenerator(data_width=32)
    
    # Generate corner case test vectors
    corner_vectors = generator.generate_corner_case_vectors()
    
    passed_tests = 0
    total_tests = len(corner_vectors)
    
    for i, vector in enumerate(corner_vectors):
        test_id = vector['test_id']
        a_val = vector['a']
        b_val = vector['b']
        
        cocotb.log.info(f"Running test {i+1}/{total_tests}: {test_id}")
        
        # Apply inputs to DUT
        dut.a.value = a_val
        dut.b.value = b_val
        
        # Wait for combinational logic to settle
        await Timer(100, units='ns')
        
        # Capture DUT output
        dut_result = int(dut.result.value)
        
        # Run golden model
        golden_inputs = {'a': a_val, 'b': b_val}
        golden_outputs = golden_model(golden_inputs)
        golden_result = golden_outputs['result'].item()
        
        # Check correctness
        if dut_result == golden_result:
            passed_tests += 1
            cocotb.log.info(f"  ✅ {test_id}: max({a_val}, {b_val}) = {dut_result}")
        else:
            cocotb.log.error(f"  ❌ {test_id}: DUT={dut_result}, Golden={golden_result}")
    
    cocotb.log.info(f"Corner cases test results: {passed_tests}/{total_tests} passed")
    assert passed_tests == total_tests, f"Corner cases test failed: {passed_tests}/{total_tests} passed"


@cocotb.test()
async def test_fpu_random_cases(dut):
    """Test FPU with random test cases."""
    cocotb.log.info("=== FPU Random Test Cases ===")
    
    # Create golden model and test generator
    golden_model = FPUGoldenModel(data_width=32)
    generator = FPUTestVectorGenerator(data_width=32)
    
    # Generate random test vectors
    random_vectors = generator.generate_random_vectors(count=10, seed=42)
    
    passed_tests = 0
    total_tests = len(random_vectors)
    
    for i, vector in enumerate(random_vectors):
        test_id = vector['test_id']
        a_val = vector['a']
        b_val = vector['b']
        
        cocotb.log.info(f"Running test {i+1}/{total_tests}: {test_id}")
        
        # Apply inputs to DUT
        dut.a.value = a_val
        dut.b.value = b_val
        
        # Wait for combinational logic to settle
        await Timer(100, units='ns')
        
        # Capture DUT output
        dut_result = int(dut.result.value)
        
        # Run golden model
        golden_inputs = {'a': a_val, 'b': b_val}
        golden_outputs = golden_model(golden_inputs)
        golden_result = golden_outputs['result'].item()
        
        # Check correctness
        if dut_result == golden_result:
            passed_tests += 1
            cocotb.log.info(f"  ✅ {test_id}: max({a_val}, {b_val}) = {dut_result}")
        else:
            cocotb.log.error(f"  ❌ {test_id}: DUT={dut_result}, Golden={golden_result}")
    
    cocotb.log.info(f"Random test results: {passed_tests}/{total_tests} passed")
    assert passed_tests == total_tests, f"Random test failed: {passed_tests}/{total_tests} passed"


@cocotb.test()
async def test_fpu_comprehensive(dut):
    """Comprehensive FPU test with all test cases."""
    cocotb.log.info("=== FPU Comprehensive Test ===")
    
    # Create golden model and test generator
    golden_model = FPUGoldenModel(data_width=32)
    generator = FPUTestVectorGenerator(data_width=32)
    
    # Generate all test vectors
    all_vectors = generator.generate_all_vectors(random_count=10, seed=42)
    
    passed_tests = 0
    total_tests = len(all_vectors)
    failed_tests = []
    
    for i, vector in enumerate(all_vectors):
        test_id = vector['test_id']
        test_type = vector['test_type']
        a_val = vector['a']
        b_val = vector['b']
        
        # Apply inputs to DUT
        dut.a.value = a_val
        dut.b.value = b_val
        
        # Wait for combinational logic to settle
        await Timer(100, units='ns')
        
        # Capture DUT output
        dut_result = int(dut.result.value)
        
        # Run golden model
        golden_inputs = {'a': a_val, 'b': b_val}
        golden_outputs = golden_model(golden_inputs)
        golden_result = golden_outputs['result'].item()
        
        # Check correctness
        if dut_result == golden_result:
            passed_tests += 1
            if i % 5 == 0:  # Log every 5th test to avoid spam
                cocotb.log.info(f"  Test {i+1}/{total_tests}: {test_id} ({test_type}) ✅")
        else:
            failed_tests.append((test_id, test_type, a_val, b_val, dut_result, golden_result))
            cocotb.log.error(f"  ❌ {test_id} ({test_type}): DUT={dut_result}, Golden={golden_result}")
    
    # Summary
    cocotb.log.info(f"=== Test Summary ===")
    cocotb.log.info(f"Total tests: {total_tests}")
    cocotb.log.info(f"Passed: {passed_tests}")
    cocotb.log.info(f"Failed: {len(failed_tests)}")
    cocotb.log.info(f"Pass rate: {passed_tests/total_tests*100:.1f}%")
    
    if failed_tests:
        cocotb.log.info("Failed tests:")
        for test_id, test_type, a_val, b_val, dut_result, golden_result in failed_tests[:5]:
            cocotb.log.info(f"  {test_id} ({test_type}): max({a_val}, {b_val}) -> DUT={dut_result}, Golden={golden_result}")
    
    # Generate simple report
    report_data = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': len(failed_tests),
        'pass_rate': passed_tests / total_tests * 100,
        'test_type_breakdown': {}
    }
    
    # Count by test type
    for vector in all_vectors:
        test_type = vector['test_type']
        if test_type not in report_data['test_type_breakdown']:
            report_data['test_type_breakdown'][test_type] = {'total': 0, 'passed': 0}
        report_data['test_type_breakdown'][test_type]['total'] += 1
    
    for test_id, test_type, _, _, _, _ in failed_tests:
        if test_type in report_data['test_type_breakdown']:
            # This was a failed test, so passed count is total - failed for this type
            pass
    
    # Calculate passed for each type (total - failed for that type)
    for vector in all_vectors:
        test_type = vector['test_type']
        test_id = vector['test_id']
        if not any(test_id == failed[0] for failed in failed_tests):
            report_data['test_type_breakdown'][test_type]['passed'] += 1
    
    cocotb.log.info("Test breakdown by type:")
    for test_type, stats in report_data['test_type_breakdown'].items():
        cocotb.log.info(f"  {test_type}: {stats['passed']}/{stats['total']} passed")
    
    assert passed_tests == total_tests, f"Comprehensive test failed: {passed_tests}/{total_tests} passed"
    cocotb.log.info("🎉 All tests PASSED!")