#!/usr/bin/env python3
"""
Generate test data for FPU differential testing.

This script generates comprehensive test vectors and reference outputs
for the FPU design, saving them in a format suitable for verification.
"""

import sys
import os
import json
import pickle
from pathlib import Path
import argparse
import logging

# Add framework to Python path
framework_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(framework_root))

from golden_model.models import FPUGoldenModel, FPUTestVectorGenerator
import torch
import numpy as np


def setup_logging(log_level='INFO'):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def generate_test_suite(data_width=32, random_count=20, seed=42):
    """
    Generate comprehensive test suite for FPU.
    
    Args:
        data_width: Data width in bits
        random_count: Number of random test vectors
        seed: Random seed for reproducibility
    
    Returns:
        Dictionary containing all test data
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Generating FPU test suite with {data_width}-bit data width")
    
    # Initialize models and generators
    golden_model = FPUGoldenModel(data_width=data_width)
    generator = FPUTestVectorGenerator(data_width=data_width)
    
    # Generate all test vectors
    test_vectors = generator.generate_all_vectors(random_count=random_count, seed=seed)
    logger.info(f"Generated {len(test_vectors)} test vectors")
    
    # Generate reference outputs
    reference_outputs = {}
    test_inputs = {}
    
    for vector in test_vectors:
        test_id = vector['test_id']
        
        # Store input
        test_inputs[test_id] = {
            'a': vector['a'],
            'b': vector['b'],
            'test_type': vector['test_type']
        }
        
        # Generate golden reference
        golden_outputs = golden_model(vector)
        result = golden_outputs['result'].item()
        
        reference_outputs[test_id] = {
            'result': result,
            'expected_max': max(vector['a'], vector['b'])
        }
        
        # Verify golden model correctness
        assert result == max(vector['a'], vector['b']), \
            f"Golden model error: max({vector['a']}, {vector['b']}) should be {max(vector['a'], vector['b'])}, got {result}"
    
    # Create comprehensive test suite
    test_suite = {
        'metadata': {
            'version': '1.0',
            'data_width': data_width,
            'max_value': (1 << data_width) - 1,
            'test_count': len(test_vectors),
            'random_count': random_count,
            'seed': seed,
            'operation': 'max(a, b)'
        },
        'test_inputs': test_inputs,
        'reference_outputs': reference_outputs,
        'statistics': {
            'total_tests': len(test_vectors),
            'simple_tests': 1,
            'corner_cases': len([v for v in test_vectors if v['test_type'] == 'corner_case']),
            'random_tests': len([v for v in test_vectors if v['test_type'] == 'random'])
        }
    }
    
    logger.info(f"Test suite statistics: {test_suite['statistics']}")
    return test_suite


def save_test_suite(test_suite, output_dir='test_output'):
    """
    Save test suite to files.
    
    Args:
        test_suite: Test suite dictionary
        output_dir: Output directory path
    """
    logger = logging.getLogger(__name__)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save as JSON (human readable)
    json_file = output_path / 'fpu_test_suite.json'
    with open(json_file, 'w') as f:
        json.dump(test_suite, f, indent=2, default=str)
    logger.info(f"Saved JSON test suite: {json_file}")
    
    # Save as pickle (for Python objects)
    pickle_file = output_path / 'fpu_test_suite.pkl'
    with open(pickle_file, 'wb') as f:
        pickle.dump(test_suite, f)
    logger.info(f"Saved pickle test suite: {pickle_file}")
    
    # Generate human-readable report
    report_file = output_path / 'test_suite_report.txt'
    with open(report_file, 'w') as f:
        f.write("FPU Test Suite Report\n")
        f.write("=" * 50 + "\n\n")
        
        metadata = test_suite['metadata']
        f.write(f"Configuration:\n")
        f.write(f"  Data Width: {metadata['data_width']} bits\n")
        f.write(f"  Max Value: {metadata['max_value']}\n")
        f.write(f"  Operation: {metadata['operation']}\n")
        f.write(f"  Random Seed: {metadata['seed']}\n\n")
        
        stats = test_suite['statistics']
        f.write(f"Test Statistics:\n")
        f.write(f"  Total Tests: {stats['total_tests']}\n")
        f.write(f"  Simple Tests: {stats['simple_tests']}\n")
        f.write(f"  Corner Cases: {stats['corner_cases']}\n")
        f.write(f"  Random Tests: {stats['random_tests']}\n\n")
        
        # Sample test cases
        f.write("Sample Test Cases:\n")
        f.write("-" * 30 + "\n")
        sample_count = min(10, len(test_suite['test_inputs']))
        for i, (test_id, inputs) in enumerate(list(test_suite['test_inputs'].items())[:sample_count]):
            outputs = test_suite['reference_outputs'][test_id]
            f.write(f"{i+1:2d}. {test_id:<20} | a={inputs['a']:>10}, b={inputs['b']:>10} | max={outputs['result']:>10}\n")
        
        if len(test_suite['test_inputs']) > sample_count:
            f.write(f"    ... and {len(test_suite['test_inputs']) - sample_count} more tests\n")
    
    logger.info(f"Generated report: {report_file}")
    return json_file, pickle_file, report_file


def verify_test_suite(test_suite):
    """
    Verify test suite correctness.
    
    Args:
        test_suite: Test suite to verify
    
    Returns:
        Boolean indicating if verification passed
    """
    logger = logging.getLogger(__name__)
    logger.info("Verifying test suite correctness...")
    
    errors = []
    
    # Check each test case
    for test_id, inputs in test_suite['test_inputs'].items():
        if test_id not in test_suite['reference_outputs']:
            errors.append(f"Missing reference output for test {test_id}")
            continue
        
        outputs = test_suite['reference_outputs'][test_id]
        expected = max(inputs['a'], inputs['b'])
        actual = outputs['result']
        
        if actual != expected:
            errors.append(f"Test {test_id}: max({inputs['a']}, {inputs['b']}) should be {expected}, got {actual}")
        
        if outputs['expected_max'] != expected:
            errors.append(f"Test {test_id}: expected_max mismatch")
    
    if errors:
        logger.error(f"Verification failed with {len(errors)} errors:")
        for error in errors[:10]:  # Show first 10 errors
            logger.error(f"  {error}")
        return False
    
    logger.info(f"Verification passed for {len(test_suite['test_inputs'])} test cases")
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generate FPU test data')
    parser.add_argument('--data-width', type=int, default=32, help='Data width in bits')
    parser.add_argument('--random-count', type=int, default=20, help='Number of random test vectors')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output-dir', default='test_output', help='Output directory')
    parser.add_argument('--log-level', default='INFO', help='Log level')
    parser.add_argument('--verify', action='store_true', help='Verify test suite after generation')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    try:
        logger.info("Starting FPU test data generation")
        
        # Generate test suite
        test_suite = generate_test_suite(
            data_width=args.data_width,
            random_count=args.random_count,
            seed=args.seed
        )
        
        # Verify if requested
        if args.verify:
            if not verify_test_suite(test_suite):
                logger.error("Test suite verification failed")
                return 1
        
        # Save test suite
        json_file, pickle_file, report_file = save_test_suite(test_suite, args.output_dir)
        
        logger.info("FPU test data generation completed successfully")
        logger.info(f"Generated files:")
        logger.info(f"  JSON: {json_file}")
        logger.info(f"  Pickle: {pickle_file}")
        logger.info(f"  Report: {report_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Test data generation failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())