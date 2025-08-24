"""
Base class for Golden Models with checkpoint functionality.

This module provides the foundational classes for implementing hardware golden models
using PyTorch, with comprehensive checkpoint management for differential testing.
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Optional, List, Tuple, Union
import logging
import copy
from pathlib import Path
import json
import numpy as np
from abc import ABC, abstractmethod


class CheckpointManager:
    """Manages checkpoints for golden model state comparison."""
    
    def __init__(self, max_history: int = 100):
        """
        Initialize checkpoint manager.
        
        Args:
            max_history: Maximum number of checkpoint states to keep in memory
        """
        self.checkpoints: Dict[str, Any] = {}
        self.checkpoint_history: List[Dict[str, Any]] = []
        self.max_history = max_history
        self.logger = logging.getLogger(__name__)
    
    def save_checkpoint(self, name: str, data: Any, timestamp: Optional[int] = None) -> None:
        """
        Save a checkpoint with given name and data.
        
        Args:
            name: Checkpoint identifier
            data: Data to save (tensor, dict, or other serializable object)
            timestamp: Optional timestamp for the checkpoint
        """
        # Convert tensors to CPU for storage
        if isinstance(data, torch.Tensor):
            checkpoint_data = data.detach().cpu().clone()
        elif isinstance(data, dict):
            checkpoint_data = {k: v.detach().cpu().clone() if isinstance(v, torch.Tensor) else v 
                             for k, v in data.items()}
        else:
            checkpoint_data = copy.deepcopy(data)
        
        self.checkpoints[name] = checkpoint_data
        
        # Add to history with metadata
        history_entry = {
            'name': name,
            'data': checkpoint_data,
            'timestamp': timestamp or len(self.checkpoint_history)
        }
        
        self.checkpoint_history.append(history_entry)
        
        # Maintain history size limit
        if len(self.checkpoint_history) > self.max_history:
            self.checkpoint_history.pop(0)
        
        self.logger.debug(f"Checkpoint '{name}' saved with shape/type: {self._get_data_info(data)}")
    
    def get_checkpoint(self, name: str) -> Optional[Any]:
        """Retrieve checkpoint by name."""
        return self.checkpoints.get(name)
    
    def get_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Get the most recent checkpoint."""
        return self.checkpoint_history[-1] if self.checkpoint_history else None
    
    def clear_checkpoints(self) -> None:
        """Clear all checkpoints."""
        self.checkpoints.clear()
        self.checkpoint_history.clear()
    
    def export_checkpoints(self, filepath: Union[str, Path]) -> None:
        """Export checkpoints to file for debugging."""
        filepath = Path(filepath)
        
        # Convert tensors to numpy for JSON serialization
        exportable_data = {}
        for name, data in self.checkpoints.items():
            if isinstance(data, torch.Tensor):
                exportable_data[name] = {
                    'type': 'tensor',
                    'shape': list(data.shape),
                    'dtype': str(data.dtype),
                    'data': data.numpy().tolist()
                }
            elif isinstance(data, dict):
                exportable_data[name] = {
                    'type': 'dict',
                    'data': {k: v.numpy().tolist() if isinstance(v, torch.Tensor) else v 
                           for k, v in data.items()}
                }
            else:
                exportable_data[name] = {
                    'type': 'other',
                    'data': data
                }
        
        with open(filepath, 'w') as f:
            json.dump(exportable_data, f, indent=2)
        
        self.logger.info(f"Checkpoints exported to {filepath}")
    
    def _get_data_info(self, data: Any) -> str:
        """Get human-readable info about data structure."""
        if isinstance(data, torch.Tensor):
            return f"Tensor{list(data.shape)} ({data.dtype})"
        elif isinstance(data, dict):
            return f"Dict with {len(data)} keys"
        elif isinstance(data, (list, tuple)):
            return f"{type(data).__name__} with {len(data)} elements"
        else:
            return str(type(data).__name__)


class GoldenModelBase(nn.Module, ABC):
    """
    Base class for hardware golden models with checkpoint support.
    
    This class provides the foundation for implementing PyTorch-based golden models
    that can be compared against hardware implementations at multiple stages.
    """
    
    def __init__(self, name: str = "GoldenModel", device: str = "cpu"):
        """
        Initialize golden model base.
        
        Args:
            name: Model name for identification
            device: Device to run computations on
        """
        super().__init__()
        self.name = name
        self.device = torch.device(device)
        self.checkpoint_manager = CheckpointManager()
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # Model state tracking
        self._step_count = 0
        self._last_input = None
        self._last_output = None
        
        # Configuration
        self.config = {}
        
    def forward(self, *args, **kwargs) -> Any:
        """
        Forward pass with automatic checkpoint management.
        
        This method wraps the actual computation to provide checkpoint functionality.
        """
        # Save input checkpoint
        if len(args) == 1 and len(kwargs) == 0:
            input_data = args[0]
        else:
            input_data = {'args': args, 'kwargs': kwargs}
        
        self.checkpoint_manager.save_checkpoint('input', input_data, self._step_count)
        self._last_input = input_data
        
        # Perform actual computation
        output = self._forward_impl(*args, **kwargs)
        
        # Save output checkpoint
        self.checkpoint_manager.save_checkpoint('output', output, self._step_count)
        self._last_output = output
        
        # Save final model state
        self.checkpoint_manager.save_checkpoint('model_state', self.state_dict(), self._step_count)
        
        self._step_count += 1
        return output
    
    @abstractmethod
    def _forward_impl(self, *args, **kwargs) -> Any:
        """
        Actual forward computation implementation.
        
        Subclasses must implement this method with their specific logic.
        """
        raise NotImplementedError("Subclasses must implement _forward_impl")
    
    def add_checkpoint(self, name: str, data: Any) -> None:
        """
        Add a custom checkpoint during computation.
        
        Args:
            name: Checkpoint name
            data: Data to checkpoint
        """
        self.checkpoint_manager.save_checkpoint(name, data, self._step_count)
    
    def get_checkpoint(self, name: str) -> Optional[Any]:
        """Get checkpoint by name."""
        return self.checkpoint_manager.get_checkpoint(name)
    
    def get_all_checkpoints(self) -> Dict[str, Any]:
        """Get all current checkpoints."""
        return self.checkpoint_manager.checkpoints.copy()
    
    def reset_checkpoints(self) -> None:
        """Clear all checkpoints and reset step counter."""
        self.checkpoint_manager.clear_checkpoints()
        self._step_count = 0
        self._last_input = None
        self._last_output = None
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the golden model with parameters."""
        self.config.update(config)
        self.logger.info(f"Model {self.name} configured with: {config}")
    
    def export_debug_data(self, output_dir: Union[str, Path]) -> None:
        """Export debug data including checkpoints and model info."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export checkpoints
        checkpoint_file = output_dir / f"{self.name}_checkpoints.json"
        self.checkpoint_manager.export_checkpoints(checkpoint_file)
        
        # Export model info
        info_file = output_dir / f"{self.name}_info.json"
        model_info = {
            'name': self.name,
            'step_count': self._step_count,
            'config': self.config,
            'device': str(self.device),
            'parameter_count': sum(p.numel() for p in self.parameters()),
            'trainable_parameters': sum(p.numel() for p in self.parameters() if p.requires_grad)
        }
        
        with open(info_file, 'w') as f:
            json.dump(model_info, f, indent=2)
        
        self.logger.info(f"Debug data exported to {output_dir}")
    
    def validate_checkpoint(self, name: str, expected_shape: Optional[Tuple] = None, 
                          expected_dtype: Optional[torch.dtype] = None) -> bool:
        """
        Validate checkpoint data matches expected properties.
        
        Args:
            name: Checkpoint name to validate
            expected_shape: Expected tensor shape (if applicable)
            expected_dtype: Expected data type (if applicable)
            
        Returns:
            True if validation passes, False otherwise
        """
        checkpoint = self.get_checkpoint(name)
        if checkpoint is None:
            self.logger.error(f"Checkpoint '{name}' not found")
            return False
        
        if isinstance(checkpoint, torch.Tensor):
            if expected_shape is not None and checkpoint.shape != expected_shape:
                self.logger.error(f"Checkpoint '{name}' shape mismatch: "
                                f"expected {expected_shape}, got {checkpoint.shape}")
                return False
            
            if expected_dtype is not None and checkpoint.dtype != expected_dtype:
                self.logger.error(f"Checkpoint '{name}' dtype mismatch: "
                                f"expected {expected_dtype}, got {checkpoint.dtype}")
                return False
        
        self.logger.debug(f"Checkpoint '{name}' validation passed")
        return True


class PipelinedGoldenModel(GoldenModelBase):
    """
    Base class for pipelined golden models with stage-wise checkpoints.
    
    This class provides infrastructure for models that have multiple processing stages,
    automatically creating checkpoints at each stage boundary.
    """
    
    def __init__(self, name: str = "PipelinedGoldenModel", device: str = "cpu"):
        super().__init__(name, device)
        self.stages = nn.ModuleList()
        self.stage_names = []
    
    def add_stage(self, stage: nn.Module, name: str) -> None:
        """
        Add a processing stage to the pipeline.
        
        Args:
            stage: PyTorch module representing the stage
            name: Name identifier for the stage
        """
        self.stages.append(stage)
        self.stage_names.append(name)
        self.logger.info(f"Added stage '{name}' to pipeline")
    
    def _forward_impl(self, x: torch.Tensor) -> torch.Tensor:
        """
        Pipeline forward pass with stage checkpoints.
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor after all pipeline stages
        """
        current = x
        
        for i, (stage, name) in enumerate(zip(self.stages, self.stage_names)):
            current = stage(current)
            self.add_checkpoint(f"stage_{i}_{name}", current)
            self.logger.debug(f"Stage {i} ({name}) output shape: {current.shape}")
        
        return current
    
    def get_stage_output(self, stage_name: str) -> Optional[torch.Tensor]:
        """Get output from a specific pipeline stage."""
        for i, name in enumerate(self.stage_names):
            if name == stage_name:
                return self.get_checkpoint(f"stage_{i}_{name}")
        return None