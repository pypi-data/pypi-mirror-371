"""
Base class for Universal Statsmodels Tools.

This module provides a base class with common functionality that can be inherited
by specific algorithm implementations (linear models, GLM, ANOVA, etc.).
"""

import json
import inspect
import importlib
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseStatsModel(ABC):
    """
    Base class for all statsmodels algorithm implementations.
    
    This class provides common functionality including:
    - Model mapping and validation
    - Parameter extraction and validation
    - Tool description generation
    - LangGraph tool creation
    - Common utility methods
    """
    
    def __init__(self):
        """Initialize the base class with common attributes."""
        self.model_mapping = self._get_model_mapping()
        self.available_models = self._get_available_models()
    
    @abstractmethod
    def _get_model_mapping(self) -> Dict[str, Any]:
        """
        Abstract method to define the model mapping for each algorithm type.
        
        Returns:
            Dictionary mapping model names to their configurations
        """
        pass
    
    @abstractmethod
    def _get_available_models(self) -> Dict[str, Any]:
        """
        Abstract method to define available models for each algorithm type.
        
        Returns:
            Dictionary of available models grouped by type
        """
        pass
    
    @abstractmethod
    def fit_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Abstract method to fit a specific model.
        
        Args:
            model_name: Name of the model to fit
            data: Input DataFrame
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing model fitting results
        """
        pass
    
    def extract_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Extract model description, parameters, and their descriptions from docstring.
        
        Args:
            model_name: Name of the model in the mapping
            
        Returns:
            Dictionary containing model information
        """
        try:
            if model_name not in self.model_mapping:
                return {"error": f"Model '{model_name}' not found in mapping"}
            
            mapping = self.model_mapping[model_name]
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
                            param_name = line.split(' : ')[0].strip()
                            param_desc = line.split(' : ')[1].strip() if len(line.split(' : ')) > 1 else ""
                            current_param = param_name
                            parameters[param_name] = param_desc
                        elif line.startswith('    ') and current_param:
                            parameters[current_param] += " " + line.strip()
            
            # Get signature for default values - handle both classes and functions
            if inspect.isclass(model_class):
                sig = inspect.signature(model_class.__init__)
            else:
                sig = inspect.signature(model_class)
            
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
                "formula_required": mapping.get("formula_required", False),
                "docstring": docstring,
                "parameters": parameters,
                "parameter_defaults": param_defaults,
                "full_signature": str(sig)
            }
            
        except Exception as e:
            logger.error(f"Failed to extract model info for {model_name}: {str(e)}")
            return {"error": f"Failed to extract model info: {str(e)}"}
    
    def get_model_tool_description(self, model_name: str) -> str:
        """
        Generate a comprehensive tool description for LangGraph use.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Formatted tool description string
        """
        info = self.extract_model_info(model_name)
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
    
    def validate_model_parameters(self, model_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters for a specific model.
        
        Args:
            model_name: Name of the model
            parameters: Dictionary of parameters to validate
            
        Returns:
            Validation result dictionary
        """
        try:
            if model_name not in self.model_mapping:
                return {
                    "valid": False,
                    "error": f"Model '{model_name}' not found"
                }
            
            mapping = self.model_mapping[model_name]
            module = importlib.import_module(mapping["module"])
            model_class = getattr(module, mapping["class"])
            
            # Get the signature - handle both classes and functions
            if inspect.isclass(model_class):
                sig = inspect.signature(model_class.__init__)
            else:
                sig = inspect.signature(model_class)
            
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
    
    def create_langgraph_tool(self, model_name: str) -> Dict[str, Any]:
        """
        Create a LangGraph tool definition for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary containing LangGraph tool definition
        """
        info = self.extract_model_info(model_name)
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
            "description": self.get_model_tool_description(model_name),
            "parameters": parameters
        }
    
    def get_available_models(self) -> Dict[str, Any]:
        """
        Get list of all available models grouped by type.
        
        Returns:
            Dictionary of models grouped by type
        """
        return self.available_models
    
    def validate_data(self, data: pd.DataFrame, dependent_var: str = None, 
                     independent_vars: List[str] = None) -> Dict[str, Any]:
        """
        Common data validation method.
        
        Args:
            data: Input DataFrame
            dependent_var: Name of the dependent variable
            independent_vars: List of independent variable names
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check if data is empty
        if data is None or data.empty:
            validation_result["errors"].append("Data is empty or None")
            validation_result["valid"] = False
            return validation_result
        
        # Check minimum sample size (need at least 2 observations for most models)
        if len(data) < 2:
            validation_result["errors"].append("Insufficient observations: need at least 2 observations")
            validation_result["valid"] = False
            return validation_result
        
        # Check dependent variable
        if dependent_var and dependent_var not in data.columns:
            validation_result["errors"].append(
                f"Dependent variable '{dependent_var}' not found in data columns: {list(data.columns)}"
            )
            validation_result["valid"] = False
        
        # Check independent variables
        if independent_vars:
            missing_vars = [var for var in independent_vars if var not in data.columns]
            if missing_vars:
                validation_result["errors"].append(f"Independent variables not found: {missing_vars}")
                validation_result["valid"] = False
        
        # Check for missing values
        if dependent_var and data[dependent_var].isnull().any():
            validation_result["warnings"].append(f"Dependent variable '{dependent_var}' contains missing values")
        
        if independent_vars:
            for var in independent_vars:
                if data[var].isnull().any():
                    validation_result["warnings"].append(f"Independent variable '{var}' contains missing values")
        
        return validation_result
    
    def clean_data(self, data: pd.DataFrame, dependent_var: str = None, 
                  independent_vars: List[str] = None) -> pd.DataFrame:
        """
        Common data cleaning method.
        
        Args:
            data: Input DataFrame
            dependent_var: Name of the dependent variable
            independent_vars: List of independent variable names
            
        Returns:
            Cleaned DataFrame
        """
        # Create a copy to avoid modifying original data
        data_clean = data.copy()
        
        # Determine columns to check for missing values
        columns_to_check = []
        if dependent_var:
            columns_to_check.append(dependent_var)
        if independent_vars:
            columns_to_check.extend(independent_vars)
        
        # Drop rows with missing values in relevant columns
        if columns_to_check:
            data_clean = data_clean.dropna(subset=columns_to_check)
        
        # Log cleaning information
        if len(data_clean) < len(data):
            dropped_rows = len(data) - len(data_clean)
            logger.warning(f"Dropped {dropped_rows} rows with missing values")
        
        return data_clean
    
    def extract_common_metrics(self, fitted_model, model_name: str) -> Dict[str, Any]:
        """
        Extract common metrics from fitted models.
        
        Args:
            fitted_model: The fitted model object
            model_name: Name of the model
            
        Returns:
            Dictionary of common metrics
        """
        metrics = {}
        
        # Common metrics that most models have
        if hasattr(fitted_model, 'aic'):
            metrics["aic"] = fitted_model.aic
        if hasattr(fitted_model, 'bic'):
            metrics["bic"] = fitted_model.bic
        if hasattr(fitted_model, 'llf'):
            metrics["llf"] = fitted_model.llf
        if hasattr(fitted_model, 'deviance'):
            metrics["deviance"] = fitted_model.deviance
        
        # Extract coefficients
        if hasattr(fitted_model, 'params'):
            try:
                coefficients = fitted_model.params.to_dict()
                metrics["coefficients"] = coefficients
            except:
                metrics["coefficients"] = dict(fitted_model.params)
        
        # Extract standard errors
        if hasattr(fitted_model, 'bse'):
            try:
                std_errors = fitted_model.bse.to_dict()
                metrics["standard_errors"] = std_errors
            except:
                metrics["standard_errors"] = dict(fitted_model.bse)
        
        # Extract p-values
        if hasattr(fitted_model, 'pvalues'):
            try:
                p_values = fitted_model.pvalues.to_dict()
                metrics["p_values"] = p_values
            except:
                metrics["p_values"] = dict(fitted_model.pvalues)
        
        # Extract residuals
        if hasattr(fitted_model, 'resid'):
            try:
                residuals = fitted_model.resid.tolist()
                metrics["residuals"] = residuals
            except:
                metrics["residuals"] = fitted_model.resid
        
        # Extract predictions
        if hasattr(fitted_model, 'fittedvalues'):
            try:
                predictions = fitted_model.fittedvalues.tolist()
                metrics["predictions"] = predictions
            except:
                metrics["predictions"] = fitted_model.fittedvalues
        
        return metrics
    
    def run_diagnostics(self, fitted_model) -> Dict[str, Any]:
        """
        Run common diagnostic tests on fitted models.
        
        Args:
            fitted_model: The fitted model object
            
        Returns:
            Dictionary containing diagnostic results
        """
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
        
        # Model convergence (for iterative models)
        if hasattr(fitted_model, 'converged'):
            diagnostics["converged"] = fitted_model.converged
        
        # Number of iterations
        if hasattr(fitted_model, 'iterations'):
            diagnostics["iterations"] = fitted_model.iterations
        
        return diagnostics
    
    def prepare_data_for_model(self, data: pd.DataFrame, dependent_var: str = None,
                              independent_vars: List[str] = None, formula: str = None,
                              add_constant: bool = True) -> Dict[str, Any]:
        """
        Prepare data for model fitting.
        
        Args:
            data: Input DataFrame
            dependent_var: Name of the dependent variable
            independent_vars: List of independent variable names
            formula: R-style formula string
            add_constant: Whether to add constant term
            
        Returns:
            Dictionary containing prepared data
        """
        # Validate data - only check dependent_var and independent_vars if not using formula
        if formula:
            # For formula interface, just check if data is not empty
            if data is None or data.empty:
                return {"error": ["Data is empty or None"]}
        else:
            # For array interface, validate dependent_var and independent_vars
            validation = self.validate_data(data, dependent_var, independent_vars)
            if not validation["valid"]:
                return {"error": validation["errors"]}
        
        # Clean data
        data_clean = self.clean_data(data, dependent_var, independent_vars)
        
        if formula:
            # Formula interface
            return {
                "method": "formula",
                "data": data_clean,
                "formula": formula
            }
        else:
            # Array interface
            y = data_clean[dependent_var]
            X = data_clean[independent_vars]
            
            if add_constant:
                import statsmodels.api as sm
                X = sm.add_constant(X)
            
            return {
                "method": "array",
                "y": y,
                "X": X,
                "data": data_clean
            }
    
    def get_model_summary(self, fitted_model) -> str:
        """
        Get model summary as string.
        
        Args:
            fitted_model: The fitted model object
            
        Returns:
            Model summary string
        """
        try:
            return str(fitted_model.summary())
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def create_result_dict(self, model_name: str, fitted_model, data_shape: Tuple[int, int],
                          metrics: Dict[str, Any], diagnostics: Dict[str, Any] = None,
                          **kwargs) -> Dict[str, Any]:
        """
        Create a standardized result dictionary.
        
        Args:
            model_name: Name of the model
            fitted_model: The fitted model object
            data_shape: Shape of the data used
            metrics: Model metrics
            diagnostics: Model diagnostics
            **kwargs: Additional result information
            
        Returns:
            Standardized result dictionary
        """
        result = {
            "success": True,
            "model_name": model_name,
            "fitted_model": fitted_model,
            "model_summary": self.get_model_summary(fitted_model),
            "data_shape": data_shape,
            "metrics": metrics,
            "diagnostics": diagnostics or {}
        }
        
        # Add additional information
        result.update(kwargs)
        
        return result
    
    def create_error_result(self, model_name: str, error: str, **kwargs) -> Dict[str, Any]:
        """
        Create a standardized error result dictionary.
        
        Args:
            model_name: Name of the model
            error: Error message
            **kwargs: Additional error information
            
        Returns:
            Standardized error result dictionary
        """
        result = {
            "success": False,
            "error": error,
            "model_name": model_name
        }
        
        # Add additional information
        result.update(kwargs)
        
        return result
    
    def filter_model_parameters(self, model_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter parameters to only include those accepted by the model.
        
        Args:
            model_name: Name of the model
            parameters: Dictionary of parameters to filter
            
        Returns:
            Filtered parameters dictionary
        """
        try:
            if model_name not in self.model_mapping:
                return parameters
            
            mapping = self.model_mapping[model_name]
            module = importlib.import_module(mapping["module"])
            model_class = getattr(module, mapping["class"])
            
            # Get the signature - handle both classes and functions
            if inspect.isclass(model_class):
                sig = inspect.signature(model_class.__init__)
            else:
                sig = inspect.signature(model_class)
            
            # Filter parameters to only include those in the signature
            filtered_params = {}
            for param_name, param_value in parameters.items():
                if param_name in sig.parameters:
                    filtered_params[param_name] = param_value
            
            return filtered_params
            
        except Exception as e:
            logger.error(f"Error filtering parameters for {model_name}: {str(e)}")
            return parameters
       