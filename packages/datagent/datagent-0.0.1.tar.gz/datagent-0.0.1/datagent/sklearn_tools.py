"""
Sklearn Tools Module for DataAgent

This module provides universal scikit-learn tools that can be easily integrated
with LangGraph agents for automated machine learning tasks.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path to import from universal_sklearn_tool
parent_dir = Path(__file__).parent.parent
sklearn_tool_path = parent_dir / "universal_sklearn_tool"
if sklearn_tool_path.exists():
    sys.path.insert(0, str(parent_dir))
    
    # Import the main universal estimator function
    from universal_sklearn_tool.universal_estimator import (
        universal_estimator as universal_sklearn_estimator,
        extract_estimator_info as extract_sklearn_model_info,
        get_estimator_tool_description as get_sklearn_tool_description,
        create_langgraph_tool as create_sklearn_langgraph_tool,
        get_available_estimators as get_available_sklearn_models,
        validate_estimator_parameters as validate_sklearn_parameters
    )
else:
    # Fallback implementation if the sklearn tool directory is not found
    def universal_sklearn_estimator(*args, **kwargs):
        raise ImportError("Universal sklearn tool not found. Please ensure the universal_sklearn_tool directory exists.")
    
    def extract_sklearn_model_info(*args, **kwargs):
        raise ImportError("Universal sklearn tool not found. Please ensure the universal_sklearn_tool directory exists.")
    
    def get_sklearn_tool_description(*args, **kwargs):
        raise ImportError("Universal sklearn tool not found. Please ensure the universal_sklearn_tool directory exists.")
    
    def create_sklearn_langgraph_tool(*args, **kwargs):
        raise ImportError("Universal sklearn tool not found. Please ensure the universal_sklearn_tool directory exists.")
    
    def get_available_sklearn_models(*args, **kwargs):
        raise ImportError("Universal sklearn tool not found. Please ensure the universal_sklearn_tool directory exists.")
    
    def validate_sklearn_parameters(*args, **kwargs):
        raise ImportError("Universal sklearn tool not found. Please ensure the universal_sklearn_tool directory exists.")

# Clean up the path modification
if sklearn_tool_path.exists():
    sys.path.pop(0)
