"""
Universal Statsmodels Tool for LangGraph Agent.

This module provides a comprehensive template function that can handle all statsmodels
statistical analyses through a unified interface, making it suitable for use with LLMs in LangGraph.
Starting with linear regression models, with plans to extend to other statistical models.
"""

import json
import inspect
import importlib
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive mapping of statsmodels linear regression models
LINEAR_MODELS_MAPPING = {
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


def extract_model_info(model_name: str) -> Dict[str, Any]:
    """
    Extract model description, parameters, and their descriptions from docstring.
    
    Args:
        model_name: Name of the model in the mapping
        
    Returns:
        Dictionary containing model information
    """
    try:
        if model_name not in LINEAR_MODELS_MAPPING:
            return {"error": f"Model '{model_name}' not found in mapping"}
        
        mapping = LINEAR_MODELS_MAPPING[model_name]
        module_name = mapping["module"]
        class_name = mapping["class"]
        
        # Import the module and get the class
        module = importlib.import_module(module_name)
        model_class = getattr(module, class_name)
        
        # Get docstring
        docstring = model_class.__doc__ or ""
        
        # Extract parameters from docstring
        parameters = {}
        if docstring:
            # Simple parameter extraction from docstring
            lines = docstring.split('\n')
            in_params = False
            current_param = None
            
            for line in lines:
                line = line.strip()
                if 'Parameters' in line and '---' in line:
                    in_params = True
                    continue
                elif in_params and (line.startswith('Returns') or line.startswith('Attributes') or line.startswith('Examples')):
                    break
                elif in_params and line:
                    if ' : ' in line and not line.startswith('    '):
                        # This is a parameter name
                        param_name = line.split(' : ')[0].strip()
                        param_desc = line.split(' : ')[1].strip() if len(line.split(' : ')) > 1 else ""
                        current_param = param_name
                        parameters[param_name] = param_desc
                    elif line.startswith('    ') and current_param:
                        # This is a continuation of parameter description
                        parameters[current_param] += " " + line.strip()
        
        # Get signature for default values
        sig = inspect.signature(model_class.__init__)
        param_defaults = {}
        for name, param in sig.parameters.items():
            if name != 'self':
                if param.default != inspect.Parameter.empty:
                    param_defaults[name] = str(param.default)
                else:
                    param_defaults[name] = "Required"
        
        return {
            "model_name": model_name,
            "class_name": class_name,
            "module_name": module_name,
            "description": mapping["description"],
            "type": mapping["type"],
            "metrics": mapping["metrics"],
            "formula_required": mapping["formula_required"],
            "docstring": docstring,
            "parameters": parameters,
            "parameter_defaults": param_defaults,
            "full_signature": str(sig)
        }
        
    except Exception as e:
        logger.error(f"Failed to extract model info for {model_name}: {str(e)}")
        return {"error": f"Failed to extract model info: {str(e)}"}


def get_model_tool_description(model_name: str) -> str:
    """
    Generate a comprehensive tool description for LangGraph use.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Formatted tool description string
    """
    info = extract_model_info(model_name)
    if "error" in info:
        return f"Error: {info['error']}"
    
    description = f"""
Fit a {info['description']} ({info['class_name']}).

This tool fits a {info['type']} model using statsmodels' {info['class_name']} class.

Parameters:
"""
    
    for param_name, param_desc in info['parameters'].items():
        default = info['parameter_defaults'].get(param_name, "Required")
        description += f"- {param_name}: {param_desc} (Default: {default})\n"
    
    description += f"""
Metrics calculated: {', '.join(info['metrics'])}

Returns:
- Fitted model
- Model summary statistics
- Diagnostic plots (if requested)
- Residuals and predictions
"""
    
    return description


def universal_linear_models(
    model_name: str,
    data: pd.DataFrame,
    dependent_var: str,
    independent_vars: List[str] = None,
    formula: str = None,
    add_constant: bool = True,
    **model_params
) -> Dict[str, Any]:
    """
    Universal function to fit any statsmodels linear model.
    
    Args:
        model_name: Name of the model from LINEAR_MODELS_MAPPING
        data: Input DataFrame
        dependent_var: Name of the dependent variable
        independent_vars: List of independent variable names (not needed if formula provided)
        formula: R-style formula string (e.g., "y ~ x1 + x2")
        add_constant: Whether to add constant term to the model
        **model_params: Parameters to pass to the model
        
    Returns:
        Dictionary containing model fitting results
    """
    try:
        # Validate model name
        if model_name not in LINEAR_MODELS_MAPPING:
            return {
                "success": False,
                "error": f"Model '{model_name}' not found. Available models: {list(LINEAR_MODELS_MAPPING.keys())}"
            }
        
        mapping = LINEAR_MODELS_MAPPING[model_name]
        model_type = mapping["type"]
        formula_required = mapping["formula_required"]
        
        # Validate dependent variable
        if dependent_var not in data.columns:
            return {
                "success": False,
                "error": f"Dependent variable '{dependent_var}' not found in data columns: {list(data.columns)}"
            }
        
        # Handle missing values
        data_clean = data.dropna()
        if len(data_clean) < len(data):
            logger.warning(f"Dropped {len(data) - len(data_clean)} rows with missing values")
        
        # Prepare data based on whether formula is provided
        if formula:
            # Use formula interface
            if formula_required and not formula:
                return {
                    "success": False,
                    "error": f"Formula is required for {model_name} but not provided"
                }
            
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
                return {
                    "success": False,
                    "error": f"Formula interface not supported for {model_name}"
                }
            
            formula_func = formula_functions[model_name]
            model = formula_func(formula, data=data_clean, **model_params)
            
        else:
            # Use array interface
            if independent_vars is None:
                return {
                    "success": False,
                    "error": "Either independent_vars or formula must be provided"
                }
            
            # Validate independent variables
            missing_vars = [var for var in independent_vars if var not in data_clean.columns]
            if missing_vars:
                return {
                    "success": False,
                    "error": f"Independent variables not found: {missing_vars}"
                }
            
            # Prepare X and y
            y = data_clean[dependent_var]
            X = data_clean[independent_vars]
            
            # Add constant if requested
            if add_constant:
                import statsmodels.api as sm
                X = sm.add_constant(X)
            
            # Import and instantiate model
            module = importlib.import_module(mapping["module"])
            model_class = getattr(module, mapping["class"])
            model = model_class(y, X, **model_params)
        
        # Fit the model
        fitted_model = model.fit()
        
        # Extract results
        results = {
            "success": True,
            "model_name": model_name,
            "model_type": model_type,
            "fitted_model": fitted_model,
            "model_summary": str(fitted_model.summary()),
            "data_shape": data_clean.shape,
            "n_observations": len(data_clean),
            "n_variables": len(independent_vars) if independent_vars else None
        }
        
        # Extract metrics based on model type
        metrics = {}
        
        if hasattr(fitted_model, 'rsquared'):
            metrics["r2"] = fitted_model.rsquared
        if hasattr(fitted_model, 'rsquared_adj'):
            metrics["adj_r2"] = fitted_model.rsquared_adj
        if hasattr(fitted_model, 'aic'):
            metrics["aic"] = fitted_model.aic
        if hasattr(fitted_model, 'bic'):
            metrics["bic"] = fitted_model.bic
        if hasattr(fitted_model, 'fvalue'):
            metrics["f_statistic"] = fitted_model.fvalue
        if hasattr(fitted_model, 'f_pvalue'):
            metrics["p_value"] = fitted_model.f_pvalue
        if hasattr(fitted_model, 'pseudo_rsquared'):
            metrics["pseudo_r2"] = fitted_model.pseudo_rsquared
        
        # Extract coefficients
        if hasattr(fitted_model, 'params'):
            coefficients = fitted_model.params.to_dict()
            metrics["coefficients"] = coefficients
        
        # Extract residuals
        if hasattr(fitted_model, 'resid'):
            residuals = fitted_model.resid.tolist()
            metrics["residuals"] = residuals
        
        # Extract predictions
        if hasattr(fitted_model, 'fittedvalues'):
            predictions = fitted_model.fittedvalues.tolist()
            metrics["predictions"] = predictions
        
        # Special handling for specific models
        if model_name == "rolling_regression" and hasattr(fitted_model, 'params'):
            metrics["rolling_coefficients"] = fitted_model.params.to_dict()
        
        if model_name == "mixed_linear_model" and hasattr(fitted_model, 'random_effects'):
            metrics["random_effects"] = fitted_model.random_effects
        
        results["metrics"] = metrics
        
        # Add diagnostic information
        diagnostics = {}
        
        # Normality test on residuals
        if hasattr(fitted_model, 'resid'):
            try:
                from scipy import stats
                _, normality_p_value = stats.normaltest(fitted_model.resid)
                diagnostics["residual_normality_p_value"] = normality_p_value
            except:
                pass
        
        # Durbin-Watson test for autocorrelation
        if hasattr(fitted_model, 'resid'):
            try:
                from statsmodels.stats.diagnostic import durbin_watson
                dw_stat = durbin_watson(fitted_model.resid)
                diagnostics["durbin_watson_statistic"] = dw_stat
            except:
                pass
        
        # Breusch-Pagan test for heteroscedasticity
        if hasattr(fitted_model, 'resid') and hasattr(fitted_model, 'model'):
            try:
                from statsmodels.stats.diagnostic import het_breuschpagan
                _, _, _, bp_p_value = het_breuschpagan(fitted_model.resid, fitted_model.model.exog)
                diagnostics["breusch_pagan_p_value"] = bp_p_value
            except:
                pass
        
        results["diagnostics"] = diagnostics
        
        logger.info(f"Successfully fitted {model_name} with R²: {metrics.get('r2', 'N/A')}")
        return results
        
    except Exception as e:
        logger.error(f"Failed to fit {model_name}: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to fit {model_name}: {str(e)}",
            "model_name": model_name
        }


def get_available_models() -> Dict[str, Any]:
    """
    Get list of all available models grouped by type.
    
    Returns:
        Dictionary of models grouped by type
    """
    models_by_type = {}
    
    for name, info in LINEAR_MODELS_MAPPING.items():
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


def validate_model_parameters(model_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate parameters for a specific model.
    
    Args:
        model_name: Name of the model
        parameters: Dictionary of parameters to validate
        
    Returns:
        Validation result dictionary
    """
    try:
        if model_name not in LINEAR_MODELS_MAPPING:
            return {
                "valid": False,
                "error": f"Model '{model_name}' not found"
            }
        
        mapping = LINEAR_MODELS_MAPPING[model_name]
        module = importlib.import_module(mapping["module"])
        model_class = getattr(module, mapping["class"])
        
        # Get the signature
        sig = inspect.signature(model_class.__init__)
        
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check if all parameters are valid
        for param_name, param_value in parameters.items():
            if param_name not in sig.parameters:
                validation_result["warnings"].append(f"Unknown parameter: {param_name}")
        
        # Check for required parameters
        for param_name, param in sig.parameters.items():
            if param_name != 'self' and param.default == inspect.Parameter.empty:
                if param_name not in parameters:
                    validation_result["errors"].append(f"Missing required parameter: {param_name}")
                    validation_result["valid"] = False
        
        return validation_result
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation failed: {str(e)}"
        }


def create_langgraph_tool(model_name: str) -> Dict[str, Any]:
    """
    Create a LangGraph tool definition for a specific model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Dictionary containing LangGraph tool definition
    """
    info = extract_model_info(model_name)
    if "error" in info:
        return {"error": info["error"]}
    
    # Create parameter schema
    parameters = {
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "description": "Path to the CSV file containing the data"
            },
            "dependent_var": {
                "type": "string",
                "description": "Name of the dependent variable"
            },
            "independent_vars": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of independent variable names (not needed if formula provided)"
            },
            "formula": {
                "type": "string", 
                "description": "R-style formula string (e.g., 'y ~ x1 + x2')"
            },
            "add_constant": {
                "type": "boolean",
                "description": "Whether to add constant term to the model",
                "default": True
            }
        },
        "required": ["data", "dependent_var"]
    }
    
    # Add model-specific parameters
    for param_name, param_info in info["parameter_defaults"].items():
        if param_name not in ["data", "dependent_var", "independent_vars", "formula", "add_constant"]:
            param_type = "number" if param_info != "Required" else "string"
            parameters["properties"][param_name] = {
                "type": param_type,
                "description": info["parameters"].get(param_name, f"Parameter {param_name}"),
                "default": param_info if param_info != "Required" else None
            }
            if param_info == "Required":
                parameters["required"].append(param_name)
    
    return {
        "name": f"fit_{model_name}",
        "description": get_model_tool_description(model_name),
        "parameters": parameters
    }


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
