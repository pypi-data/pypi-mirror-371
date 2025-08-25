"""
Universal Statsmodels Tool Package

This package provides a comprehensive template function that can handle all statsmodels
statistical analyses through a unified interface, making it suitable for use with LLMs in LangGraph.
"""

# Import from the algos submodules
from .algos.linear_models import (
    universal_linear_models,
    extract_model_info as extract_linear_model_info,
    get_model_tool_description as get_linear_model_tool_description,
    create_langgraph_tool as create_linear_langgraph_tool,
    get_available_models as get_linear_available_models,
    validate_model_parameters as validate_linear_model_parameters
)

from .algos.glm import (
    universal_glm,
    extract_model_info as extract_glm_info,
    get_model_tool_description as get_glm_tool_description,
    create_langgraph_tool as create_glm_langgraph_tool,
    get_available_models as get_glm_available_models,
    validate_model_parameters as validate_glm_parameters
)

from .algos.nonparametric import (
    universal_nonparametric,
    extract_model_info as extract_nonparametric_info,
    get_model_tool_description as get_nonparametric_tool_description,
    create_langgraph_tool as create_nonparametric_langgraph_tool,
    get_available_models as get_nonparametric_available_models,
    validate_model_parameters as validate_nonparametric_parameters
)

from .algos.rlm import (
    universal_rlm,
    extract_model_info as extract_rlm_info,
    get_model_tool_description as get_rlm_tool_description,
    create_langgraph_tool as create_rlm_langgraph_tool,
    get_available_models as get_rlm_available_models,
    validate_model_parameters as validate_rlm_parameters
)

from .algos.anova import (
    universal_anova,
    extract_model_info as extract_anova_info,
    get_model_tool_description as get_anova_tool_description,
    create_langgraph_tool as create_anova_langgraph_tool,
    get_available_models as get_anova_available_models,
    validate_model_parameters as validate_anova_parameters
)

__version__ = "1.0.0"
__all__ = [
    # Linear models
    "universal_linear_models",
    "extract_linear_model_info", 
    "get_linear_model_tool_description",
    "create_linear_langgraph_tool",
    "get_linear_available_models",
    "validate_linear_model_parameters",
    # GLM models
    "universal_glm",
    "extract_glm_info", 
    "get_glm_tool_description",
    "create_glm_langgraph_tool",
    "get_glm_available_models",
    "validate_glm_parameters",
    # Nonparametric models
    "universal_nonparametric",
    "extract_nonparametric_info", 
    "get_nonparametric_tool_description",
    "create_nonparametric_langgraph_tool",
    "get_nonparametric_available_models",
    "validate_nonparametric_parameters",
    # Robust Linear Models
    "universal_rlm",
    "extract_rlm_info", 
    "get_rlm_tool_description",
    "create_rlm_langgraph_tool",
    "get_rlm_available_models",
    "validate_rlm_parameters",
    # ANOVA models
    "universal_anova",
    "extract_anova_info", 
    "get_anova_tool_description",
    "create_anova_langgraph_tool",
    "get_anova_available_models",
    "validate_anova_parameters"
]
