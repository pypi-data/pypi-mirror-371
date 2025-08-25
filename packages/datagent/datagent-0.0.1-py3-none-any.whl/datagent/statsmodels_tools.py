"""
Statsmodels Tools Module for DataAgent

This module provides universal statsmodels tools that can be easily integrated
with LangGraph agents for automated statistical analysis tasks.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path to import from universal_statsmodels_tool
parent_dir = Path(__file__).parent.parent
statsmodels_tool_path = parent_dir / "universal_statsmodels_tool"
if statsmodels_tool_path.exists():
    sys.path.insert(0, str(parent_dir))
    
    # Import all the statsmodels tools
    from universal_statsmodels_tool.algos.linear_models import (
        universal_linear_models,
        extract_model_info as extract_linear_model_info,
        get_model_tool_description as get_linear_model_tool_description,
        create_langgraph_tool as create_linear_langgraph_tool,
        get_available_models as get_linear_available_models,
        validate_model_parameters as validate_linear_model_parameters
    )

    from universal_statsmodels_tool.algos.glm import (
        universal_glm,
        extract_model_info as extract_glm_info,
        get_model_tool_description as get_glm_tool_description,
        create_langgraph_tool as create_glm_langgraph_tool,
        get_available_models as get_glm_available_models,
        validate_model_parameters as validate_glm_parameters
    )

    from universal_statsmodels_tool.algos.nonparametric import (
        universal_nonparametric,
        extract_model_info as extract_nonparametric_info,
        get_model_tool_description as get_nonparametric_tool_description,
        create_langgraph_tool as create_nonparametric_langgraph_tool,
        get_available_models as get_nonparametric_available_models,
        validate_model_parameters as validate_nonparametric_parameters
    )

    from universal_statsmodels_tool.algos.rlm import (
        universal_rlm,
        extract_model_info as extract_rlm_info,
        get_model_tool_description as get_rlm_tool_description,
        create_langgraph_tool as create_rlm_langgraph_tool,
        get_available_models as get_rlm_available_models,
        validate_model_parameters as validate_rlm_parameters
    )

    from universal_statsmodels_tool.algos.anova import (
        universal_anova,
        extract_model_info as extract_anova_info,
        get_model_tool_description as get_anova_tool_description,
        create_langgraph_tool as create_anova_langgraph_tool,
        get_available_models as get_anova_available_models,
        validate_model_parameters as validate_anova_parameters
    )
else:
    # Fallback implementations if the statsmodels tool directory is not found
    def universal_linear_models(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def extract_linear_model_info(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def get_linear_model_tool_description(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def create_linear_langgraph_tool(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def get_linear_available_models(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def validate_linear_model_parameters(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    # GLM fallbacks
    def universal_glm(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def extract_glm_info(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def get_glm_tool_description(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def create_glm_langgraph_tool(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def get_glm_available_models(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def validate_glm_parameters(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    # Nonparametric fallbacks
    def universal_nonparametric(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def extract_nonparametric_info(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def get_nonparametric_tool_description(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def create_nonparametric_langgraph_tool(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def get_nonparametric_available_models(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def validate_nonparametric_parameters(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    # RLM fallbacks
    def universal_rlm(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def extract_rlm_info(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def get_rlm_tool_description(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def create_rlm_langgraph_tool(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def get_rlm_available_models(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def validate_rlm_parameters(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    # ANOVA fallbacks
    def universal_anova(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def extract_anova_info(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def get_anova_tool_description(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def create_anova_langgraph_tool(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def get_anova_available_models(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")
    
    def validate_anova_parameters(*args, **kwargs):
        raise ImportError("Universal statsmodels tool not found. Please ensure the universal_statsmodels_tool directory exists.")

# Clean up the path modification
if statsmodels_tool_path.exists():
    sys.path.pop(0)
