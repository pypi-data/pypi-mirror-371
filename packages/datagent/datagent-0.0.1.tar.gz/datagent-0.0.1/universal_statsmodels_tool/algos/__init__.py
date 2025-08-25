"""
Universal Statsmodels Tool - Unified Interface.

This module provides a unified interface to all statsmodels algorithms
through a single entry point, making it easy to use with LangGraph agents.
"""

from .base_model import BaseStatsModel
from .linear_models import LinearModels
from .glm import GLMModels
from .anova import ANOVAModels
from .rlm import RLMModels
from .nonparametric import NonparametricModels

# Import backward compatibility functions
from .linear_models import (
    universal_linear_models,
    get_available_models as get_available_linear_models,
    validate_model_parameters as validate_linear_model_parameters,
    create_langgraph_tool as create_linear_model_tool,
    extract_model_info as extract_linear_model_info,
    get_model_tool_description as get_linear_model_tool_description
)

from .glm import (
    universal_glm,
    get_available_models as get_available_glm_models,
    validate_model_parameters as validate_glm_parameters,
    create_langgraph_tool as create_glm_tool,
    extract_model_info as extract_glm_info,
    get_model_tool_description as get_glm_tool_description
)

from .anova import (
    universal_anova,
    get_available_models as get_available_anova_models,
    validate_model_parameters as validate_anova_parameters,
    create_langgraph_tool as create_anova_tool,
    extract_model_info as extract_anova_info,
    get_model_tool_description as get_anova_tool_description
)

from .rlm import (
    universal_rlm,
    get_available_models as get_available_rlm_models,
    validate_model_parameters as validate_rlm_parameters,
    create_langgraph_tool as create_rlm_tool,
    extract_model_info as extract_rlm_info,
    get_model_tool_description as get_rlm_tool_description
)

from .nonparametric import (
    universal_nonparametric,
    get_available_models as get_available_nonparametric_models,
    validate_model_parameters as validate_nonparametric_parameters,
    create_langgraph_tool as create_nonparametric_tool,
    extract_model_info as extract_nonparametric_info,
    get_model_tool_description as get_nonparametric_tool_description
)


class UniversalStatsModels:
    """
    Universal interface for all statsmodels algorithms.
    
    This class provides a unified interface to all available statsmodels
    algorithms including linear models, GLM, ANOVA, robust linear models,
    and nonparametric methods.
    """
    
    def __init__(self):
        """Initialize all algorithm handlers."""
        self.linear_models = LinearModels()
        self.glm_models = GLMModels()
        self.anova_models = ANOVAModels()
        self.rlm_models = RLMModels()
        self.nonparametric_models = NonparametricModels()
        
        # Create a unified model mapping
        self.all_models = {}
        self.all_models.update(self.linear_models.get_available_models())
        self.all_models.update(self.glm_models.get_available_models())
        self.all_models.update(self.anova_models.get_available_models())
        self.all_models.update(self.rlm_models.get_available_models())
        self.all_models.update(self.nonparametric_models.get_available_models())
    
    def fit_model(self, algorithm_type: str, model_name: str, data, **kwargs):
        """
        Fit a model using the specified algorithm type and model name.
        
        Args:
            algorithm_type: Type of algorithm ('linear', 'glm', 'anova', 'rlm', 'nonparametric')
            model_name: Name of the specific model
            data: Input DataFrame
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing model fitting results
        """
        if algorithm_type == "linear":
            return self.linear_models.fit_model(model_name, data, **kwargs)
        elif algorithm_type == "glm":
            return self.glm_models.fit_model(model_name, data, **kwargs)
        elif algorithm_type == "anova":
            return self.anova_models.fit_model(model_name, data, **kwargs)
        elif algorithm_type == "rlm":
            return self.rlm_models.fit_model(model_name, data, **kwargs)
        elif algorithm_type == "nonparametric":
            return self.nonparametric_models.fit_model(model_name, data, **kwargs)
        else:
            return {
                "success": False,
                "error": f"Unknown algorithm type: {algorithm_type}. Available types: linear, glm, anova, rlm, nonparametric"
            }
    
    def get_available_models(self, algorithm_type: str = None):
        """
        Get available models for the specified algorithm type or all types.
        
        Args:
            algorithm_type: Type of algorithm to get models for (optional)
            
        Returns:
            Dictionary of available models
        """
        if algorithm_type is None:
            return self.all_models
        elif algorithm_type == "linear":
            return self.linear_models.get_available_models()
        elif algorithm_type == "glm":
            return self.glm_models.get_available_models()
        elif algorithm_type == "anova":
            return self.anova_models.get_available_models()
        elif algorithm_type == "rlm":
            return self.rlm_models.get_available_models()
        elif algorithm_type == "nonparametric":
            return self.nonparametric_models.get_available_models()
        else:
            return {
                "error": f"Unknown algorithm type: {algorithm_type}. Available types: linear, glm, anova, rlm, nonparametric"
            }
    
    def validate_model_parameters(self, algorithm_type: str, model_name: str, parameters: dict):
        """
        Validate parameters for a specific model.
        
        Args:
            algorithm_type: Type of algorithm
            model_name: Name of the model
            parameters: Parameters to validate
            
        Returns:
            Validation result dictionary
        """
        if algorithm_type == "linear":
            return self.linear_models.validate_model_parameters(model_name, parameters)
        elif algorithm_type == "glm":
            return self.glm_models.validate_model_parameters(model_name, parameters)
        elif algorithm_type == "anova":
            return self.anova_models.validate_model_parameters(model_name, parameters)
        elif algorithm_type == "rlm":
            return self.rlm_models.validate_model_parameters(model_name, parameters)
        elif algorithm_type == "nonparametric":
            return self.nonparametric_models.validate_model_parameters(model_name, parameters)
        else:
            return {
                "valid": False,
                "error": f"Unknown algorithm type: {algorithm_type}. Available types: linear, glm, anova, rlm, nonparametric"
            }
    
    def create_langgraph_tool(self, algorithm_type: str, model_name: str):
        """
        Create a LangGraph tool definition for a specific model.
        
        Args:
            algorithm_type: Type of algorithm
            model_name: Name of the model
            
        Returns:
            LangGraph tool definition
        """
        if algorithm_type == "linear":
            return self.linear_models.create_langgraph_tool(model_name)
        elif algorithm_type == "glm":
            return self.glm_models.create_langgraph_tool(model_name)
        elif algorithm_type == "anova":
            return self.anova_models.create_langgraph_tool(model_name)
        elif algorithm_type == "rlm":
            return self.rlm_models.create_langgraph_tool(model_name)
        elif algorithm_type == "nonparametric":
            return self.nonparametric_models.create_langgraph_tool(model_name)
        else:
            return {
                "error": f"Unknown algorithm type: {algorithm_type}. Available types: linear, glm, anova, rlm, nonparametric"
            }
    
    def extract_model_info(self, algorithm_type: str, model_name: str):
        """
        Extract model information for a specific model.
        
        Args:
            algorithm_type: Type of algorithm
            model_name: Name of the model
            
        Returns:
            Model information dictionary
        """
        if algorithm_type == "linear":
            return self.linear_models.extract_model_info(model_name)
        elif algorithm_type == "glm":
            return self.glm_models.extract_model_info(model_name)
        elif algorithm_type == "anova":
            return self.anova_models.extract_model_info(model_name)
        elif algorithm_type == "rlm":
            return self.rlm_models.extract_model_info(model_name)
        elif algorithm_type == "nonparametric":
            return self.nonparametric_models.extract_model_info(model_name)
        else:
            return {
                "error": f"Unknown algorithm type: {algorithm_type}. Available types: linear, glm, anova, rlm, nonparametric"
            }


# Create a global instance for easy access
universal_statsmodels = UniversalStatsModels()


# Convenience functions for backward compatibility
def fit_model(algorithm_type: str, model_name: str, data, **kwargs):
    """
    Convenience function to fit a model.
    
    Args:
        algorithm_type: Type of algorithm
        model_name: Name of the model
        data: Input DataFrame
        **kwargs: Additional parameters
        
    Returns:
        Model fitting results
    """
    return universal_statsmodels.fit_model(algorithm_type, model_name, data, **kwargs)


def get_all_available_models():
    """
    Get all available models across all algorithm types.
    
    Returns:
        Dictionary of all available models
    """
    return universal_statsmodels.get_available_models()


def get_models_by_type(algorithm_type: str):
    """
    Get models for a specific algorithm type.
    
    Args:
        algorithm_type: Type of algorithm
        
    Returns:
        Dictionary of models for the specified type
    """
    return universal_statsmodels.get_available_models(algorithm_type)


# Export main classes and functions
__all__ = [
    'BaseStatsModel',
    'LinearModels',
    'GLMModels', 
    'ANOVAModels',
    'RLMModels',
    'NonparametricModels',
    'UniversalStatsModels',
    'universal_statsmodels',
    'fit_model',
    'get_all_available_models',
    'get_models_by_type',
    # Backward compatibility
    'universal_linear_models',
    'universal_glm',
    'universal_anova',
    'universal_rlm',
    'universal_nonparametric',
    'get_available_linear_models',
    'get_available_glm_models',
    'get_available_anova_models',
    'get_available_rlm_models',
    'get_available_nonparametric_models'
]
