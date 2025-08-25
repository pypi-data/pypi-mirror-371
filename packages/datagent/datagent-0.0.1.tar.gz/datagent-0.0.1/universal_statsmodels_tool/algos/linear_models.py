"""
Universal Linear Models Tool for LangGraph Agent.

This module provides a comprehensive template function that can handle all statsmodels
linear regression models through a unified interface, making it suitable for use with LLMs in LangGraph.
"""

import json
import inspect
import importlib
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
import logging
from .base_model import BaseStatsModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinearModels(BaseStatsModel):
    """
    Linear Models implementation inheriting from BaseStatsModel.
    
    Handles all linear regression models including OLS, GLS, WLS, quantile regression,
    recursive least squares, rolling regression, and mixed linear models.
    """
    
    def _get_model_mapping(self) -> Dict[str, Any]:
        """
        Define the model mapping for linear models.
        
        Returns:
            Dictionary mapping model names to their configurations
        """
        return {
            # Linear Regression Models
            "ols": {
                "module": "statsmodels.regression.linear_model",
                "class": "OLS",
                "type": "regression",
                "metrics": ["r2", "adj_r2", "aic", "bic", "f_statistic", "p_value", "residuals", "coefficients"],
                "description": "Ordinary Least Squares linear regression",
                "formula_required": False
            },
            "gls": {
                "module": "statsmodels.regression.linear_model", 
                "class": "GLS",
                "type": "regression",
                "metrics": ["r2", "adj_r2", "aic", "bic", "f_statistic", "p_value", "residuals", "coefficients"],
                "description": "Generalized Least Squares regression",
                "formula_required": False
            },
            "wls": {
                "module": "statsmodels.regression.linear_model",
                "class": "WLS", 
                "type": "regression",
                "metrics": ["r2", "adj_r2", "aic", "bic", "f_statistic", "p_value", "residuals", "coefficients"],
                "description": "Weighted Least Squares regression",
                "formula_required": False
            },
            "quantile_regression": {
                "module": "statsmodels.regression.quantile_regression",
                "class": "QuantReg",
                "type": "regression",
                "metrics": ["pseudo_r2", "aic", "bic", "coefficients"],
                "description": "Quantile regression",
                "formula_required": False
            },
            "recursive_least_squares": {
                "module": "statsmodels.regression.recursive_ls",
                "class": "RecursiveLS",
                "type": "regression",
                "metrics": ["r2", "aic", "bic", "coefficients", "recursive_coefficients"],
                "description": "Recursive least squares regression",
                "formula_required": False
            },
            "rolling_regression": {
                "module": "statsmodels.regression.rolling",
                "class": "RollingOLS",
                "type": "regression",
                "metrics": ["r2", "coefficients", "rolling_metrics"],
                "description": "Rolling window regression",
                "formula_required": False
            },
            "mixed_linear_model": {
                "module": "statsmodels.regression.mixed_linear_model",
                "class": "MixedLM",
                "type": "regression",
                "metrics": ["aic", "bic", "coefficients", "random_effects"],
                "description": "Linear Mixed Effects Model",
                "formula_required": True
            }
        }
    
    def _get_available_models(self) -> Dict[str, Any]:
        """
        Define available models grouped by type.
        
        Returns:
            Dictionary of available models grouped by type
        """
        models_by_type = {}
        
        for name, info in self.model_mapping.items():
            model_type = info["type"]
            if model_type not in models_by_type:
                models_by_type[model_type] = {}
            
            models_by_type[model_type][name] = {
                "description": info["description"],
                "class": info["class"],
                "module": info["module"],
                "metrics": info["metrics"],
                "formula_required": info["formula_required"]
            }
        
        return models_by_type
    
    def fit_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Fit a linear model using the specified model name.
        
        Args:
            model_name: Name of the model from model mapping
            data: Input DataFrame
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing model fitting results
        """
        try:
            # Validate model name
            if model_name not in self.model_mapping:
                return self.create_error_result(
                    model_name, 
                    f"Model '{model_name}' not found. Available models: {list(self.model_mapping.keys())}"
                )
            
            mapping = self.model_mapping[model_name]
            formula_required = mapping["formula_required"]
            
            # Extract common parameters
            dependent_var = kwargs.get('dependent_var')
            independent_vars = kwargs.get('independent_vars')
            formula = kwargs.get('formula')
            add_constant = kwargs.get('add_constant', True)
            
            # Validate dependent variable
            if dependent_var and dependent_var not in data.columns:
                return self.create_error_result(
                    model_name,
                    f"Dependent variable '{dependent_var}' not found in data columns: {list(data.columns)}"
                )
            
            # Prepare data
            data_prep = self.prepare_data_for_model(
                data, dependent_var, independent_vars, formula, add_constant
            )
            
            if "error" in data_prep:
                return self.create_error_result(model_name, data_prep["error"])
            
            # Fit model based on data preparation method
            if data_prep["method"] == "formula":
                fitted_model = self._fit_with_formula(model_name, data_prep, **kwargs)
            else:
                fitted_model = self._fit_with_arrays(model_name, data_prep, **kwargs)
            
            if not fitted_model["success"]:
                return fitted_model
            
            # Extract metrics
            metrics = self._extract_linear_metrics(fitted_model["fitted_model"], model_name)
            
            # Run diagnostics
            diagnostics = self.run_diagnostics(fitted_model["fitted_model"])
            
            # Create result
            return self.create_result_dict(
                model_name=model_name,
                fitted_model=fitted_model["fitted_model"],
                data_shape=data_prep["data"].shape,
                metrics=metrics,
                diagnostics=diagnostics,
                n_observations=len(data_prep["data"]),
                n_variables=len(independent_vars) if independent_vars else None,
                model_type=mapping["type"]
            )
            
        except Exception as e:
            logger.error(f"Failed to fit {model_name}: {str(e)}")
            return self.create_error_result(model_name, f"Failed to fit {model_name}: {str(e)}")
    
    def _fit_with_formula(self, model_name: str, data_prep: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Fit model using formula interface.
        
        Args:
            model_name: Name of the model
            data_prep: Prepared data dictionary
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing fitted model
        """
        try:
            # Import statsmodels formula interface
            import statsmodels.api as sm
            from statsmodels.formula.api import ols, gls, wls, mixedlm, quantreg
            
            # Map model names to formula functions
            formula_functions = {
                "ols": ols,
                "gls": gls, 
                "wls": wls,
                "mixed_linear_model": mixedlm,
                "quantile_regression": quantreg
            }
            
            if model_name not in formula_functions:
                return {"success": False, "error": f"Formula interface not supported for {model_name}"}
            
            formula_func = formula_functions[model_name]
            # Call formula function with formula as first argument and data as keyword argument
            model = formula_func(data_prep["formula"], data=data_prep["data"])
            fitted_model = model.fit()
            
            return {"success": True, "fitted_model": fitted_model}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _fit_with_arrays(self, model_name: str, data_prep: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Fit model using array interface.
        
        Args:
            model_name: Name of the model
            data_prep: Prepared data dictionary
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing fitted model
        """
        try:
            # Import and instantiate model
            mapping = self.model_mapping[model_name]
            module = importlib.import_module(mapping["module"])
            model_class = getattr(module, mapping["class"])
            
            model = model_class(data_prep["y"], data_prep["X"], **kwargs)
            fitted_model = model.fit()
            
            return {"success": True, "fitted_model": fitted_model}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_linear_metrics(self, fitted_model, model_name: str) -> Dict[str, Any]:
        """
        Extract linear model specific metrics.
        
        Args:
            fitted_model: The fitted model object
            model_name: Name of the model
            
        Returns:
            Dictionary of metrics
        """
        # Get common metrics from base class
        metrics = self.extract_common_metrics(fitted_model, model_name)
        
        # Add linear model specific metrics
        if hasattr(fitted_model, 'rsquared'):
            metrics["r2"] = fitted_model.rsquared
        if hasattr(fitted_model, 'rsquared_adj'):
            metrics["adj_r2"] = fitted_model.rsquared_adj
        if hasattr(fitted_model, 'fvalue'):
            metrics["f_statistic"] = fitted_model.fvalue
        if hasattr(fitted_model, 'f_pvalue'):
            metrics["p_value"] = fitted_model.f_pvalue
        if hasattr(fitted_model, 'pseudo_rsquared'):
            metrics["pseudo_r2"] = fitted_model.pseudo_rsquared
        
        # Special handling for specific models
        if model_name == "rolling_regression" and hasattr(fitted_model, 'params'):
            metrics["rolling_coefficients"] = fitted_model.params.to_dict()
        
        if model_name == "mixed_linear_model" and hasattr(fitted_model, 'random_effects'):
            metrics["random_effects"] = fitted_model.random_effects
        
        return metrics


# Backward compatibility functions
def universal_linear_models(model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """
    Universal function to fit any statsmodels linear model (backward compatibility).
    
    Args:
        model_name: Name of the model from LINEAR_MODELS_MAPPING
        data: Input DataFrame
        **kwargs: Additional parameters
        
    Returns:
        Dictionary containing model fitting results
    """
    linear_models = LinearModels()
    return linear_models.fit_model(model_name, data, **kwargs)


def get_available_models() -> Dict[str, Any]:
    """
    Get list of all available models grouped by type (backward compatibility).
    
    Returns:
        Dictionary of models grouped by type
    """
    linear_models = LinearModels()
    return linear_models.get_available_models()


def validate_model_parameters(model_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate parameters for a specific model (backward compatibility).
    
    Args:
        model_name: Name of the model
        parameters: Dictionary of parameters to validate
        
    Returns:
        Validation result dictionary
    """
    linear_models = LinearModels()
    return linear_models.validate_model_parameters(model_name, parameters)


def create_langgraph_tool(model_name: str) -> Dict[str, Any]:
    """
    Create a LangGraph tool definition for a specific model (backward compatibility).
    
    Args:
        model_name: Name of the model
        
    Returns:
        Dictionary containing LangGraph tool definition
    """
    linear_models = LinearModels()
    return linear_models.create_langgraph_tool(model_name)


def extract_model_info(model_name: str) -> Dict[str, Any]:
    """
    Extract model description, parameters, and their descriptions (backward compatibility).
    
    Args:
        model_name: Name of the model in the mapping
        
    Returns:
        Dictionary containing model information
    """
    linear_models = LinearModels()
    return linear_models.extract_model_info(model_name)


def get_model_tool_description(model_name: str) -> str:
    """
    Generate a comprehensive tool description for LangGraph use (backward compatibility).
    
    Args:
        model_name: Name of the model
        
    Returns:
        Formatted tool description string
    """
    linear_models = LinearModels()
    return linear_models.get_model_tool_description(model_name)


# Example usage and testing functions
def example_usage():
    """Example usage of the universal statsmodels function."""
    import pandas as pd
    import numpy as np
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    
    # Generate synthetic data
    x1 = np.random.randn(n_samples)
    x2 = np.random.randn(n_samples)
    x3 = np.random.randn(n_samples)
    
    # Create dependent variable with some noise
    y = 2 + 1.5 * x1 + 0.8 * x2 - 0.3 * x3 + np.random.randn(n_samples) * 0.5
    
    # Create DataFrame
    data = pd.DataFrame({
        'y': y,
        'x1': x1,
        'x2': x2,
        'x3': x3
    })
    
    print("=== Universal Statsmodels Tool Example ===")
    
    # Example 1: Ordinary Least Squares
    print("\n1. Ordinary Least Squares Regression")
    result1 = universal_linear_models(
        model_name="ols",
        data=data,
        dependent_var="y",
        independent_vars=["x1", "x2", "x3"],
        add_constant=True
    )
    
    if result1['success']:
        print(f"✓ Successfully fitted {result1['model_name']}")
        print(f"  R²: {result1['metrics']['r2']:.4f}")
        print(f"  Adjusted R²: {result1['metrics']['adj_r2']:.4f}")
        print(f"  F-statistic: {result1['metrics']['f_statistic']:.4f}")
        print(f"  Coefficients: {result1['metrics']['coefficients']}")
    else:
        print(f"✗ Failed: {result1['error']}")
    
    # Example 2: Using formula interface
    print("\n2. OLS with Formula Interface")
    result2 = universal_linear_models(
        model_name="ols",
        data=data,
        dependent_var="y",
        formula="y ~ x1 + x2 + x3"
    )
    
    if result2['success']:
        print(f"✓ Successfully fitted {result2['model_name']} with formula")
        print(f"  R²: {result2['metrics']['r2']:.4f}")
        print(f"  AIC: {result2['metrics']['aic']:.4f}")
        print(f"  BIC: {result2['metrics']['bic']:.4f}")
    else:
        print(f"✗ Failed: {result2['error']}")
    
    # Example 3: Weighted Least Squares
    print("\n3. Weighted Least Squares Regression")
    # Add weights column
    data['weights'] = np.random.uniform(0.5, 2.0, n_samples)
    
    result3 = universal_linear_models(
        model_name="wls",
        data=data,
        dependent_var="y",
        independent_vars=["x1", "x2", "x3"],
        weights=data['weights']
    )
    
    if result3['success']:
        print(f"✓ Successfully fitted {result3['model_name']}")
        print(f"  R²: {result3['metrics']['r2']:.4f}")
        print(f"  Diagnostics: {result3['diagnostics']}")
    else:
        print(f"✗ Failed: {result3['error']}")


if __name__ == "__main__":
    # Print available models
    print("Available statsmodels:")
    models = get_available_models()
    for model_type, type_models in models.items():
        print(f"\n{model_type.upper()}:")
        for name, info in type_models.items():
            print(f"  - {name}: {info['description']}")
    
    # Run example usage
    print("\n" + "="*50)
    example_usage()
