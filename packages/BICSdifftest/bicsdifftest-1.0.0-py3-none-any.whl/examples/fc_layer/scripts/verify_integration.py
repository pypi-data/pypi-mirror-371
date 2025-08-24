#!/usr/bin/env python3
"""
Integration verification script for FC Layer differential testing.

This script performs comprehensive integration checks:
- Import verification for all components
- Golden model functionality tests  
- Test vector generation validation
- Configuration file validation
- Basic simulation setup tests
"""

import sys
import os
from pathlib import Path
import torch
import numpy as np
import yaml
import json

# Add framework to path
framework_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(framework_root))

def test_imports():
    """Test all critical imports."""
    print("Testing imports...")
    
    try:
        # Framework imports
        from testbench.base import DiffTestBase, TestSequence, TestVector
        print("  ✓ Framework base classes imported")
        
        from golden_model.models.fc_layer_model import FCLayerGoldenModel, FCLayerTestVectorGenerator
        print("  ✓ FC Layer golden model imported")
        
        from golden_model.base.utils import TensorComparator, ComparisonMode
        print("  ✓ Comparison utilities imported")
        
        # Test instantiation
        model = FCLayerGoldenModel(input_size=10, output_size=5)
        print("  ✓ Golden model instantiation successful")
        
        generator = FCLayerTestVectorGenerator(input_size=10, output_size=5)
        print("  ✓ Test vector generator instantiation successful")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_golden_model_functionality():
    """Test golden model basic functionality."""
    print("\\nTesting golden model functionality...")
    
    try:
        from golden_model.models.fc_layer_model import FCLayerGoldenModel
        
        # Create small model for testing
        model = FCLayerGoldenModel(input_size=8, output_size=4, data_width=16, frac_bits=8)
        
        # Test weight loading
        weights = torch.randn(8, 4) * 0.1
        biases = torch.randn(4) * 0.01
        model.load_weights_from_tensor(weights, biases)
        print("  ✓ Weight loading successful")
        
        # Test inference
        input_data = torch.randn(8) * 0.5
        inputs = {
            'mode': 1,
            'valid': True,
            'input_data': input_data.tolist()
        }
        
        outputs = model(inputs)
        print("  ✓ Inference computation successful")
        
        # Validate output structure
        expected_keys = ['output_data', 'valid', 'ready', 'debug_state', 'debug_accumulator', 'debug_addr_counter', 'debug_flags']
        for key in expected_keys:
            if key not in outputs:
                raise ValueError(f"Missing output key: {key}")
        print("  ✓ Output structure validation passed")
        
        # Validate output shapes
        if outputs['output_data'].shape != (4,):
            raise ValueError(f"Wrong output shape: {outputs['output_data'].shape}")
        print("  ✓ Output shape validation passed")
        
        # Test checkpoints
        checkpoints = model.get_all_checkpoints()
        if 'inputs' not in checkpoints or 'final_outputs' not in checkpoints:
            raise ValueError("Missing critical checkpoints")
        print("  ✓ Checkpoint system working")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Golden model test failed: {e}")
        return False

def test_vector_generation():
    """Test vector generation functionality."""
    print("\\nTesting test vector generation...")
    
    try:
        from golden_model.models.fc_layer_model import FCLayerTestVectorGenerator
        
        generator = FCLayerTestVectorGenerator(input_size=8, output_size=4)
        
        # Test weight loading vectors
        weight_vectors, weights, biases = generator.generate_weight_loading_vectors()
        expected_count = 8 * 4 + 4  # weights + biases  
        if len(weight_vectors) != expected_count:
            raise ValueError(f"Wrong number of weight vectors: {len(weight_vectors)} vs {expected_count}")
        print("  ✓ Weight loading vector generation successful")
        
        # Test inference vectors
        inference_vectors = generator.generate_inference_vectors(count=10)
        if len(inference_vectors) != 10:
            raise ValueError(f"Wrong number of inference vectors: {len(inference_vectors)}")
        print("  ✓ Inference vector generation successful")
        
        # Test corner case vectors
        corner_vectors = generator.generate_corner_case_vectors()
        if len(corner_vectors) < 5:  # Should have at least several corner cases
            raise ValueError(f"Too few corner case vectors: {len(corner_vectors)}")
        print("  ✓ Corner case vector generation successful")
        
        # Validate vector structure
        sample_vector = inference_vectors[0]
        required_keys = ['mode', 'valid', 'input_data', 'test_type']
        for key in required_keys:
            if key not in sample_vector:
                raise ValueError(f"Missing vector key: {key}")
        print("  ✓ Vector structure validation passed")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Vector generation test failed: {e}")
        return False

def test_configuration_files():
    """Test configuration file validity."""
    print("\\nTesting configuration files...")
    
    try:
        # Test YAML configuration
        config_path = Path(__file__).parent.parent / "config" / "fc_layer_test.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        required_sections = ['name', 'top_module', 'golden_model_class', 'verilator', 'cocotb', 'fc_layer']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing config section: {section}")
        
        print("  ✓ YAML configuration file valid")
        
        # Validate FC layer parameters
        fc_config = config['fc_layer']
        if fc_config['input_size'] != 100 or fc_config['output_size'] != 10:
            raise ValueError("FC layer dimensions don't match expectations")
        
        print("  ✓ FC layer configuration parameters valid")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Configuration test failed: {e}")
        return False

def test_testbench_structure():
    """Test testbench file structure and syntax."""
    print("\\nTesting testbench structure...")
    
    try:
        # Import and check testbench structure
        testbench_path = Path(__file__).parent.parent / "testbench" / "test_fc_layer.py"
        
        # Check file exists and is readable
        if not testbench_path.exists():
            raise FileNotFoundError("Testbench file not found")
        
        # Attempt to compile (syntax check)
        import py_compile
        py_compile.compile(testbench_path, doraise=True)
        print("  ✓ Testbench syntax valid")
        
        # Check for required test functions by parsing file content
        with open(testbench_path, 'r') as f:
            content = f.read()
        
        required_tests = [
            'test_fc_layer_weight_loading',
            'test_fc_layer_inference', 
            'test_fc_layer_corner_cases',
            'test_fc_layer_comprehensive'
        ]
        
        for test_func in required_tests:
            if test_func not in content:
                raise ValueError(f"Missing test function: {test_func}")
        
        print("  ✓ All required test functions present")
        
        # Check for FCLayerDiffTest class
        if 'class FCLayerDiffTest(DiffTestBase)' not in content:
            raise ValueError("FCLayerDiffTest class not found or malformed")
        
        print("  ✓ FCLayerDiffTest class structure valid")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Testbench structure test failed: {e}")
        return False

def test_end_to_end_simulation():
    """Test a simple end-to-end simulation setup."""
    print("\\nTesting end-to-end simulation setup...")
    
    try:
        from golden_model.models.fc_layer_model import FCLayerGoldenModel
        
        # Create a minimal test scenario
        model = FCLayerGoldenModel(input_size=4, output_size=2)
        
        # Load simple weights
        weights = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6], [0.7, 0.8]])
        biases = torch.tensor([0.1, 0.2])
        model.load_weights_from_tensor(weights, biases)
        
        # Run inference
        test_input = [1.0, -1.0, 0.5, -0.5]
        inputs = {
            'mode': 1,
            'valid': True,
            'input_data': test_input
        }
        
        outputs = model(inputs)
        
        # Verify output is reasonable
        output_data = outputs['output_data']
        if not torch.is_tensor(output_data) or output_data.shape != (2,):
            raise ValueError("Invalid output format")
        
        # Manual calculation for verification
        expected = np.dot(test_input, weights.numpy()) + biases.numpy()
        
        # Allow for some fixed-point quantization error
        error = np.abs(output_data.numpy() - expected)
        if np.max(error) > 0.1:  # Generous tolerance for this test
            raise ValueError(f"Output error too large: {np.max(error)}")
        
        print("  ✓ End-to-end computation verification passed")
        
        # Test checkpoint system
        checkpoints = model.get_all_checkpoints()
        if len(checkpoints) < 3:  # Should have input, intermediate, and output checkpoints
            raise ValueError("Insufficient checkpoints generated")
        
        print("  ✓ Checkpoint system functioning")
        
        return True
        
    except Exception as e:
        print(f"  ✗ End-to-end test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("FC Layer Integration Verification")
    print("=" * 40)
    
    tests = [
        ("Import Tests", test_imports),
        ("Golden Model Tests", test_golden_model_functionality),
        ("Vector Generation Tests", test_vector_generation),
        ("Configuration Tests", test_configuration_files),
        ("Testbench Structure Tests", test_testbench_structure),
        ("End-to-End Simulation Tests", test_end_to_end_simulation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n{test_name}:")
        if test_func():
            passed += 1
    
    print("\\n" + "=" * 40)
    print(f"Integration Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All integration tests PASSED!")
        print("\\nThe FC Layer differential testing setup is ready for use.")
        print("\\nNext steps:")
        print("  1. cd examples/fc_layer")
        print("  2. make test_weight_loading  # Test individual components")
        print("  3. make test_comprehensive   # Run full test suite")
        return 0
    else:
        print("✗ Some integration tests FAILED!")
        print("Please address the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())