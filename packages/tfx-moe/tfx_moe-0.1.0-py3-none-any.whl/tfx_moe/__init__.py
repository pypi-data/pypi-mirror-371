"""
TFX Component for Evaluating Multiple Model Outputs.

This module provides the MultiOutputEvaluator component, which computes metrics (e.g., MSE, MAE)
for multiple model outputs and formats results for TensorFlow Model Analysis (TFMA).
"""

from .core import MultiOutputEvaluator
__all__ = ["MultiOutputEvaluator"]