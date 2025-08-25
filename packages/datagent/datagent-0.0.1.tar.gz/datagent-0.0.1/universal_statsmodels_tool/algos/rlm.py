"""
Universal Robust Linear Models (RLM) Tool for LangGraph Agent.

This module provides a comprehensive template function that can handle all statsmodels
robust linear models through a unified interface, making it suitable for use with LLMs in LangGraph.
Supports various M-estimators and robust regression techniques for handling outliers and influential observations.
"""

import json
import inspect
import importlib
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
import logging
import statsmodels.api as sm
from .base_model import BaseStatsModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RLMModels(BaseStatsModel):
    """
    Robust Linear Models implementation inheriting from BaseStatsModel.
    
    Handles all robust linear models including various M-estimators for handling outliers.
    """
    
    def _get_model_mapping(self) -> Dict[str, Any]:
        """
        Define the model mapping for robust linear models.
        
        Returns:
            Dictionary mapping model names to their configurations
        """
        return {
            # Robust Linear Models with different M-estimators
            "rlm_huber": {
                "module": "statsmodels.robust.robust_linear_model",
                "class": "RLM",
                "norm": "HuberT",
                "type": "robust_regression",
                "metrics": ["aic", "bic", "deviance", "residuals", "coefficients", "scale", "weights"],
                "description": "Robust Linear Model with Huber's T norm (default)",
                "formula_required": False,
                "default_params": {"M": "HuberT()"}
            },
            "rlm_tukey_biweight": {
                "module": "statsmodels.robust.robust_linear_model",
                "class": "RLM",
                "norm": "TukeyBiweight",
                "type": "robust_regression",
                "metrics": ["aic", "bic", "deviance", "residuals", "coefficients", "scale", "weights"],
                "description": "Robust Linear Model with Tukey's biweight norm",
                "formula_required": False,
                "default_params": {"M": "TukeyBiweight()"}
            },
            "rlm_hampel": {
                "module": "statsmodels.robust.robust_linear_model",
                "class": "RLM",
                "norm": "Hampel",
                "type": "robust_regression",
                "metrics": ["aic", "bic", "deviance", "residuals", "coefficients", "scale", "weights"],
                "description": "Robust Linear Model with Hampel function",
                "formula_required": False,
                "default_params": {"M": "Hampel()"}
            },
            "rlm_andrew_wave": {
                "module": "statsmodels.robust.robust_linear_model",
                "class": "RLM",
                "norm": "AndrewWave",
                "type": "robust_regression",
                "metrics": ["aic", "bic", "deviance", "residuals", "coefficients", "scale", "weights"],
                "description": "Robust Linear Model with Andrew's wave norm",
                "formula_required": False,
                "default_params": {"M": "AndrewWave()"}
            },
            "rlm_ramsay_e": {
                "module": "statsmodels.robust.robust_linear_model",
                "class": "RLM",
                "norm": "RamsayE",
                "type": "robust_regression",
                "metrics": ["aic", "bic", "deviance", "residuals", "coefficients", "scale", "weights"],
                "description": "Robust Linear Model with Ramsay's Ea norm",
                "formula_required": False,
                "default_params": {"M": "RamsayE()"}
            },
            "rlm_trimmed_mean": {
                "module": "statsmodels.robust.robust_linear_model",
                "class": "RLM",
                "norm": "TrimmedMean",
                "type": "robust_regression",
                "metrics": ["aic", "bic", "deviance", "residuals", "coefficients", "scale", "weights"],
                "description": "Robust Linear Model with trimmed mean norm",
                "formula_required": False,
                "default_params": {"M": "TrimmedMean()"}
            },
            "rlm_least_squares": {
                "module": "statsmodels.robust.robust_linear_model",
                "class": "RLM",
                "norm": "LeastSquares",
                "type": "robust_regression",
                "metrics": ["aic", "bic", "deviance", "residuals", "coefficients", "scale", "weights"],
                "description": "Robust Linear Model with least squares norm (equivalent to OLS)",
                "formula_required": False,
                "default_params": {"M": "LeastSquares()"}
            },
            "rlm_m_quantile": {
                "module": "statsmodels.robust.robust_linear_model",
                "class": "RLM",
                "norm": "MQuantileNorm",
                "type": "robust_regression",
                "metrics": ["aic", "bic", "deviance", "residuals", "coefficients", "scale", "weights"],
                "description": "Robust Linear Model with M-quantiles norm",
                "formula_required": False,
                "default_params": {"M": "MQuantileNorm(0.5, HuberT())"},
                "special_handling": True
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
                "formula_required": info.get("formula_required", False),
                "norm": info.get("norm", "Not specified")
            }
        
        return models_by_type
    
    def fit_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Fit a robust linear model using the specified model name.
        
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
            
            # Extract common parameters
            dependent_var = kwargs.get('dependent_var')
            independent_vars = kwargs.get('independent_vars')
            formula = kwargs.get('formula')
            
            # Validate inputs
            if data.empty:
                return self.create_error_result(model_name, "Data is empty")
            
            if dependent_var and dependent_var not in data.columns:
                return self.create_error_result(
                    model_name,
                    f"Dependent variable '{dependent_var}' not found in data columns: {list(data.columns)}"
                )
            
            module_name = mapping["module"]
            class_name = mapping["class"]
            
            # Import required modules
            module = importlib.import_module(module_name)
            model_class = getattr(module, class_name)
            
            # Import robust norms if needed
            if "norm" in mapping:
                norms_module = importlib.import_module("statsmodels.robust.norms")
                norm_class = getattr(norms_module, mapping["norm"])
                
                # Special handling for MQuantileNorm
                if mapping["norm"] == "MQuantileNorm":
                    try:
                        # Create base norm first
                        base_norm_class = getattr(norms_module, "HuberT")
                        base_norm = base_norm_class()
                        
                        # Create MQuantileNorm with base norm
                        norm_instance = norm_class(0.5, base_norm)
                        kwargs["M"] = norm_instance
                    except Exception as e:
                        logger.warning(f"Failed to create MQuantileNorm, falling back to HuberT: {str(e)}")
                        # Fallback to HuberT
                        norm_class = getattr(norms_module, "HuberT")
                        norm_instance = norm_class()
                        kwargs["M"] = norm_instance
                else:
                    # Create norm instance with default or provided parameters
                    norm_params = self._get_norm_default_params(mapping["norm"])
                    norm_params.update(kwargs.get("norm_params", {}))
                    norm_instance = norm_class(**norm_params)
                    
                    # Update kwargs with the norm instance
                    kwargs["M"] = norm_instance
            
            # Prepare data
            if formula and mapping.get("formula_required", False):
                # Use formula interface
                y = data[dependent_var]
                model = model_class.from_formula(formula, data=data, **kwargs)
            else:
                # Use array interface
                y = data[dependent_var]
                if independent_vars:
                    if not all(var in data.columns for var in independent_vars):
                        missing_vars = [var for var in independent_vars if var not in data.columns]
                        return self.create_error_result(model_name, f"Independent variables not found: {missing_vars}")
                    X = data[independent_vars]
                else:
                    # Use all columns except dependent variable
                    X = data.drop(columns=[dependent_var])
                
                # Add constant if not present
                if not any(X.columns.str.contains('const|intercept', case=False)):
                    X = sm.add_constant(X)
                
                model = model_class(y, X, **kwargs)
            
            # Fit the model
            fitted_model = model.fit()
            
            # Extract results
            results = {
                "success": True,
                "model_name": model_name,
                "fitted_model": fitted_model,
                "coefficients": fitted_model.params.to_dict() if hasattr(fitted_model.params, 'to_dict') else dict(fitted_model.params),
                "standard_errors": fitted_model.bse.to_dict() if hasattr(fitted_model.bse, 'to_dict') else dict(fitted_model.bse),
                "p_values": fitted_model.pvalues.to_dict() if hasattr(fitted_model.pvalues, 'to_dict') else dict(fitted_model.pvalues),
                "residuals": fitted_model.resid.tolist(),
                "fitted_values": fitted_model.fittedvalues.tolist(),
                "n_observations": fitted_model.nobs,
                "df_resid": fitted_model.df_resid,
                "df_model": fitted_model.df_model
            }
            
            # Add robust-specific metrics
            if hasattr(fitted_model, 'scale'):
                results["scale"] = fitted_model.scale
            
            if hasattr(fitted_model, 'weights'):
                results["weights"] = fitted_model.weights.tolist()
            
            if hasattr(fitted_model, 'deviance'):
                results["deviance"] = fitted_model.deviance
            
            # Add model diagnostics
            diagnostics = {}
            
            # AIC and BIC if available
            if hasattr(fitted_model, 'aic'):
                diagnostics["aic"] = fitted_model.aic
            if hasattr(fitted_model, 'bic'):
                diagnostics["bic"] = fitted_model.bic
            
            # Model summary
            try:
                summary_str = str(fitted_model.summary())
                diagnostics["summary"] = summary_str
            except Exception as e:
                diagnostics["summary_error"] = str(e)
            
            results["diagnostics"] = diagnostics
            
            # Add model info
            results["model_info"] = {
                "description": mapping["description"],
                "type": mapping["type"],
                "available_metrics": mapping["metrics"],
                "formula_used": formula if formula else None,
                "independent_vars": independent_vars if independent_vars else list(X.columns),
                "dependent_var": dependent_var
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error fitting robust linear model {model_name}: {str(e)}")
            return self.create_error_result(model_name, f"Failed to fit model: {str(e)}")
    
    def _get_norm_default_params(self, norm_name: str) -> Dict[str, Any]:
        """
        Get default parameters for a specific norm.
        
        Args:
            norm_name: Name of the norm
            
        Returns:
            Dictionary of default parameters
        """
        norm_defaults = {
            "HuberT": {"t": 1.345},
            "TukeyBiweight": {"c": 4.685},
            "Hampel": {"a": 2.0, "b": 4.0, "c": 8.0},
            "AndrewWave": {"a": 1.339},
            "RamsayE": {"a": 0.3},
            "TrimmedMean": {"c": 2.0},
            "LeastSquares": {},
            "MQuantileNorm": {"q": 0.5, "base_norm": "HuberT()"}
        }
        
        return norm_defaults.get(norm_name, {})


# Backward compatibility functions
def universal_rlm(model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """
    Universal function to fit any statsmodels robust linear model (backward compatibility).
    
    Args:
        model_name: Name of the robust linear model to use
        data: Input DataFrame
        **kwargs: Additional parameters
        
    Returns:
        Dictionary containing model results, metrics, and diagnostics
    """
    rlm_models = RLMModels()
    return rlm_models.fit_model(model_name, data, **kwargs)


def get_available_models() -> Dict[str, Any]:
    """
    Get list of all available robust linear models grouped by type (backward compatibility).
    
    Returns:
        Dictionary containing all available models with their descriptions
    """
    rlm_models = RLMModels()
    return rlm_models.get_available_models()


def validate_model_parameters(model_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate parameters for a specific robust linear model (backward compatibility).
    
    Args:
        model_name: Name of the model to validate parameters for
        parameters: Dictionary of parameters to validate
        
    Returns:
        Dictionary with validation results
    """
    rlm_models = RLMModels()
    return rlm_models.validate_model_parameters(model_name, parameters)


def create_langgraph_tool(model_name: str) -> Dict[str, Any]:
    """
    Create a LangGraph tool definition for a specific robust linear model (backward compatibility).
    
    Args:
        model_name: Name of the model to create a tool for
        
    Returns:
        Dictionary containing LangGraph tool definition
    """
    rlm_models = RLMModels()
    return rlm_models.create_langgraph_tool(model_name)


def extract_model_info(model_name: str) -> Dict[str, Any]:
    """
    Extract model description, parameters, and their descriptions (backward compatibility).
    
    Args:
        model_name: Name of the model in the mapping
        
    Returns:
        Dictionary containing model information
    """
    rlm_models = RLMModels()
    return rlm_models.extract_model_info(model_name)


def get_model_tool_description(model_name: str) -> str:
    """
    Generate a comprehensive tool description for LangGraph use (backward compatibility).
    
    Args:
        model_name: Name of the model in the mapping
        
    Returns:
        String description of the model and its capabilities
    """
    rlm_models = RLMModels()
    return rlm_models.get_model_tool_description(model_name)


# Example usage and testing functions
def example_usage():
    """
    Example usage of the universal robust linear model function.
    """
    print("=== Robust Linear Models Example Usage ===\n")
    
    # Create sample data with outliers
    np.random.seed(42)
    n_samples = 100
    
    # Generate clean data
    x1 = np.random.randn(n_samples)
    x2 = np.random.randn(n_samples)
    y_clean = 2 + 1.5 * x1 + 0.8 * x2 + np.random.randn(n_samples) * 0.5
    
    # Add outliers
    outliers_idx = np.random.choice(n_samples, size=5, replace=False)
    y_with_outliers = y_clean.copy()
    y_with_outliers[outliers_idx] += 10  # Add large outliers
    
    # Create DataFrame
    data = pd.DataFrame({
        'y': y_with_outliers,
        'x1': x1,
        'x2': x2
    })
    
    print("Sample data with outliers created.")
    print(f"Data shape: {data.shape}")
    print(f"Outliers added at indices: {outliers_idx}")
    print()
    
    # Test different robust models
    models_to_test = ["rlm_huber", "rlm_tukey_biweight", "rlm_hampel"]
    
    for model_name in models_to_test:
        print(f"Testing {model_name}...")
        
        try:
            result = universal_rlm(
                model_name=model_name,
                data=data,
                dependent_var="y",
                independent_vars=["x1", "x2"]
            )
            
            if result["success"]:
                print(f"✓ {model_name} fitted successfully")
                print(f"  Coefficients: {result['coefficients']}")
                print(f"  Scale: {result.get('scale', 'N/A')}")
                print(f"  Observations: {result['n_observations']}")
                print()
            else:
                print(f"✗ {model_name} failed: {result['error']}")
                print()
                
        except Exception as e:
            print(f"✗ {model_name} exception: {str(e)}")
            print()
    
    print("=== Example completed ===")


if __name__ == "__main__":
    # Print available models
    print("Available Robust Linear Models:")
    models = get_available_models()
    for model_type, type_models in models.items():
        print(f"\n{model_type.upper()}:")
        for model_name, info in type_models.items():
            print(f"  - {model_name}: {info['description']}")
            print(f"    Norm: {info['norm']}")
            print(f"    Metrics: {', '.join(info['metrics'])}")
    
    print("\n" + "="*50)
    
    # Run example
    example_usage()
