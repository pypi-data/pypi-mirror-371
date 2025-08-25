"""
DataAgent - A comprehensive data analysis toolkit

This package provides universal tools for scikit-learn and statsmodels
that can be easily integrated with LangGraph agents for automated data analysis.
"""

__version__ = "0.0.1"
__author__ = "Haris Jabbar"
__email__ = "haris@superpandas.ai"

# Import sklearn tools
from .sklearn_tools import (
    universal_sklearn_estimator,
    extract_sklearn_model_info,
    get_sklearn_tool_description,
    create_sklearn_langgraph_tool,
    get_available_sklearn_models,
    validate_sklearn_parameters
)

# Import statsmodels tools
from .statsmodels_tools import (
    # Linear models
    universal_linear_models,
    extract_linear_model_info,
    get_linear_model_tool_description,
    create_linear_langgraph_tool,
    get_linear_available_models,
    validate_linear_model_parameters,
    
    # GLM models
    universal_glm,
    extract_glm_info,
    get_glm_tool_description,
    create_glm_langgraph_tool,
    get_glm_available_models,
    validate_glm_parameters,
    
    # Nonparametric models
    universal_nonparametric,
    extract_nonparametric_info,
    get_nonparametric_tool_description,
    create_nonparametric_langgraph_tool,
    get_nonparametric_available_models,
    validate_nonparametric_parameters,
    
    # Robust Linear Models
    universal_rlm,
    extract_rlm_info,
    get_rlm_tool_description,
    create_rlm_langgraph_tool,
    get_rlm_available_models,
    validate_rlm_parameters,
    
    # ANOVA models
    universal_anova,
    extract_anova_info,
    get_anova_tool_description,
    create_anova_langgraph_tool,
    get_anova_available_models,
    validate_anova_parameters
)

__all__ = [
    # Sklearn tools
    "universal_sklearn_estimator",
    "extract_sklearn_model_info",
    "get_sklearn_tool_description",
    "create_sklearn_langgraph_tool",
    "get_available_sklearn_models",
    "validate_sklearn_parameters",
    
    # Statsmodels tools
    "universal_linear_models",
    "extract_linear_model_info",
    "get_linear_model_tool_description",
    "create_linear_langgraph_tool",
    "get_linear_available_models",
    "validate_linear_model_parameters",
    "universal_glm",
    "extract_glm_info",
    "get_glm_tool_description",
    "create_glm_langgraph_tool",
    "get_glm_available_models",
    "validate_glm_parameters",
    "universal_nonparametric",
    "extract_nonparametric_info",
    "get_nonparametric_tool_description",
    "create_nonparametric_langgraph_tool",
    "get_nonparametric_available_models",
    "validate_nonparametric_parameters",
    "universal_rlm",
    "extract_rlm_info",
    "get_rlm_tool_description",
    "create_rlm_langgraph_tool",
    "get_rlm_available_models",
    "validate_rlm_parameters",
    "universal_anova",
    "extract_anova_info",
    "get_anova_tool_description",
    "create_anova_langgraph_tool",
    "get_anova_available_models",
    "validate_anova_parameters"
]
