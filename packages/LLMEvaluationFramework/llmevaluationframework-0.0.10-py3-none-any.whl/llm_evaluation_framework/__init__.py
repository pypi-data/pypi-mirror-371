"""
LLM Evaluation Framework
========================
A modular, extensible framework for evaluating and comparing large language models (LLMs)
with support for multiple scoring strategies, dataset generation, persistence, and CLI usage.
"""

__version__ = "0.1.0"

# Expose key components for easy import
from .registry.model_registry import ModelRegistry

# Updated import to reflect correct module path
from .model_inference_engine import ModelInferenceEngine
from .auto_suggestion_engine import AutoSuggestionEngine  # fixed path, file is in root package
from .test_dataset_generator import TestDatasetGenerator
