"""
LangGraph Integration Example for Universal Statsmodels Tool

This example demonstrates how to integrate the universal statsmodels tool
with LangGraph agents for automated statistical analysis.
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import the universal statsmodels functions
from algos.linear_models import universal_linear_models, get_available_models as get_linear_models
from algos.glm import universal_glm, get_available_models as get_glm_models
from algos.nonparametric import universal_nonparametric, get_available_models as get_nonparametric_models
from algos.rlm import universal_rlm, get_available_models as get_rlm_models


# Define the state schema
class AgentState:
    """State for the statistical analysis agent."""
    
    def __init__(self, data: pd.DataFrame = None, analysis_results: List[Dict] = None, 
                 current_analysis: Dict = None, recommendations: List[str] = None):
        self.data = data
        self.analysis_results = analysis_results or []
        self.current_analysis = current_analysis or {}
        self.recommendations = recommendations or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "data": self.data.to_dict() if self.data is not None else None,
            "analysis_results": self.analysis_results,
            "current_analysis": self.current_analysis,
            "recommendations": self.recommendations
        }
    
    @classmethod
    def from_dict(cls, state_dict: Dict[str, Any]) -> 'AgentState':
        """Create state from dictionary."""
        data = pd.DataFrame(state_dict["data"]) if state_dict.get("data") else None
        return cls(
            data=data,
            analysis_results=state_dict.get("analysis_results", []),
            current_analysis=state_dict.get("current_analysis", {}),
            recommendations=state_dict.get("recommendations", [])
        )


# Define LangChain tools for each model type
@tool
def analyze_linear_models(data_json: str, dependent_var: str, independent_vars: List[str] = None, 
                         model_name: str = "ols") -> str:
    """
    Analyze data using linear regression models.
    
    Args:
        data_json: JSON string representation of the DataFrame
        dependent_var: Name of the dependent variable
        independent_vars: List of independent variable names
        model_name: Type of linear model to use (ols, gls, wls, quantile_regression, etc.)
    
    Returns:
        JSON string with analysis results
    """
    try:
        # Parse data
        data = pd.DataFrame(json.loads(data_json))
        
        # Get available models
        available_models = get_linear_models()
        
        if model_name not in available_models.get("regression", {}):
            return json.dumps({
                "success": False,
                "error": f"Model '{model_name}' not available. Available models: {list(available_models.get('regression', {}).keys())}"
            })
        
        # Perform analysis
        result = universal_linear_models(
            model_name=model_name,
            data=data,
            dependent_var=dependent_var,
            independent_vars=independent_vars
        )
        
        return json.dumps(result, default=str)
        
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def analyze_glm_models(data_json: str, dependent_var: str, independent_vars: List[str] = None,
                      model_name: str = "gaussian_glm", family: str = "Gaussian", link: str = "identity") -> str:
    """
    Analyze data using generalized linear models.
    
    Args:
        data_json: JSON string representation of the DataFrame
        dependent_var: Name of the dependent variable
        independent_vars: List of independent variable names
        model_name: Type of GLM model to use
        family: GLM family (Gaussian, Binomial, Poisson, etc.)
        link: Link function (identity, log, logit, etc.)
    
    Returns:
        JSON string with analysis results
    """
    try:
        # Parse data
        data = pd.DataFrame(json.loads(data_json))
        
        # Get available models
        available_models = get_glm_models()
        
        if model_name not in available_models.get("glm", {}):
            return json.dumps({
                "success": False,
                "error": f"Model '{model_name}' not available. Available models: {list(available_models.get('glm', {}).keys())}"
            })
        
        # Perform analysis
        result = universal_glm(
            model_name=model_name,
            data=data,
            dependent_var=dependent_var,
            independent_vars=independent_vars,
            family=family,
            link=link
        )
        
        return json.dumps(result, default=str)
        
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def analyze_nonparametric_models(data_json: str, dependent_var: str, independent_vars: List[str] = None,
                                model_name: str = "kernel_density") -> str:
    """
    Analyze data using nonparametric models.
    
    Args:
        data_json: JSON string representation of the DataFrame
        dependent_var: Name of the dependent variable
        independent_vars: List of independent variable names
        model_name: Type of nonparametric model to use
    
    Returns:
        JSON string with analysis results
    """
    try:
        # Parse data
        data = pd.DataFrame(json.loads(data_json))
        
        # Get available models
        available_models = get_nonparametric_models()
        
        if model_name not in available_models.get("nonparametric", {}):
            return json.dumps({
                "success": False,
                "error": f"Model '{model_name}' not available. Available models: {list(available_models.get('nonparametric', {}).keys())}"
            })
        
        # Perform analysis
        result = universal_nonparametric(
            model_name=model_name,
            data=data,
            dependent_var=dependent_var,
            independent_vars=independent_vars
        )
        
        return json.dumps(result, default=str)
        
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def analyze_robust_models(data_json: str, dependent_var: str, independent_vars: List[str] = None,
                         model_name: str = "rlm_huber") -> str:
    """
    Analyze data using robust linear models for outlier-resistant regression.
    
    Args:
        data_json: JSON string representation of the DataFrame
        dependent_var: Name of the dependent variable
        independent_vars: List of independent variable names
        model_name: Type of robust model to use (rlm_huber, rlm_tukey_biweight, rlm_hampel, etc.)
    
    Returns:
        JSON string with analysis results including outlier detection and robust estimates
    """
    try:
        # Parse data
        data = pd.DataFrame(json.loads(data_json))
        
        # Get available models
        available_models = get_rlm_models()
        
        if model_name not in available_models.get("robust_regression", {}):
            return json.dumps({
                "success": False,
                "error": f"Model '{model_name}' not available. Available models: {list(available_models.get('robust_regression', {}).keys())}"
            })
        
        # Perform analysis
        result = universal_rlm(
            model_name=model_name,
            data=data,
            dependent_var=dependent_var,
            independent_vars=independent_vars
        )
        
        return json.dumps(result, default=str)
        
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_available_models() -> str:
    """
    Get list of all available statistical models.
    
    Returns:
        JSON string with all available models grouped by type
    """
    try:
        all_models = {
            "linear_models": get_linear_models(),
            "glm_models": get_glm_models(),
            "nonparametric_models": get_nonparametric_models(),
            "robust_models": get_rlm_models()
        }
        
        return json.dumps(all_models, default=str)
        
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def detect_outliers_and_recommend_robust_analysis(data_json: str, dependent_var: str, 
                                                independent_vars: List[str] = None) -> str:
    """
    Detect outliers in the data and recommend robust analysis methods.
    
    Args:
        data_json: JSON string representation of the DataFrame
        dependent_var: Name of the dependent variable
        independent_vars: List of independent variable names
    
    Returns:
        JSON string with outlier detection results and recommendations
    """
    try:
        # Parse data
        data = pd.DataFrame(json.loads(data_json))
        
        # Basic outlier detection using IQR method
        y = data[dependent_var]
        Q1 = y.quantile(0.25)
        Q3 = y.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = data[(y < lower_bound) | (y > upper_bound)]
        outlier_count = len(outliers)
        outlier_percentage = (outlier_count / len(data)) * 100
        
        # Recommendations based on outlier presence
        recommendations = []
        if outlier_percentage > 10:
            recommendations.append("High outlier percentage detected. Consider using robust regression models.")
            recommendations.append("Recommended models: rlm_huber, rlm_tukey_biweight, rlm_hampel")
        elif outlier_percentage > 5:
            recommendations.append("Moderate outlier percentage detected. Consider robust regression as alternative.")
            recommendations.append("Recommended models: rlm_huber, rlm_andrew_wave")
        else:
            recommendations.append("Low outlier percentage. Standard linear models should work well.")
            recommendations.append("Consider comparing with robust models for validation.")
        
        # Perform both OLS and robust regression for comparison
        ols_result = universal_linear_models(
            model_name="ols",
            data=data,
            dependent_var=dependent_var,
            independent_vars=independent_vars
        )
        
        rlm_result = universal_rlm(
            model_name="rlm_huber",
            data=data,
            dependent_var=dependent_var,
            independent_vars=independent_vars
        )
        
        return json.dumps({
            "outlier_analysis": {
                "outlier_count": outlier_count,
                "outlier_percentage": outlier_percentage,
                "outlier_indices": outliers.index.tolist(),
                "lower_bound": lower_bound,
                "upper_bound": upper_bound
            },
            "recommendations": recommendations,
            "ols_comparison": ols_result,
            "robust_comparison": rlm_result
        }, default=str)
        
    except Exception as e:
        return json.dumps({"error": str(e)})


def create_statistical_analysis_agent():
    """Create a LangGraph agent for statistical analysis."""
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze_data", ToolNode([
        analyze_linear_models,
        analyze_glm_models,
        analyze_nonparametric_models,
        analyze_robust_models,
        get_available_models,
        detect_outliers_and_recommend_robust_analysis
    ]))
    
    # Define edges
    workflow.add_edge("analyze_data", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def example_usage():
    """Example usage of the statistical analysis agent."""
    
    # Create sample data with outliers
    np.random.seed(42)
    n_samples = 100
    
    # Generate clean data
    x1 = np.random.randn(n_samples)
    x2 = np.random.randn(n_samples)
    y_clean = 2 + 1.5 * x1 + 0.8 * x2 + np.random.randn(n_samples) * 0.5
    
    # Add outliers
    outliers_idx = np.random.choice(n_samples, size=10, replace=False)
    y_with_outliers = y_clean.copy()
    y_with_outliers[outliers_idx] += 15  # Add large outliers
    
    # Create DataFrame
    data = pd.DataFrame({
        'y': y_with_outliers,
        'x1': x1,
        'x2': x2
    })
    
    print("=== LangGraph Statistical Analysis Agent Example ===\n")
    
    # Create the agent
    agent = create_statistical_analysis_agent()
    
    # Example 1: Get available models
    print("1. Getting available models...")
    result = get_available_models()
    models_info = json.loads(result)
    print(f"Available model types: {list(models_info.keys())}")
    print(f"Robust models: {list(models_info['robust_models']['robust_regression'].keys())}")
    print()
    
    # Example 2: Detect outliers and get recommendations
    print("2. Detecting outliers and getting recommendations...")
    data_json = data.to_json()
    result = detect_outliers_and_recommend_robust_analysis(data_json, "y", ["x1", "x2"])
    analysis = json.loads(result)
    print(f"Outlier percentage: {analysis['outlier_analysis']['outlier_percentage']:.2f}%")
    print(f"Recommendations: {analysis['recommendations']}")
    print()
    
    # Example 3: Compare OLS vs Robust regression
    print("3. Comparing OLS vs Robust regression...")
    
    # OLS analysis
    ols_result = analyze_linear_models(data_json, "y", ["x1", "x2"], "ols")
    ols_analysis = json.loads(ols_result)
    
    # Robust analysis
    robust_result = analyze_robust_models(data_json, "y", ["x1", "x2"], "rlm_huber")
    robust_analysis = json.loads(robust_result)
    
    if ols_analysis['success'] and robust_analysis['success']:
        print("OLS Coefficients:")
        for var, coef in ols_analysis['coefficients'].items():
            print(f"  {var}: {coef:.4f}")
        
        print("\nRobust Coefficients (Huber):")
        for var, coef in robust_analysis['coefficients'].items():
            print(f"  {var}: {coef:.4f}")
        
        print(f"\nRobust Scale Estimate: {robust_analysis.get('scale', 'N/A')}")
        print(f"Robust Weights Range: {min(robust_analysis['weights']):.3f} - {max(robust_analysis['weights']):.3f}")
    
    print("\n=== Example completed ===")


if __name__ == "__main__":
    example_usage()
