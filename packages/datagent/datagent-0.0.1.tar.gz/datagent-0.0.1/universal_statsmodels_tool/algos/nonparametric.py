"""
Universal Nonparametric Methods Tool for LangGraph Agent.

This module provides a comprehensive template function that can handle all statsmodels
nonparametric methods through a unified interface, making it suitable for use with LLMs in LangGraph.
Includes kernel density estimation, kernel regression, LOWESS, and asymmetric kernels.
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


class NonparametricModels(BaseStatsModel):
    """
    Nonparametric Models implementation inheriting from BaseStatsModel.
    
    Handles all nonparametric methods including kernel density estimation, 
    kernel regression, LOWESS, and asymmetric kernels.
    """
    
    def _get_model_mapping(self) -> Dict[str, Any]:
        """
        Define the model mapping for nonparametric models.
        
        Returns:
            Dictionary mapping model names to their configurations
        """
        return {
            # Kernel Density Estimation (Univariate)
            "univariate_kde": {
                "module": "statsmodels.nonparametric.kde",
                "class": "KDEUnivariate",
                "type": "density_estimation",
                "metrics": ["density", "support", "entropy", "bandwidth"],
                "description": "Univariate kernel density estimation using FFT",
                "formula_required": False,
                "default_params": {"kernel": "gau", "bw": "normal_reference"}
            },
            "multivariate_kde": {
                "module": "statsmodels.nonparametric.kernel_density",
                "class": "KDEMultivariate",
                "type": "density_estimation",
                "metrics": ["density", "support", "entropy", "bandwidth"],
                "description": "Multivariate kernel density estimation",
                "formula_required": False,
                "default_params": {"bw": "normal_reference"}
            },
            "conditional_kde": {
                "module": "statsmodels.nonparametric.kernel_density",
                "class": "KDEMultivariateConditional",
                "type": "density_estimation",
                "metrics": ["density", "support", "entropy", "bandwidth"],
                "description": "Conditional kernel density estimation",
                "formula_required": False,
                "default_params": {"bw": "normal_reference"}
            },
            
            # Kernel Regression
            "kernel_regression": {
                "module": "statsmodels.nonparametric.kernel_regression",
                "class": "KernelReg",
                "type": "regression",
                "metrics": ["fitted_values", "residuals", "r2", "bandwidth"],
                "description": "Kernel regression with local polynomial fitting",
                "formula_required": False,
                "default_params": {"bw": "aic", "kernel": "gau"}
            },
            "censored_kernel_regression": {
                "module": "statsmodels.nonparametric.kernel_regression",
                "class": "KernelCensoredReg",
                "type": "regression",
                "metrics": ["fitted_values", "residuals", "r2", "bandwidth"],
                "description": "Kernel regression for censored data",
                "formula_required": False,
                "default_params": {"bw": "aic", "kernel": "gau"}
            },
            
            # LOWESS Smoothing
            "lowess": {
                "module": "statsmodels.nonparametric.smoothers_lowess",
                "class": "lowess",
                "type": "smoothing",
                "metrics": ["fitted_values", "residuals", "smoothing"],
                "description": "Locally Weighted Scatterplot Smoothing",
                "formula_required": False,
                "default_params": {"frac": 0.3, "it": 3, "delta": 0.0}
            },
            
            # Asymmetric Kernels for Density Estimation
            "beta_kernel_pdf": {
                "module": "statsmodels.nonparametric.kernels_asymmetric",
                "class": "kernel_pdf_beta",
                "type": "asymmetric_kernel",
                "metrics": ["density", "support", "bandwidth"],
                "description": "Beta kernel for density estimation with boundary corrections",
                "formula_required": False,
                "default_params": {"bw": "silverman"}
            },
            "gamma_kernel_pdf": {
                "module": "statsmodels.nonparametric.kernels_asymmetric",
                "class": "kernel_pdf_gamma",
                "type": "asymmetric_kernel",
                "metrics": ["density", "support", "bandwidth"],
                "description": "Gamma kernel for density estimation",
                "formula_required": False,
                "default_params": {"bw": "silverman"}
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
                "default_params": info.get("default_params", {})
            }
        
        return models_by_type
    
    def fit_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Fit a nonparametric model using the specified model name.
        
        Args:
            model_name: Name of the model from model mapping
            data: Input DataFrame
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing model fitting results
        """
        try:
            if model_name not in self.model_mapping:
                return self.create_error_result(
                    model_name,
                    f"Model '{model_name}' not found. Available models: {list(self.model_mapping.keys())}"
                )
            
            mapping = self.model_mapping[model_name]
            module_name = mapping["module"]
            class_name = mapping["class"]
            
            # Import the module and class
            module = importlib.import_module(module_name)
            model_class = getattr(module, class_name)
            
            # Set default parameters
            default_params = mapping.get("default_params", {})
            for key, value in default_params.items():
                if key not in kwargs:
                    kwargs[key] = value
            
            # Handle different model types
            model_type = mapping["type"]
            fitted_model = None
            metrics = {}
            
            # Extract parameters
            dependent_var = kwargs.get('dependent_var')
            independent_vars = kwargs.get('independent_vars')
            variables = kwargs.get('variables')
            x_col = kwargs.get('x_col')
            y_col = kwargs.get('y_col')
            
            # Filter kwargs to only include model-specific parameters
            model_kwargs = self.filter_model_parameters(model_name, kwargs)
            
            if model_type == "density_estimation":
                # Handle density estimation models
                if variables is None:
                    # Use first numeric column if no variables specified
                    numeric_cols = data.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) == 0:
                        return self.create_error_result(model_name, "No numeric columns found for density estimation")
                    variables = [numeric_cols[0]]
                
                if len(variables) == 1:
                    # Univariate density estimation
                    if model_name == "univariate_kde":
                        kde = model_class(data[variables[0]])
                        kde.fit(**model_kwargs)
                        fitted_model = kde
                        
                        # Calculate metrics
                        metrics = {
                            "bandwidth": kde.bw,
                            "entropy": kde.entropy if hasattr(kde, 'entropy') else None,
                            "support_min": kde.support[0] if hasattr(kde, 'support') and len(kde.support) > 0 else None,
                            "support_max": kde.support[-1] if hasattr(kde, 'support') and len(kde.support) > 0 else None
                        }
                    else:
                        # Asymmetric kernel density estimation
                        sample = data[variables[0]].dropna()
                        if len(sample) == 0:
                            return self.create_error_result(model_name, "No valid data for density estimation")
                        
                        # Get bandwidth
                        bw = kwargs.get('bw', 'silverman')
                        if bw == 'silverman':
                            from statsmodels.nonparametric.bandwidths import bw_silverman
                            bandwidth = bw_silverman(sample)
                        elif bw == 'scott':
                            from statsmodels.nonparametric.bandwidths import bw_scott
                            bandwidth = bw_scott(sample)
                        else:
                            bandwidth = bw
                        
                        # Create evaluation points
                        x_eval = np.linspace(sample.min(), sample.max(), 100)
                        
                        # Calculate density using the kernel function
                        density = model_class(x_eval, sample, bandwidth)
                        
                        fitted_model = {
                            "kernel_function": model_class,
                            "sample": sample,
                            "bandwidth": bandwidth,
                            "x_eval": x_eval,
                            "density": density
                        }
                        
                        metrics = {
                            "bandwidth": bandwidth,
                            "sample_size": len(sample),
                            "support_min": sample.min(),
                            "support_max": sample.max()
                        }
                else:
                    # Multivariate density estimation
                    # KDEMultivariate requires var_type parameter
                    # Determine var_type based on data types
                    var_types = []
                    for var in variables:
                        if data[var].dtype in ['object', 'category']:
                            var_types.append('o')  # ordered
                        else:
                            var_types.append('c')  # continuous
                    
                    kde = model_class(data[variables], var_types, **model_kwargs)
                    fitted_model = kde
                    
                    metrics = {
                        "bandwidth": kde.bw if hasattr(kde, 'bw') else None,
                        "sample_size": len(data),
                        "dimensions": len(variables)
                    }
            
            elif model_type == "regression":
                # Handle kernel regression models
                if dependent_var is None or independent_vars is None:
                    return self.create_error_result(model_name, "Both dependent_var and independent_vars required for regression models")
                
                if model_name == "kernel_regression":
                    # Kernel regression
                    endog = data[dependent_var]
                    exog = data[independent_vars]
                    
                    # KernelReg requires var_type parameter
                    # Determine var_type based on data types
                    var_types = []
                    for col in independent_vars:
                        if data[col].dtype in ['object', 'category']:
                            var_types.append('o')  # ordered
                        else:
                            var_types.append('c')  # continuous
                    
                    # Remove kernel parameter if it's not supported
                    kernel_params = model_kwargs.copy()
                    if 'kernel' in kernel_params:
                        del kernel_params['kernel']
                    
                    kr = model_class(endog, exog, var_types, **kernel_params)
                    fitted_model = kr
                    
                    # Get fitted values and residuals
                    fitted_values = kr.fit()[0]
                    residuals = endog - fitted_values
                    
                    # Calculate R-squared
                    ss_res = np.sum(residuals**2)
                    ss_tot = np.sum((endog - np.mean(endog))**2)
                    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                    
                    metrics = {
                        "r2": r2,
                        "residuals_mean": np.mean(residuals),
                        "residuals_std": np.std(residuals),
                        "bandwidth": kr.bw if hasattr(kr, 'bw') else None
                    }
                
                elif model_name == "censored_kernel_regression":
                    # Censored kernel regression
                    endog = data[dependent_var]
                    exog = data[independent_vars]
                    
                    # Assume no censoring for now (can be extended)
                    kr = model_class(endog, exog, **model_kwargs)
                    fitted_model = kr
                    
                    fitted_values = kr.fit()[0]
                    residuals = endog - fitted_values
                    
                    ss_res = np.sum(residuals**2)
                    ss_tot = np.sum((endog - np.mean(endog))**2)
                    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                    
                    metrics = {
                        "r2": r2,
                        "residuals_mean": np.mean(residuals),
                        "residuals_std": np.std(residuals),
                        "bandwidth": kr.bw if hasattr(kr, 'bw') else None
                    }
            
            elif model_type == "smoothing":
                # Handle LOWESS smoothing
                if x_col is None or y_col is None:
                    return self.create_error_result(model_name, "Both x_col and y_col required for smoothing models")
                
                if model_name == "lowess":
                    x_data = data[x_col]
                    y_data = data[y_col]
                    
                    # Apply LOWESS smoothing
                    # LOWESS expects 1D arrays and returns (x, y) pairs
                    lowess_result = model_class(y_data, x_data, **model_kwargs)
                    
                    # Extract smoothed y values (second column)
                    smoothed = lowess_result[:, 1]
                    
                    fitted_model = {
                        "smoothed_values": smoothed,
                        "x_data": x_data,
                        "y_data": y_data,
                        "lowess_result": lowess_result
                    }
                    
                    # Calculate residuals
                    residuals = y_data - smoothed
                    
                    metrics = {
                        "residuals_mean": np.mean(residuals),
                        "residuals_std": np.std(residuals),
                        "smoothing_frac": kwargs.get('frac', 0.3),
                        "iterations": kwargs.get('it', 3)
                    }
            
            elif model_type == "asymmetric_kernel":
                # Handle asymmetric kernel models
                if variables is None:
                    numeric_cols = data.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) == 0:
                        return self.create_error_result(model_name, "No numeric columns found for asymmetric kernel estimation")
                    variables = [numeric_cols[0]]
                
                sample = data[variables[0]].dropna()
                if len(sample) == 0:
                    return self.create_error_result(model_name, "No valid data for asymmetric kernel estimation")
                
                # Get bandwidth
                bw = kwargs.get('bw', 'silverman')
                if bw == 'silverman':
                    from statsmodels.nonparametric.bandwidths import bw_silverman
                    bandwidth = bw_silverman(sample)
                elif bw == 'scott':
                    from statsmodels.nonparametric.bandwidths import bw_scott
                    bandwidth = bw_scott(sample)
                else:
                    bandwidth = bw
                
                # Create evaluation points
                x_eval = np.linspace(sample.min(), sample.max(), 100)
                
                # Calculate density or CDF using the kernel function
                # Asymmetric kernel functions expect (x, sample, bandwidth) order
                # We need to calculate the density at each evaluation point
                result = np.array([model_class(x, sample, bandwidth) for x in x_eval])
                
                fitted_model = {
                    "kernel_function": model_class,
                    "sample": sample,
                    "bandwidth": bandwidth,
                    "x_eval": x_eval,
                    "result": result
                }
                
                metrics = {
                    "bandwidth": bandwidth,
                    "sample_size": len(sample),
                    "support_min": sample.min(),
                    "support_max": sample.max()
                }
            
            else:
                return self.create_error_result(model_name, f"Unknown model type: {model_type}")
            
            return {
                "success": True,
                "model_name": model_name,
                "model_type": model_type,
                "fitted_model": fitted_model,
                "metrics": metrics,
                "parameters": kwargs,
                "data_shape": data.shape,
                "variables_used": variables if variables else (dependent_var, independent_vars)
            }
            
        except Exception as e:
            logger.error(f"Error fitting {model_name}: {str(e)}")
            return self.create_error_result(model_name, f"Failed to fit {model_name}: {str(e)}")


# Backward compatibility functions
def universal_nonparametric(model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """
    Universal function to fit any statsmodels nonparametric model (backward compatibility).
    
    Args:
        model_name: Name of the nonparametric model to use
        data: DataFrame containing the data
        **kwargs: Additional model-specific parameters
        
    Returns:
        Dictionary containing model results, metrics, and diagnostics
    """
    nonparametric_models = NonparametricModels()
    return nonparametric_models.fit_model(model_name, data, **kwargs)


def get_available_models() -> Dict[str, Any]:
    """
    Get list of all available nonparametric models grouped by type (backward compatibility).
    
    Returns:
        Dictionary of models grouped by type
    """
    nonparametric_models = NonparametricModels()
    return nonparametric_models.get_available_models()


def validate_model_parameters(model_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate parameters for a specific nonparametric model (backward compatibility).
    
    Args:
        model_name: Name of the model
        parameters: Parameters to validate
        
    Returns:
        Dictionary with validation results
    """
    nonparametric_models = NonparametricModels()
    return nonparametric_models.validate_model_parameters(model_name, parameters)


def create_langgraph_tool(model_name: str) -> Dict[str, Any]:
    """
    Create a LangGraph tool definition for a specific nonparametric model (backward compatibility).
    
    Args:
        model_name: Name of the model
        
    Returns:
        LangGraph tool definition
    """
    nonparametric_models = NonparametricModels()
    return nonparametric_models.create_langgraph_tool(model_name)


def extract_model_info(model_name: str) -> Dict[str, Any]:
    """
    Extract model description, parameters, and their descriptions (backward compatibility).
    
    Args:
        model_name: Name of the model in the mapping
        
    Returns:
        Dictionary containing model information
    """
    nonparametric_models = NonparametricModels()
    return nonparametric_models.extract_model_info(model_name)


def get_model_tool_description(model_name: str) -> str:
    """
    Generate a comprehensive tool description for LangGraph use (backward compatibility).
    
    Args:
        model_name: Name of the model
        
    Returns:
        Formatted tool description
    """
    nonparametric_models = NonparametricModels()
    return nonparametric_models.get_model_tool_description(model_name)


# Example usage and testing functions
def example_usage():
    """
    Example usage of the universal nonparametric function.
    """
    print("=== Nonparametric Methods Examples ===\n")
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    
    # Create synthetic data
    x = np.random.randn(n_samples)
    y = 2 + 1.5 * x + 0.8 * x**2 + np.random.randn(n_samples) * 0.5
    
    # Create DataFrame
    data = pd.DataFrame({
        'x': x,
        'y': y,
        'positive_data': np.abs(x) + np.random.exponential(1, n_samples)
    })
    
    print("1. Univariate Kernel Density Estimation:")
    result = universal_nonparametric(
        model_name="univariate_kde",
        data=data,
        variables=["x"]
    )
    print(f"Success: {result['success']}")
    print(f"Bandwidth: {result['metrics']['bandwidth']:.4f}")
    print()
    
    print("2. Kernel Regression:")
    result = universal_nonparametric(
        model_name="kernel_regression",
        data=data,
        dependent_var="y",
        independent_vars=["x"]
    )
    print(f"Success: {result['success']}")
    print(f"R-squared: {result['metrics']['r2']:.4f}")
    print()
    
    print("3. LOWESS Smoothing:")
    result = universal_nonparametric(
        model_name="lowess",
        data=data,
        x_col="x",
        y_col="y",
        frac=0.3
    )
    print(f"Success: {result['success']}")
    print(f"Residuals std: {result['metrics']['residuals_std']:.4f}")
    print()
    
    print("4. Beta Kernel Density Estimation:")
    result = universal_nonparametric(
        model_name="beta_kernel_pdf",
        data=data,
        variables=["positive_data"]
    )
    print(f"Success: {result['success']}")
    print(f"Bandwidth: {result['metrics']['bandwidth']:.4f}")
    print()
    
    print("5. Available Models by Type:")
    models = get_available_models()
    for model_type, type_models in models.items():
        print(f"\n{model_type.upper()}:")
        for model_name, model_info in type_models.items():
            print(f"  - {model_name}: {model_info['description']}")


if __name__ == "__main__":
    # Print available models and run examples
    print("Available Nonparametric Models:")
    models = get_available_models()
    for model_type, type_models in models.items():
        print(f"\n{model_type.upper()}:")
        for model_name in type_models.keys():
            print(f"  - {model_name}")
    
    print("\n" + "="*50)
    example_usage()
