"""
Universal Generalized Linear Models (GLM) Tool for LangGraph Agent.

This module provides a comprehensive template function that can handle all statsmodels
generalized linear models through a unified interface, making it suitable for use with LLMs in LangGraph.
Supports various GLM families (Gaussian, Binomial, Poisson, Gamma, etc.) and link functions.
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


class GLMModels(BaseStatsModel):
    """
    Generalized Linear Models implementation inheriting from BaseStatsModel.
    
    Handles all GLM models including various families (Gaussian, Binomial, Poisson, etc.)
    and discrete choice models (Logit, Probit, etc.).
    """
    
    def _get_model_mapping(self) -> Dict[str, Any]:
        """
        Define the model mapping for GLM models.
        
        Returns:
            Dictionary mapping model names to their configurations
        """
        return {
            # GLM with different families
            "gaussian_glm": {
                "module": "statsmodels.genmod.generalized_linear_model",
                "class": "GLM",
                "family": "Gaussian",
                "type": "glm",
                "metrics": ["aic", "bic", "deviance", "pearson_chi2", "pseudo_r2", "llf"],
                "description": "GLM with Gaussian family (normal distribution)",
                "formula_required": False,
                "default_link": "identity",
                "links": ["identity", "log", "inverse"]
            },
            "binomial_glm": {
                "module": "statsmodels.genmod.generalized_linear_model",
                "class": "GLM",
                "family": "Binomial",
                "type": "glm",
                "metrics": ["aic", "bic", "deviance", "pearson_chi2", "pseudo_r2", "llf"],
                "description": "GLM with Binomial family (logistic regression)",
                "formula_required": False,
                "default_link": "logit",
                "links": ["logit", "probit", "cloglog"]
            },
            "poisson_glm": {
                "module": "statsmodels.genmod.generalized_linear_model",
                "class": "GLM",
                "family": "Poisson",
                "type": "glm",
                "metrics": ["aic", "bic", "deviance", "pearson_chi2", "pseudo_r2", "llf"],
                "description": "GLM with Poisson family (count data)",
                "formula_required": False,
                "default_link": "log",
                "links": ["log", "identity", "sqrt"]
            },
            "gamma_glm": {
                "module": "statsmodels.genmod.generalized_linear_model",
                "class": "GLM",
                "family": "Gamma",
                "type": "glm",
                "metrics": ["aic", "bic", "deviance", "pearson_chi2", "pseudo_r2", "llf"],
                "description": "GLM with Gamma family (positive continuous data)",
                "formula_required": False,
                "default_link": "inverse_power",
                "links": ["log", "inverse", "inverse_power"]
            },
            "inverse_gaussian_glm": {
                "module": "statsmodels.genmod.generalized_linear_model",
                "class": "GLM",
                "family": "InverseGaussian",
                "type": "glm",
                "metrics": ["aic", "bic", "deviance", "pearson_chi2", "pseudo_r2", "llf"],
                "description": "GLM with Inverse Gaussian family",
                "formula_required": False,
                "default_link": "inverse_power",
                "links": ["inverse", "inverse_power", "log"]
            },
            "negative_binomial_glm": {
                "module": "statsmodels.genmod.generalized_linear_model",
                "class": "GLM",
                "family": "NegativeBinomial",
                "type": "glm",
                "metrics": ["aic", "bic", "deviance", "pearson_chi2", "pseudo_r2", "llf"],
                "description": "GLM with Negative Binomial family (overdispersed count data)",
                "formula_required": False,
                "default_link": "log",
                "links": ["log", "identity"]
            },
            "tweedie_glm": {
                "module": "statsmodels.genmod.generalized_linear_model",
                "class": "GLM",
                "family": "Tweedie",
                "type": "glm",
                "metrics": ["aic", "bic", "deviance", "pearson_chi2", "pseudo_r2", "llf"],
                "description": "GLM with Tweedie family (flexible distribution)",
                "formula_required": False,
                "default_link": "log",
                "links": ["log", "identity"]
            },
            # Discrete choice models (specialized GLMs)
            "logit": {
                "module": "statsmodels.discrete.discrete_model",
                "class": "Logit",
                "family": "Binomial",
                "type": "glm",
                "metrics": ["aic", "bic", "llf", "pseudo_r2", "confusion_matrix"],
                "description": "Logit model for binary choice",
                "formula_required": True,
                "default_link": "logit",
                "links": ["logit", "probit"]
            },
            "probit": {
                "module": "statsmodels.discrete.discrete_model",
                "class": "Probit",
                "family": "Binomial",
                "type": "glm",
                "metrics": ["aic", "bic", "llf", "pseudo_r2", "confusion_matrix"],
                "description": "Probit model for binary choice",
                "formula_required": True,
                "default_link": "probit",
                "links": ["probit", "logit"]
            },
            "multinomial_logit": {
                "module": "statsmodels.discrete.discrete_model",
                "class": "MNLogit",
                "family": "Multinomial",
                "type": "glm",
                "metrics": ["aic", "bic", "llf", "pseudo_r2"],
                "description": "Multinomial Logit model for multiple choice",
                "formula_required": True,
                "default_link": "logit",
                "links": ["logit"]
            },
            "ordered_logit": {
                "module": "statsmodels.discrete.discrete_model",
                "class": "OrderedModel",
                "family": "Ordered",
                "type": "glm",
                "metrics": ["aic", "bic", "llf", "pseudo_r2"],
                "description": "Ordered Logit model for ordinal data",
                "formula_required": True,
                "default_link": "logit",
                "links": ["logit", "probit"]
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
                "family": info["family"],
                "metrics": info["metrics"],
                "formula_required": info["formula_required"],
                "default_link": info["default_link"]
            }
        
        return models_by_type
    
    def fit_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Fit a GLM model using the specified model name.
        
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
            family_name = mapping["family"]
            default_link = mapping["default_link"]
            
            # Extract common parameters
            dependent_var = kwargs.get('dependent_var')
            independent_vars = kwargs.get('independent_vars')
            formula = kwargs.get('formula')
            add_constant = kwargs.get('add_constant', True)
            family_params = kwargs.get('family_params', {})
            link_name = kwargs.get('link_name', default_link)
            link_params = kwargs.get('link_params', {})
            
            # Remove extracted parameters from kwargs to avoid conflicts
            kwargs.pop('dependent_var', None)
            kwargs.pop('independent_vars', None)
            kwargs.pop('formula', None)
            kwargs.pop('add_constant', None)
            kwargs.pop('family_params', None)
            kwargs.pop('link_name', None)
            kwargs.pop('link_params', None)
            
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
                fitted_model = self._fit_with_formula(model_name, data_prep, family_name, 
                                                    family_params, link_name, link_params, **kwargs)
            else:
                fitted_model = self._fit_with_arrays(model_name, data_prep, family_name, 
                                                   family_params, link_name, link_params, **kwargs)
            
            if not fitted_model["success"]:
                return fitted_model
            
            # Extract metrics
            metrics = self._extract_glm_metrics(fitted_model["fitted_model"], model_name)
            
            # Run diagnostics
            diagnostics = self.run_diagnostics(fitted_model["fitted_model"])
            
            # Create result
            return self.create_result_dict(
                model_name=model_name,
                fitted_model=fitted_model["fitted_model"],
                data_shape=data_prep["data"].shape,
                metrics=metrics,
                diagnostics=diagnostics,
                family=family_name,
                link_function=link_name,
                n_observations=len(data_prep["data"]),
                n_variables=len(independent_vars) if independent_vars else None,
                model_type=mapping["type"]
            )
            
        except Exception as e:
            logger.error(f"Failed to fit {model_name}: {str(e)}")
            return self.create_error_result(model_name, f"Failed to fit {model_name}: {str(e)}")
    
    def _fit_with_formula(self, model_name: str, data_prep: Dict[str, Any], 
                         family_name: str, family_params: Dict[str, Any],
                         link_name: str, link_params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Fit GLM model using formula interface.
        
        Args:
            model_name: Name of the model
            data_prep: Prepared data dictionary
            family_name: Name of the GLM family
            family_params: Parameters for the family
            link_name: Name of the link function
            link_params: Parameters for the link function
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing fitted model
        """
        try:
            # Import statsmodels formula interface
            import statsmodels.api as sm
            from statsmodels.formula.api import glm, logit, probit, mnlogit
            
            # Map model names to formula functions
            formula_functions = {
                "gaussian_glm": glm,
                "binomial_glm": glm,
                "poisson_glm": glm,
                "gamma_glm": glm,
                "inverse_gaussian_glm": glm,
                "negative_binomial_glm": glm,
                "tweedie_glm": glm,
                "logit": logit,
                "probit": probit,
                "multinomial_logit": mnlogit
            }
            
            if model_name not in formula_functions:
                return {"success": False, "error": f"Formula interface not supported for {model_name}"}
            
            formula_func = formula_functions[model_name]
            
            # For GLM models, we need to specify family and link
            if model_name.endswith('_glm'):
                # Get family and link
                family = self._get_glm_family(family_name, **family_params)
                link = self._get_link_function(link_name, **link_params)
                family.link = link
                
                model = formula_func(data_prep["formula"], data=data_prep["data"], 
                                   family=family, **kwargs)
            else:
                # For discrete choice models, use formula directly
                model = formula_func(data_prep["formula"], data=data_prep["data"], **kwargs)
            
            fitted_model = model.fit()
            
            return {"success": True, "fitted_model": fitted_model}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _fit_with_arrays(self, model_name: str, data_prep: Dict[str, Any], 
                        family_name: str, family_params: Dict[str, Any],
                        link_name: str, link_params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Fit GLM model using array interface.
        
        Args:
            model_name: Name of the model
            data_prep: Prepared data dictionary
            family_name: Name of the GLM family
            family_params: Parameters for the family
            link_name: Name of the link function
            link_params: Parameters for the link function
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing fitted model
        """
        try:
            # Import and instantiate model
            mapping = self.model_mapping[model_name]
            module = importlib.import_module(mapping["module"])
            model_class = getattr(module, mapping["class"])
            
            # For GLM models, we need to specify family and link
            if model_name.endswith('_glm'):
                family = self._get_glm_family(family_name, **family_params)
                link = self._get_link_function(link_name, **link_params)
                family.link = link
                
                model = model_class(data_prep["y"], data_prep["X"], 
                                   family=family, **kwargs)
            else:
                # For discrete choice models
                model = model_class(data_prep["y"], data_prep["X"], **kwargs)
            
            fitted_model = model.fit()
            
            return {"success": True, "fitted_model": fitted_model}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_glm_family(self, family_name: str, **family_params) -> Any:
        """
        Get GLM family object.
        
        Args:
            family_name: Name of the family
            **family_params: Family-specific parameters
            
        Returns:
            GLM family object
        """
        import statsmodels.api as sm
        from statsmodels.genmod import families
        
        family_map = {
            "Gaussian": families.Gaussian,
            "Binomial": families.Binomial,
            "Poisson": families.Poisson,
            "Gamma": families.Gamma,
            "InverseGaussian": families.InverseGaussian,
            "NegativeBinomial": families.NegativeBinomial,
            "Tweedie": families.Tweedie
        }
        
        if family_name not in family_map:
            raise ValueError(f"Unknown family: {family_name}")
        
        family_class = family_map[family_name]
        
        # Handle special cases
        if family_name == "NegativeBinomial":
            alpha = family_params.get('alpha', 1.0)
            return family_class(alpha=alpha)
        elif family_name == "Tweedie":
            var_power = family_params.get('var_power', 1.0)
            return family_class(var_power=var_power)
        else:
            return family_class()
    
    def _get_link_function(self, link_name: str, **link_params) -> Any:
        """
        Get link function object.
        
        Args:
            link_name: Name of the link function
            **link_params: Link-specific parameters
            
        Returns:
            Link function object
        """
        from statsmodels.genmod import families
        
        link_map = {
            "identity": families.links.identity(),
            "log": families.links.log(),
            "logit": families.links.logit(),
            "probit": families.links.probit(),
            "cloglog": families.links.cloglog(),
            "inverse": families.links.inverse_power(),
            "inverse_power": families.links.inverse_power(),
            "sqrt": families.links.sqrt()
        }
        
        if link_name not in link_map:
            raise ValueError(f"Unknown link function: {link_name}")
        
        return link_map[link_name]
    
    def _extract_glm_metrics(self, fitted_model, model_name: str) -> Dict[str, Any]:
        """
        Extract GLM-specific metrics.
        
        Args:
            fitted_model: The fitted model object
            model_name: Name of the model
            
        Returns:
            Dictionary of GLM-specific metrics
        """
        # Get common metrics from base class
        metrics = self.extract_common_metrics(fitted_model, model_name)
        
        # Add GLM-specific metrics
        if hasattr(fitted_model, 'deviance'):
            metrics["deviance"] = fitted_model.deviance
        if hasattr(fitted_model, 'pearson_chi2'):
            metrics["pearson_chi2"] = fitted_model.pearson_chi2
        if hasattr(fitted_model, 'pseudo_rsquared'):
            metrics["pseudo_r2"] = fitted_model.pseudo_rsquared
        if hasattr(fitted_model, 'llf'):
            metrics["llf"] = fitted_model.llf
        
        # Add confusion matrix for binary models
        if model_name in ["logit", "probit"] and hasattr(fitted_model, 'predict'):
            try:
                y_true = fitted_model.model.endog
                y_pred = (fitted_model.predict() > 0.5).astype(int)
                
                from sklearn.metrics import confusion_matrix
                cm = confusion_matrix(y_true, y_pred)
                metrics["confusion_matrix"] = cm.tolist()
                
                # Calculate accuracy
                accuracy = (cm[0, 0] + cm[1, 1]) / cm.sum()
                metrics["accuracy"] = accuracy
            except:
                pass
        
        return metrics


# Backward compatibility functions
def universal_glm(model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """
    Universal function to fit any statsmodels GLM model (backward compatibility).
    
    Args:
        model_name: Name of the model from GLM_MAPPING
        data: Input DataFrame
        **kwargs: Additional parameters
        
    Returns:
        Dictionary containing model fitting results
    """
    glm_models = GLMModels()
    return glm_models.fit_model(model_name, data, **kwargs)


def get_available_models() -> Dict[str, Any]:
    """
    Get list of all available GLM models grouped by type (backward compatibility).
    
    Returns:
        Dictionary of models grouped by type
    """
    glm_models = GLMModels()
    return glm_models.get_available_models()


def validate_model_parameters(model_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate parameters for a specific GLM model (backward compatibility).
    
    Args:
        model_name: Name of the model
        parameters: Dictionary of parameters to validate
        
    Returns:
        Validation result dictionary
    """
    glm_models = GLMModels()
    return glm_models.validate_model_parameters(model_name, parameters)


def create_langgraph_tool(model_name: str) -> Dict[str, Any]:
    """
    Create a LangGraph tool definition for a specific GLM model (backward compatibility).
    
    Args:
        model_name: Name of the model
        
    Returns:
        Dictionary containing LangGraph tool definition
    """
    glm_models = GLMModels()
    return glm_models.create_langgraph_tool(model_name)


def extract_model_info(model_name: str) -> Dict[str, Any]:
    """
    Extract model description, parameters, and their descriptions (backward compatibility).
    
    Args:
        model_name: Name of the model in the mapping
        
    Returns:
        Dictionary containing model information
    """
    glm_models = GLMModels()
    return glm_models.extract_model_info(model_name)


def get_model_tool_description(model_name: str) -> str:
    """
    Generate a comprehensive tool description for LangGraph use (backward compatibility).
    
    Args:
        model_name: Name of the model
        
    Returns:
        Formatted tool description string
    """
    glm_models = GLMModels()
    return glm_models.get_model_tool_description(model_name)


# Example usage and testing functions
def example_usage():
    """Example usage of the universal GLM function."""
    import pandas as pd
    import numpy as np
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    
    # Generate synthetic data for different GLM types
    x1 = np.random.randn(n_samples)
    x2 = np.random.randn(n_samples)
    x3 = np.random.randn(n_samples)
    
    # Gaussian GLM data
    y_gaussian = 2 + 1.5 * x1 + 0.8 * x2 - 0.3 * x3 + np.random.randn(n_samples) * 0.5
    
    # Binomial GLM data (logistic regression)
    logit_prob = 1 / (1 + np.exp(-(2 + 1.5 * x1 + 0.8 * x2)))
    y_binomial = np.random.binomial(1, logit_prob)
    
    # Poisson GLM data (count data)
    lambda_poisson = np.exp(2 + 1.5 * x1 + 0.8 * x2)
    y_poisson = np.random.poisson(lambda_poisson)
    
    # Create DataFrames
    data_gaussian = pd.DataFrame({
        'y': y_gaussian,
        'x1': x1,
        'x2': x2,
        'x3': x3
    })
    
    data_binomial = pd.DataFrame({
        'y': y_binomial,
        'x1': x1,
        'x2': x2
    })
    
    data_poisson = pd.DataFrame({
        'y': y_poisson,
        'x1': x1,
        'x2': x2
    })
    
    print("=== Universal GLM Tool Example ===")
    
    # Example 1: Gaussian GLM
    print("\n1. Gaussian GLM (Linear Regression)")
    result1 = universal_glm(
        model_name="gaussian_glm",
        data=data_gaussian,
        dependent_var="y",
        independent_vars=["x1", "x2", "x3"],
        add_constant=True
    )
    
    if result1['success']:
        print(f"✓ Successfully fitted {result1['model_name']}")
        print(f"  AIC: {result1['metrics']['aic']:.4f}")
        print(f"  BIC: {result1['metrics']['bic']:.4f}")
        print(f"  Deviance: {result1['metrics']['deviance']:.4f}")
        print(f"  Coefficients: {result1['metrics']['coefficients']}")
    else:
        print(f"✗ Failed: {result1['error']}")
    
    # Example 2: Binomial GLM (Logistic Regression)
    print("\n2. Binomial GLM (Logistic Regression)")
    result2 = universal_glm(
        model_name="binomial_glm",
        data=data_binomial,
        dependent_var="y",
        independent_vars=["x1", "x2"],
        add_constant=True
    )
    
    if result2['success']:
        print(f"✓ Successfully fitted {result2['model_name']}")
        print(f"  AIC: {result2['metrics']['aic']:.4f}")
        print(f"  Pseudo R²: {result2['metrics']['pseudo_r2']:.4f}")
        print(f"  Coefficients: {result2['metrics']['coefficients']}")
    else:
        print(f"✗ Failed: {result2['error']}")
    
    # Example 3: Poisson GLM
    print("\n3. Poisson GLM (Count Data)")
    result3 = universal_glm(
        model_name="poisson_glm",
        data=data_poisson,
        dependent_var="y",
        independent_vars=["x1", "x2"],
        add_constant=True
    )
    
    if result3['success']:
        print(f"✓ Successfully fitted {result3['model_name']}")
        print(f"  AIC: {result3['metrics']['aic']:.4f}")
        print(f"  Deviance: {result3['metrics']['deviance']:.4f}")
        print(f"  Coefficients: {result3['metrics']['coefficients']}")
    else:
        print(f"✗ Failed: {result3['error']}")
    
    # Example 4: Using formula interface
    print("\n4. GLM with Formula Interface")
    result4 = universal_glm(
        model_name="gaussian_glm",
        data=data_gaussian,
        dependent_var="y",
        formula="y ~ x1 + x2 + x3"
    )
    
    if result4['success']:
        print(f"✓ Successfully fitted {result4['model_name']} with formula")
        print(f"  AIC: {result4['metrics']['aic']:.4f}")
        print(f"  BIC: {result4['metrics']['bic']:.4f}")
    else:
        print(f"✗ Failed: {result4['error']}")


if __name__ == "__main__":
    # Print available models
    print("Available GLM models:")
    models = get_available_models()
    for model_type, type_models in models.items():
        print(f"\n{model_type.upper()}:")
        for name, info in type_models.items():
            print(f"  - {name}: {info['description']}")
            print(f"    Family: {info['family']}")
            print(f"    Default Link: {info['default_link']}")
    
    # Run example usage
    print("\n" + "="*50)
    example_usage()
    
    def _fit_with_arrays(self, model_name: str, data_prep: Dict[str, Any], 
                        family_name: str, family_params: Dict[str, Any],
                        link_name: str, link_params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Fit GLM model using array interface.
        
        Args:
            model_name: Name of the model
            data_prep: Prepared data dictionary
            family_name: Name of the GLM family
            family_params: Parameters for the family
            link_name: Name of the link function
            link_params: Parameters for the link function
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing fitted model
        """
        try:
            # Import and instantiate model
            mapping = self.model_mapping[model_name]
            module = importlib.import_module(mapping["module"])
            model_class = getattr(module, mapping["class"])
            
            # For GLM models, we need to specify family and link
            if model_name.endswith('_glm'):
                family = self._get_glm_family(family_name, **family_params)
                link = self._get_link_function(link_name, **link_params)
                family.link = link
                
                model = model_class(data_prep["y"], data_prep["X"], 
                                   family=family, **kwargs)
            else:
                # For discrete choice models
                model = model_class(data_prep["y"], data_prep["X"], **kwargs)
            
            fitted_model = model.fit()
            
            return {"success": True, "fitted_model": fitted_model}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_glm_family(self, family_name: str, **family_params) -> Any:
        """
        Get GLM family object.
        
        Args:
            family_name: Name of the family
            **family_params: Family-specific parameters
            
        Returns:
            GLM family object
        """
        import statsmodels.api as sm
        from statsmodels.genmod import families
        
        family_map = {
            "Gaussian": families.Gaussian,
            "Binomial": families.Binomial,
            "Poisson": families.Poisson,
            "Gamma": families.Gamma,
            "InverseGaussian": families.InverseGaussian,
            "NegativeBinomial": families.NegativeBinomial,
            "Tweedie": families.Tweedie
        }
        
        if family_name not in family_map:
            raise ValueError(f"Unknown family: {family_name}")
        
        family_class = family_map[family_name]
        
        # Handle special cases
        if family_name == "NegativeBinomial":
            alpha = family_params.get('alpha', 1.0)
            return family_class(alpha=alpha)
        elif family_name == "Tweedie":
            var_power = family_params.get('var_power', 1.0)
            return family_class(var_power=var_power)
        else:
            return family_class()
    
    def _get_link_function(self, link_name: str, **link_params) -> Any:
        """
        Get link function object.
        
        Args:
            link_name: Name of the link function
            **link_params: Link-specific parameters
            
        Returns:
            Link function object
        """
        from statsmodels.genmod import families
        
        link_map = {
            "identity": families.links.identity(),
            "log": families.links.log(),
            "logit": families.links.logit(),
            "probit": families.links.probit(),
            "cloglog": families.links.cloglog(),
            "inverse": families.links.inverse_power(),
            "inverse_power": families.links.inverse_power(),
            "sqrt": families.links.sqrt()
        }
        
        if link_name not in link_map:
            raise ValueError(f"Unknown link function: {link_name}")
        
        return link_map[link_name]
    
    def _extract_glm_metrics(self, fitted_model, model_name: str) -> Dict[str, Any]:
        """
        Extract GLM-specific metrics.
        
        Args:
            fitted_model: The fitted model object
            model_name: Name of the model
            
        Returns:
            Dictionary of GLM-specific metrics
        """
        # Get common metrics from base class
        metrics = self.extract_common_metrics(fitted_model, model_name)
        
        # Add GLM-specific metrics
        if hasattr(fitted_model, 'deviance'):
            metrics["deviance"] = fitted_model.deviance
        if hasattr(fitted_model, 'pearson_chi2'):
            metrics["pearson_chi2"] = fitted_model.pearson_chi2
        if hasattr(fitted_model, 'pseudo_rsquared'):
            metrics["pseudo_r2"] = fitted_model.pseudo_rsquared
        if hasattr(fitted_model, 'llf'):
            metrics["llf"] = fitted_model.llf
        
        # Add confusion matrix for binary models
        if model_name in ["logit", "probit"] and hasattr(fitted_model, 'predict'):
            try:
                y_true = fitted_model.model.endog
                y_pred = (fitted_model.predict() > 0.5).astype(int)
                
                from sklearn.metrics import confusion_matrix
                cm = confusion_matrix(y_true, y_pred)
                metrics["confusion_matrix"] = cm.tolist()
                
                # Calculate accuracy
                accuracy = (cm[0, 0] + cm[1, 1]) / cm.sum()
                metrics["accuracy"] = accuracy
            except:
                pass
        
        return metrics


# Backward compatibility functions
def universal_glm(model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """
    Universal function to fit any statsmodels GLM model (backward compatibility).
    
    Args:
        model_name: Name of the model from GLM_MAPPING
        data: Input DataFrame
        **kwargs: Additional parameters
        
    Returns:
        Dictionary containing model fitting results
    """
    glm_models = GLMModels()
    return glm_models.fit_model(model_name, data, **kwargs)


def get_available_models() -> Dict[str, Any]:
    """
    Get list of all available GLM models grouped by type (backward compatibility).
    
    Returns:
        Dictionary of models grouped by type
    """
    glm_models = GLMModels()
    return glm_models.get_available_models()


def validate_model_parameters(model_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate parameters for a specific GLM model (backward compatibility).
    
    Args:
        model_name: Name of the model
        parameters: Dictionary of parameters to validate
        
    Returns:
        Validation result dictionary
    """
    glm_models = GLMModels()
    return glm_models.validate_model_parameters(model_name, parameters)


def create_langgraph_tool(model_name: str) -> Dict[str, Any]:
    """
    Create a LangGraph tool definition for a specific GLM model (backward compatibility).
    
    Args:
        model_name: Name of the model
        
    Returns:
        Dictionary containing LangGraph tool definition
    """
    glm_models = GLMModels()
    return glm_models.create_langgraph_tool(model_name)


def extract_model_info(model_name: str) -> Dict[str, Any]:
    """
    Extract model description, parameters, and their descriptions (backward compatibility).
    
    Args:
        model_name: Name of the model in the mapping
        
    Returns:
        Dictionary containing model information
    """
    glm_models = GLMModels()
    return glm_models.extract_model_info(model_name)


def get_model_tool_description(model_name: str) -> str:
    """
    Generate a comprehensive tool description for LangGraph use (backward compatibility).
    
    Args:
        model_name: Name of the model
        
    Returns:
        Formatted tool description string
    """
    glm_models = GLMModels()
    return glm_models.get_model_tool_description(model_name)


# Example usage and testing functions
def example_usage():
    """Example usage of the universal GLM function."""
    import pandas as pd
    import numpy as np
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    
    # Generate synthetic data for different GLM types
    x1 = np.random.randn(n_samples)
    x2 = np.random.randn(n_samples)
    x3 = np.random.randn(n_samples)
    
    # Gaussian GLM data
    y_gaussian = 2 + 1.5 * x1 + 0.8 * x2 - 0.3 * x3 + np.random.randn(n_samples) * 0.5
    
    # Binomial GLM data (logistic regression)
    logit_prob = 1 / (1 + np.exp(-(2 + 1.5 * x1 + 0.8 * x2)))
    y_binomial = np.random.binomial(1, logit_prob)
    
    # Poisson GLM data (count data)
    lambda_poisson = np.exp(2 + 1.5 * x1 + 0.8 * x2)
    y_poisson = np.random.poisson(lambda_poisson)
    
    # Create DataFrames
    data_gaussian = pd.DataFrame({
        'y': y_gaussian,
        'x1': x1,
        'x2': x2,
        'x3': x3
    })
    
    data_binomial = pd.DataFrame({
        'y': y_binomial,
        'x1': x1,
        'x2': x2
    })
    
    data_poisson = pd.DataFrame({
        'y': y_poisson,
        'x1': x1,
        'x2': x2
    })
    
    print("=== Universal GLM Tool Example ===")
    
    # Example 1: Gaussian GLM
    print("\n1. Gaussian GLM (Linear Regression)")
    result1 = universal_glm(
        model_name="gaussian_glm",
        data=data_gaussian,
        dependent_var="y",
        independent_vars=["x1", "x2", "x3"],
        add_constant=True
    )
    
    if result1['success']:
        print(f"✓ Successfully fitted {result1['model_name']}")
        print(f"  AIC: {result1['metrics']['aic']:.4f}")
        print(f"  BIC: {result1['metrics']['bic']:.4f}")
        print(f"  Deviance: {result1['metrics']['deviance']:.4f}")
        print(f"  Coefficients: {result1['metrics']['coefficients']}")
    else:
        print(f"✗ Failed: {result1['error']}")
    
    # Example 2: Binomial GLM (Logistic Regression)
    print("\n2. Binomial GLM (Logistic Regression)")
    result2 = universal_glm(
        model_name="binomial_glm",
        data=data_binomial,
        dependent_var="y",
        independent_vars=["x1", "x2"],
        add_constant=True
    )
    
    if result2['success']:
        print(f"✓ Successfully fitted {result2['model_name']}")
        print(f"  AIC: {result2['metrics']['aic']:.4f}")
        print(f"  Pseudo R²: {result2['metrics']['pseudo_r2']:.4f}")
        print(f"  Coefficients: {result2['metrics']['coefficients']}")
    else:
        print(f"✗ Failed: {result2['error']}")
    
    # Example 3: Poisson GLM
    print("\n3. Poisson GLM (Count Data)")
    result3 = universal_glm(
        model_name="poisson_glm",
        data=data_poisson,
        dependent_var="y",
        independent_vars=["x1", "x2"],
        add_constant=True
    )
    
    if result3['success']:
        print(f"✓ Successfully fitted {result3['model_name']}")
        print(f"  AIC: {result3['metrics']['aic']:.4f}")
        print(f"  Deviance: {result3['metrics']['deviance']:.4f}")
        print(f"  Coefficients: {result3['metrics']['coefficients']}")
    else:
        print(f"✗ Failed: {result3['error']}")
    
    # Example 4: Using formula interface
    print("\n4. GLM with Formula Interface")
    result4 = universal_glm(
        model_name="gaussian_glm",
        data=data_gaussian,
        dependent_var="y",
        formula="y ~ x1 + x2 + x3"
    )
    
    if result4['success']:
        print(f"✓ Successfully fitted {result4['model_name']} with formula")
        print(f"  AIC: {result4['metrics']['aic']:.4f}")
        print(f"  BIC: {result4['metrics']['bic']:.4f}")
    else:
        print(f"✗ Failed: {result4['error']}")


if __name__ == "__main__":
    # Print available models
    print("Available GLM models:")
    models = get_available_models()
    for model_type, type_models in models.items():
        print(f"\n{model_type.upper()}:")
        for name, info in type_models.items():
            print(f"  - {name}: {info['description']}")
            print(f"    Family: {info['family']}")
            print(f"    Default Link: {info['default_link']}")
    
    # Run example usage
    print("\n" + "="*50)
    example_usage()