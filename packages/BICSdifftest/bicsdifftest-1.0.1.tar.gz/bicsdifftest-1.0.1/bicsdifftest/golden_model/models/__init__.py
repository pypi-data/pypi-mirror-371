"""
Golden models for different DUT designs.

This package contains PyTorch-based golden models that mirror
the functionality of hardware designs for differential testing.
"""

from .simple_alu_model import SimpleALUGoldenModel
from .fc_layer_model import FCLayerGoldenModel
from .fpu_model import FPUGoldenModel, FPUTestVectorGenerator

__all__ = [
    'SimpleALUGoldenModel',
    'FCLayerGoldenModel',
    'FPUGoldenModel',
    'FPUTestVectorGenerator'
]