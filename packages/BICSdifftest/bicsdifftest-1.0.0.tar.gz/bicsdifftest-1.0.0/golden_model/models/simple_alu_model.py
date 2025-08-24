"""
Golden model for Simple ALU design.

This module implements a PyTorch-based golden model that mirrors
the functionality of the simple_alu Verilog module.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, Tuple, Optional, List
import logging

# Import base classes
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from golden_model.base import GoldenModelBase, PipelinedGoldenModel


class SimpleALUGoldenModel(PipelinedGoldenModel):
    """
    PyTorch golden model for the Simple ALU design.
    
    This model implements the same functionality as the Verilog simple_alu module
    with checkpoints at each pipeline stage for comprehensive verification.
    """
    
    # Operation codes - must match Verilog definitions
    ALU_ADD = 0x0
    ALU_SUB = 0x1
    ALU_MUL = 0x2
    ALU_DIV = 0x3
    ALU_AND = 0x4
    ALU_OR  = 0x5
    ALU_XOR = 0x6
    ALU_NOT = 0x7
    ALU_SHL = 0x8
    ALU_SHR = 0x9
    ALU_ROL = 0xA
    ALU_ROR = 0xB
    ALU_MAX = 0xC
    ALU_MIN = 0xD
    ALU_CMP = 0xE
    ALU_NOP = 0xF
    
    def __init__(self, data_width: int = 32, device: str = "cpu"):
        """
        Initialize Simple ALU golden model.
        
        Args:
            data_width: Data width in bits
            device: Device to run computations on
        """
        super().__init__("SimpleALUGoldenModel", device)
        
        self.data_width = data_width
        self.max_value = (1 << data_width) - 1
        self.sign_bit = 1 << (data_width - 1)
        
        # Configure pipeline stages
        self.add_stage(ALUStage1(data_width), "arithmetic_logic")
        self.add_stage(ALUStage2(data_width), "shift_rotate")
        
        # Internal state for multi-cycle operations
        self.pipeline_counter = 0
        self.current_inputs = None
        
    def forward(self, inputs: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """
        Forward pass of the ALU golden model.
        
        Args:
            inputs: Dictionary containing 'a', 'b', 'op', and 'valid'
            
        Returns:
            Dictionary containing outputs and intermediate values
        """
        # Extract inputs
        a = self._to_tensor(inputs.get('a', 0))
        b = self._to_tensor(inputs.get('b', 0))
        op = int(inputs.get('op', self.ALU_NOP))
        valid = bool(inputs.get('valid', False))
        
        # Save input checkpoint
        input_data = {
            'operand_a': a,
            'operand_b': b,
            'operation': op,
            'valid': valid
        }
        self.add_checkpoint('inputs', input_data)
        
        if not valid:
            # Return zero outputs when not valid
            return self._create_zero_output()
        
        # Check if this is a multi-cycle operation
        is_multi_cycle = op in [self.ALU_MUL, self.ALU_DIV]
        
        if is_multi_cycle:
            self.pipeline_counter += 1
            ready = self.pipeline_counter >= 3  # 3 cycles for mul/div
        else:
            self.pipeline_counter = 0
            ready = True
        
        self.add_checkpoint('pipeline_state', {
            'counter': self.pipeline_counter,
            'ready': ready,
            'is_multi_cycle': is_multi_cycle
        })
        
        if not ready:
            return self._create_zero_output()
        
        # Reset counter after completion
        self.pipeline_counter = 0
        
        # Stage 1: Arithmetic and logic operations
        stage1_result, stage1_overflow = self._stage1_compute(a, b, op)
        self.add_checkpoint('stage1', {
            'result': stage1_result,
            'overflow': stage1_overflow
        })
        
        # Stage 2: Shift and rotation operations
        stage2_result, stage2_overflow = self._stage2_compute(a, b, stage1_result, stage1_overflow, op)
        self.add_checkpoint('stage2', {
            'result': stage2_result,
            'overflow': stage2_overflow
        })
        
        # Final processing
        final_result = stage2_result
        final_overflow = stage2_overflow
        zero_flag = (final_result == 0)
        
        # Create output dictionary
        outputs = {
            'result': final_result,
            'overflow': final_overflow,
            'zero': zero_flag,
            'valid': torch.tensor(True),
            'debug_stage1': stage1_result,
            'debug_stage2': stage2_result,
            'debug_flags': torch.tensor([
                1,   # input_valid_reg (bit 0)
                1,   # computation_valid (bit 1) 
                int(zero_flag),      # zero_o (bit 2)
                int(final_overflow)  # final_overflow (bit 3)
            ])
        }
        
        self.add_checkpoint('outputs', outputs)
        
        return outputs
    
    def _stage1_compute(self, a: torch.Tensor, b: torch.Tensor, op: int) -> Tuple[torch.Tensor, bool]:
        """Compute stage 1 operations."""
        result = torch.tensor(0, dtype=torch.int64)
        overflow = False
        
        if op == self.ALU_ADD:
            temp_result = int(a) + int(b)
            result = torch.tensor(temp_result & self.max_value, dtype=torch.int64)
            overflow = temp_result > self.max_value
            
        elif op == self.ALU_SUB:
            temp_result = int(a) - int(b)
            result = torch.tensor(temp_result & self.max_value, dtype=torch.int64)
            overflow = temp_result < 0
            
        elif op == self.ALU_MUL:
            temp_result = int(a) * int(b)
            result = torch.tensor(temp_result & self.max_value, dtype=torch.int64)
            overflow = temp_result > self.max_value
            
        elif op == self.ALU_DIV:
            if int(b) != 0:
                result = torch.tensor(int(a) // int(b), dtype=torch.int64)
                overflow = False
            else:
                result = torch.tensor(self.max_value, dtype=torch.int64)  # All 1s
                overflow = True
                
        elif op == self.ALU_AND:
            result = torch.tensor(int(a) & int(b), dtype=torch.int64)
            
        elif op == self.ALU_OR:
            result = torch.tensor(int(a) | int(b), dtype=torch.int64)
            
        elif op == self.ALU_XOR:
            result = torch.tensor(int(a) ^ int(b), dtype=torch.int64)
            
        elif op == self.ALU_NOT:
            result = torch.tensor((~int(a)) & self.max_value, dtype=torch.int64)
            
        else:
            result = a.clone()
            
        return result, overflow
    
    def _stage2_compute(self, a: torch.Tensor, b: torch.Tensor, stage1_result: torch.Tensor, 
                       stage1_overflow: bool, op: int) -> Tuple[torch.Tensor, bool]:
        """Compute stage 2 operations."""
        result = stage1_result.clone()
        overflow = stage1_overflow
        
        if op == self.ALU_SHL:
            shift_amount = int(b) & 0x3F  # 6-bit mask
            if shift_amount < self.data_width:
                shifted = int(stage1_result) << shift_amount
                result = torch.tensor(shifted & self.max_value, dtype=torch.int64)
                # Check if any bits were shifted out
                overflow = (shifted >> self.data_width) != 0
            else:
                result = torch.tensor(0, dtype=torch.int64)
                overflow = int(stage1_result) != 0
                
        elif op == self.ALU_SHR:
            shift_amount = int(b) & 0x3F
            if shift_amount < self.data_width:
                result = torch.tensor(int(stage1_result) >> shift_amount, dtype=torch.int64)
            else:
                result = torch.tensor(0, dtype=torch.int64)
                
        elif op == self.ALU_ROL:
            rotate_amount = int(b) % self.data_width
            val = int(stage1_result)
            rotated = ((val << rotate_amount) | (val >> (self.data_width - rotate_amount))) & self.max_value
            result = torch.tensor(rotated, dtype=torch.int64)
            
        elif op == self.ALU_ROR:
            rotate_amount = int(b) % self.data_width
            val = int(stage1_result)
            rotated = ((val >> rotate_amount) | (val << (self.data_width - rotate_amount))) & self.max_value
            result = torch.tensor(rotated, dtype=torch.int64)
            
        elif op == self.ALU_MAX:
            result = torch.tensor(max(int(a), int(b)), dtype=torch.int64)
            
        elif op == self.ALU_MIN:
            result = torch.tensor(min(int(a), int(b)), dtype=torch.int64)
            
        elif op == self.ALU_CMP:
            a_val, b_val = int(a), int(b)
            if a_val == b_val:
                result = torch.tensor(0x00000000, dtype=torch.int64)
            elif a_val > b_val:
                result = torch.tensor(0x00000001, dtype=torch.int64)
            else:
                result = torch.tensor(0xFFFFFFFF, dtype=torch.int64)
                
        return result, overflow
    
    def _to_tensor(self, value: Any) -> torch.Tensor:
        """Convert value to tensor."""
        if isinstance(value, torch.Tensor):
            return value.to(torch.int64)
        else:
            return torch.tensor(int(value), dtype=torch.int64)
    
    def _create_zero_output(self) -> Dict[str, torch.Tensor]:
        """Create zero output for invalid/not-ready states."""
        return {
            'result': torch.tensor(0, dtype=torch.int64),
            'overflow': torch.tensor(False),
            'zero': torch.tensor(True),
            'valid': torch.tensor(False),
            'debug_stage1': torch.tensor(0, dtype=torch.int64),
            'debug_stage2': torch.tensor(0, dtype=torch.int64),
            'debug_flags': torch.tensor([0, 0, 1, 0])  # [input_valid_reg=0, computation_valid=0, zero=1, overflow=0]
        }
    
    def get_operation_name(self, op_code: int) -> str:
        """Get operation name from operation code."""
        op_names = {
            self.ALU_ADD: "ADD",
            self.ALU_SUB: "SUB",
            self.ALU_MUL: "MUL",
            self.ALU_DIV: "DIV",
            self.ALU_AND: "AND",
            self.ALU_OR:  "OR",
            self.ALU_XOR: "XOR",
            self.ALU_NOT: "NOT",
            self.ALU_SHL: "SHL",
            self.ALU_SHR: "SHR",
            self.ALU_ROL: "ROL",
            self.ALU_ROR: "ROR",
            self.ALU_MAX: "MAX",
            self.ALU_MIN: "MIN",
            self.ALU_CMP: "CMP",
            self.ALU_NOP: "NOP"
        }
        return op_names.get(op_code, f"UNKNOWN({op_code})")


class ALUStage1(nn.Module):
    """Stage 1 of ALU pipeline - Arithmetic and Logic operations."""
    
    def __init__(self, data_width: int):
        super().__init__()
        self.data_width = data_width
        
    def forward(self, x):
        # This is a placeholder - actual computation is done in the main model
        return x


class ALUStage2(nn.Module):
    """Stage 2 of ALU pipeline - Shift and Rotation operations."""
    
    def __init__(self, data_width: int):
        super().__init__()
        self.data_width = data_width
        
    def forward(self, x):
        # This is a placeholder - actual computation is done in the main model
        return x


# Test vector generator for ALU
class ALUTestVectorGenerator:
    """Generate test vectors for ALU verification."""
    
    def __init__(self, data_width: int = 32):
        self.data_width = data_width
        self.max_value = (1 << data_width) - 1
        
    def generate_corner_cases(self) -> List[Dict[str, Any]]:
        """Generate corner case test vectors."""
        test_vectors = []
        
        corner_values = [
            0x00000000,  # Zero
            0x00000001,  # One
            0xFFFFFFFF,  # Max value / -1
            0x80000000,  # Sign bit
            0x7FFFFFFF,  # Max positive
            0xAAAAAAAA,  # Alternating pattern
            0x55555555   # Alternating inverse
        ]
        
        # Test all operations with corner values
        for op in range(16):  # 16 ALU operations
            for a in corner_values:
                for b in corner_values[:4]:  # Reduce combinations
                    test_vectors.append({
                        'a': a & self.max_value,
                        'b': b & self.max_value,
                        'op': op,
                        'valid': True
                    })
                    
        return test_vectors
        
    def generate_random_vectors(self, count: int = 1000, seed: int = 42) -> List[Dict[str, Any]]:
        """Generate random test vectors."""
        np.random.seed(seed)
        test_vectors = []
        
        for _ in range(count):
            test_vectors.append({
                'a': np.random.randint(0, self.max_value + 1),
                'b': np.random.randint(0, self.max_value + 1),
                'op': np.random.randint(0, 16),
                'valid': True
            })
            
        return test_vectors
        
    def generate_targeted_vectors(self) -> List[Dict[str, Any]]:
        """Generate vectors targeting specific functionality."""
        test_vectors = []
        
        # Addition overflow tests
        test_vectors.extend([
            {'a': 0xFFFFFFFF, 'b': 0x00000001, 'op': SimpleALUGoldenModel.ALU_ADD, 'valid': True},
            {'a': 0x80000000, 'b': 0x80000000, 'op': SimpleALUGoldenModel.ALU_ADD, 'valid': True},
            {'a': 0x7FFFFFFF, 'b': 0x7FFFFFFF, 'op': SimpleALUGoldenModel.ALU_ADD, 'valid': True}
        ])
        
        # Division by zero tests
        test_vectors.extend([
            {'a': 0x12345678, 'b': 0x00000000, 'op': SimpleALUGoldenModel.ALU_DIV, 'valid': True},
            {'a': 0xFFFFFFFF, 'b': 0x00000000, 'op': SimpleALUGoldenModel.ALU_DIV, 'valid': True}
        ])
        
        # Shift tests with large shift amounts
        test_vectors.extend([
            {'a': 0xFFFFFFFF, 'b': 32, 'op': SimpleALUGoldenModel.ALU_SHL, 'valid': True},
            {'a': 0xFFFFFFFF, 'b': 64, 'op': SimpleALUGoldenModel.ALU_SHR, 'valid': True}
        ])
        
        # Rotation tests
        test_vectors.extend([
            {'a': 0x12345678, 'b': 8, 'op': SimpleALUGoldenModel.ALU_ROL, 'valid': True},
            {'a': 0x87654321, 'b': 16, 'op': SimpleALUGoldenModel.ALU_ROR, 'valid': True}
        ])
        
        return test_vectors