"""
LangGraph Integration Example for DataAgent

This example demonstrates how to integrate DataAgent tools with LangGraph
for automated data analysis workflows.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import datagent
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from typing import Dict, Any, TypedDict

# Define the state structure for our LangGraph workflow
class AnalysisState(TypedDict):
    data: pd.DataFrame
    target: pd.Series
    analysis_results: Dict[str, Any]
    current_step: str
    recommendations: list

def load_data(state: AnalysisState) -> AnalysisState:
    """Load and prepare data"""
    print("Loading iris dataset...")
    
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target)
    
    state["data"] = X
    state["target"] = y
    state["current_step"] = "data_loaded"
    state["analysis_results"] = {}
    state["recommendations"] = []
    
    print(f"Loaded dataset with shape: {X.shape}")
    return state

def analyze_with_sklearn(state: AnalysisState) -> AnalysisState:
    """Analyze data using sklearn tools"""
    print("Running sklearn analysis...")
    
    try:
        # Create DataFrame with target column for sklearn tools
        df = state["data"].copy()
        df['target'] = state["target"]
        
        # Use DataAgent's sklearn tool
        result = datagent.universal_sklearn_estimator(
            estimator_name="random_forest_classifier",
            data=df,
            target_column="target",
            test_size=0.2,
            random_state=42,
            n_estimators=100
        )
        
        state["analysis_results"]["sklearn"] = result
        state["current_step"] = "sklearn_completed"
        
        # Add recommendations based on results
        accuracy = result["metrics"]["accuracy"]
        if accuracy > 0.95:
            state["recommendations"].append("Excellent model performance! Consider using this model for production.")
        elif accuracy > 0.85:
            state["recommendations"].append("Good model performance. Consider hyperparameter tuning for improvement.")
        else:
            state["recommendations"].append("Model performance could be improved. Consider feature engineering or different algorithms.")
            
        print(f"Sklearn analysis completed. Accuracy: {accuracy:.4f}")
        
    except Exception as e:
        print(f"Error in sklearn analysis: {e}")
        state["analysis_results"]["sklearn"] = {"error": str(e)}
    
    return state

def analyze_with_statsmodels(state: AnalysisState) -> AnalysisState:
    """Analyze data using statsmodels tools"""
    print("Running statsmodels analysis...")
    
    try:
        # Create a combined dataset for statsmodels
        df = state["data"].copy()
        df['target'] = state["target"]
        
        # Use DataAgent's statsmodels tool
        result = datagent.universal_linear_models(
            model_name="ols",
            data=df,
            formula="target ~ sepal_length + sepal_width + petal_length + petal_width"
        )
        
        state["analysis_results"]["statsmodels"] = result
        state["current_step"] = "statsmodels_completed"
        
        # Add recommendations based on results
        r_squared = result.get("r_squared", 0)
        if r_squared > 0.9:
            state["recommendations"].append("Strong linear relationship detected. Linear models are appropriate.")
        elif r_squared > 0.7:
            state["recommendations"].append("Moderate linear relationship. Consider non-linear models for better fit.")
        else:
            state["recommendations"].append("Weak linear relationship. Consider non-linear models or feature engineering.")
            
        print(f"Statsmodels analysis completed. R-squared: {r_squared:.4f}")
        
    except Exception as e:
        print(f"Error in statsmodels analysis: {e}")
        state["analysis_results"]["statsmodels"] = {"error": str(e)}
    
    return state

def generate_report(state: AnalysisState) -> AnalysisState:
    """Generate a comprehensive analysis report"""
    print("Generating analysis report...")
    
    report = {
        "summary": {
            "dataset_shape": state["data"].shape,
            "target_classes": len(state["target"].unique()),
            "analysis_steps": state["current_step"]
        },
        "results": state["analysis_results"],
        "recommendations": state["recommendations"]
    }
    
    state["analysis_results"]["report"] = report
    state["current_step"] = "report_generated"
    
    print("Report generated successfully!")
    return state

def print_report(state: AnalysisState) -> AnalysisState:
    """Print the analysis report"""
    print("\n" + "="*60)
    print("DATAAGENT ANALYSIS REPORT")
    print("="*60)
    
    report = state["analysis_results"]["report"]
    
    print(f"\nDataset Summary:")
    print(f"  Shape: {report['summary']['dataset_shape']}")
    print(f"  Target classes: {report['summary']['target_classes']}")
    
    print(f"\nAnalysis Results:")
    
    # Sklearn results
    if "sklearn" in report["results"] and "error" not in report["results"]["sklearn"]:
        sklearn_result = report["results"]["sklearn"]
        print(f"  Scikit-learn Random Forest:")
        print(f"    Accuracy: {sklearn_result['metrics']['accuracy']:.4f}")
        print(f"    Precision: {sklearn_result['metrics']['precision']:.4f}")
        print(f"    Recall: {sklearn_result['metrics']['recall']:.4f}")
        print(f"    F1 Score: {sklearn_result['metrics']['f1']:.4f}")
    
    # Statsmodels results
    if "statsmodels" in report["results"] and "error" not in report["results"]["statsmodels"]:
        statsmodels_result = report["results"]["statsmodels"]
        print(f"  Statsmodels OLS:")
        print(f"    R-squared: {statsmodels_result.get('r_squared', 'N/A')}")
        print(f"    Adjusted R-squared: {statsmodels_result.get('adj_r_squared', 'N/A')}")
        print(f"    AIC: {statsmodels_result.get('aic', 'N/A')}")
    
    print(f"\nRecommendations:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "="*60)
    
    return state

def main():
    """Main function to run the LangGraph-style workflow"""
    print("DataAgent LangGraph Integration Example")
    print("="*50)
    
    # Initialize state
    state = AnalysisState(
        data=pd.DataFrame(),
        target=pd.Series(),
        analysis_results={},
        current_step="initialized",
        recommendations=[]
    )
    
    # Run the workflow steps
    state = load_data(state)
    state = analyze_with_sklearn(state)
    state = analyze_with_statsmodels(state)
    state = generate_report(state)
    state = print_report(state)
    
    print("\nWorkflow completed successfully!")

if __name__ == "__main__":
    main()
