"""
Basic Usage Example for DataAgent

This example demonstrates how to use both sklearn and statsmodels tools
from the DataAgent package.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import datagent
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris

def sklearn_example():
    """Example using sklearn tools"""
    print("=== Scikit-learn Example ===")
    
    # Load iris dataset
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target)
    
    print(f"Dataset shape: {X.shape}")
    print(f"Target classes: {np.unique(y)}")
    
    # Create DataFrame with target column for sklearn tools
    df = X.copy()
    df['target'] = y
    
    # Use universal sklearn estimator
    try:
        result = datagent.universal_sklearn_estimator(
            estimator_name="random_forest_classifier",
            data=df,
            target_column="target",
            test_size=0.2,
            random_state=42,
            n_estimators=100
        )
        
        print(f"Model: {result['estimator_name']}")
        print(f"Accuracy: {result['metrics']['accuracy']:.4f}")
        print(f"Precision: {result['metrics']['precision']:.4f}")
        print(f"Recall: {result['metrics']['recall']:.4f}")
        print(f"F1 Score: {result['metrics']['f1']:.4f}")
        
    except Exception as e:
        print(f"Error in sklearn example: {e}")

def statsmodels_example():
    """Example using statsmodels tools"""
    print("\n=== Statsmodels Example ===")
    
    # Create sample data for linear regression
    np.random.seed(42)
    n = 100
    X = np.random.randn(n, 2)
    y = 2 * X[:, 0] + 1.5 * X[:, 1] + np.random.randn(n) * 0.5
    
    df = pd.DataFrame({
        'y': y,
        'x1': X[:, 0],
        'x2': X[:, 1]
    })
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Use universal linear model
    try:
        result = datagent.universal_linear_models(
            model_name="ols",
            data=df,
            formula="y ~ x1 + x2"
        )
        
        print(f"Model: {result.get('model_name', 'OLS')}")
        print(f"R-squared: {result.get('r_squared', 'N/A')}")
        print(f"Adjusted R-squared: {result.get('adj_r_squared', 'N/A')}")
        print(f"AIC: {result.get('aic', 'N/A')}")
        print(f"BIC: {result.get('bic', 'N/A')}")
        
        # Print coefficients if available
        if 'params' in result:
            print("\nCoefficients:")
            for param, value in result['params'].items():
                print(f"  {param}: {value:.4f}")
            
    except Exception as e:
        print(f"Error in statsmodels example: {e}")

def available_models_example():
    """Example showing available models"""
    print("\n=== Available Models ===")
    
    try:
        # Get available sklearn models
        sklearn_models = datagent.get_available_sklearn_models()
        print(f"Available sklearn models: {len(sklearn_models)}")
        print("Sample sklearn models:")
        for model in list(sklearn_models.keys())[:5]:
            print(f"  - {model}")
            
        # Get available statsmodels models
        linear_models = datagent.get_linear_available_models()
        print(f"\nAvailable linear models: {len(linear_models)}")
        print("Sample linear models:")
        for model in list(linear_models.keys())[:5]:
            print(f"  - {model}")
            
    except Exception as e:
        print(f"Error getting available models: {e}")

if __name__ == "__main__":
    print("DataAgent Basic Usage Example")
    print("=" * 50)
    
    sklearn_example()
    statsmodels_example()
    available_models_example()
    
    print("\n" + "=" * 50)
    print("Example completed!")
