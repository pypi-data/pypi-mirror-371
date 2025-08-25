#!/usr/bin/env python3
"""
Example script demonstrating LangGraph integration with the universal estimator.
"""

import pandas as pd
import numpy as np
from sklearn.datasets import load_iris, load_diabetes, load_wine
from universal_estimator import (
    universal_estimator,
    create_langgraph_tool,
    get_available_estimators
)

def create_sample_data():
    """Create sample data for demonstration using scikit-learn datasets."""
    try:
        # Use scikit-learn datasets
        iris = load_iris()
        data_clf = pd.DataFrame(iris.data, columns=iris.feature_names)
        data_clf['target'] = iris.target
        
        diabetes = load_diabetes()
        data_reg = pd.DataFrame(diabetes.data, columns=diabetes.feature_names)
        data_reg['target'] = diabetes.target
        
        print("✓ Using scikit-learn datasets (Iris for classification, Diabetes for regression)")
        
    except Exception as e:
        print(f"Warning: Could not load scikit-learn datasets: {e}")
        print("Falling back to synthetic data...")
        
        # Fallback to synthetic data
        np.random.seed(42)
        n_samples = 1000
        n_features = 10
        
        # Create features
        X = np.random.randn(n_samples, n_features)
        
        # Create classification target (3 classes)
        y_clf = np.random.randint(0, 3, n_samples)
        
        # Create regression target
        y_reg = np.random.randn(n_samples)
        
        # Create DataFrame
        data_clf = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data_clf['target'] = y_clf
        
        data_reg = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data_reg['target'] = y_reg
    
    return data_clf, data_reg

def demonstrate_langgraph_tools():
    """Demonstrate how to create LangGraph tools for different estimators."""
    print("LangGraph Integration Example")
    print("=" * 50)
    
    # Create tools for different estimator types
    estimators_to_demo = [
        "random_forest_classifier",
        "linear_regression", 
        "kmeans",
        "pca"
    ]
    
    print("\nCreating LangGraph tool definitions:")
    for estimator_name in estimators_to_demo:
        print(f"\n--- {estimator_name.upper()} ---")
        tool = create_langgraph_tool(estimator_name)
        
        print(f"Tool name: {tool['name']}")
        print(f"Description: {tool['description'][:100]}...")
        print(f"Required parameters: {tool['parameters']['required']}")
        print(f"Optional parameters: {[k for k in tool['parameters']['properties'].keys() if k not in tool['parameters']['required']]}")
    
    return estimators_to_demo

def demonstrate_universal_estimator():
    """Demonstrate the universal estimator function."""
    print("\n" + "=" * 50)
    print("Universal Estimator Demonstration")
    print("=" * 50)
    
    # Create sample data
    data_clf, data_reg = create_sample_data()
    
    # Example 1: Classification
    print("\n1. Classification Example (Random Forest)")
    result = universal_estimator(
        estimator_name="random_forest_classifier",
        data=data_clf,
        target_column="target",
        n_estimators=50,
        max_depth=5,
        random_state=42
    )
    
    if result['success']:
        print(f"✓ Successfully trained {result['estimator_name']}")
        print(f"  Accuracy: {result['metrics']['accuracy']:.4f}")
        print(f"  F1-Score: {result['metrics']['f1']:.4f}")
        print(f"  Top 3 features: {sorted(result['feature_importance'].items(), key=lambda x: x[1], reverse=True)[:3]}")
    else:
        print(f"✗ Failed: {result['error']}")
    
    # Example 2: Regression
    print("\n2. Regression Example (Linear Regression)")
    result = universal_estimator(
        estimator_name="linear_regression",
        data=data_reg,
        target_column="target"
    )
    
    if result['success']:
        print(f"✓ Successfully trained {result['estimator_name']}")
        print(f"  R² Score: {result['metrics']['r2']:.4f}")
        print(f"  MSE: {result['metrics']['mse']:.4f}")
        print(f"  Top 3 features: {sorted(result['feature_importance'].items(), key=lambda x: abs(x[1]), reverse=True)[:3]}")
    else:
        print(f"✗ Failed: {result['error']}")
    
    # Example 3: Clustering
    print("\n3. Clustering Example (K-Means)")
    result = universal_estimator(
        estimator_name="kmeans",
        data=data_clf.drop(columns=['target']),
        target_column=None,
        n_clusters=3,
        random_state=42
    )
    
    if result['success']:
        print(f"✓ Successfully performed {result['estimator_name']}")
        print(f"  Number of clusters: {result['n_clusters']}")
        print(f"  Silhouette score: {result['metrics'].get('silhouette', 'N/A')}")
        print(f"  Cluster distribution: {np.bincount(result['clusters'])}")
    else:
        print(f"✗ Failed: {result['error']}")
    
    # Example 4: Dimensionality Reduction
    print("\n4. Dimensionality Reduction Example (PCA)")
    result = universal_estimator(
        estimator_name="pca",
        data=data_clf.drop(columns=['target']),
        target_column=None,
        n_components=3
    )
    
    if result['success']:
        print(f"✓ Successfully applied {result['estimator_name']}")
        print(f"  Original shape: {result['data_shape']['original']}")
        print(f"  Transformed shape: {result['data_shape']['transformed']}")
        print(f"  Explained variance: {result['metrics']['explained_variance_ratio']}")
        print(f"  Cumulative variance: {result['metrics']['cumulative_variance_ratio'][-1]:.4f}")
    else:
        print(f"✗ Failed: {result['error']}")

def demonstrate_parameter_validation():
    """Demonstrate parameter validation."""
    print("\n" + "=" * 50)
    print("Parameter Validation Demonstration")
    print("=" * 50)
    
    from universal_estimator import validate_estimator_parameters
    
    # Test valid parameters
    print("\n1. Valid parameters for Random Forest:")
    validation = validate_estimator_parameters("random_forest_classifier", {
        "n_estimators": 100,
        "max_depth": 10,
        "random_state": 42
    })
    print(f"  Valid: {validation['valid']}")
    print(f"  Warnings: {validation['warnings']}")
    print(f"  Errors: {validation['errors']}")
    
    # Test invalid parameters
    print("\n2. Invalid parameters for Random Forest:")
    validation = validate_estimator_parameters("random_forest_classifier", {
        "n_estimators": 100,
        "invalid_param": "test",
        "another_invalid": 123
    })
    print(f"  Valid: {validation['valid']}")
    print(f"  Warnings: {validation['warnings']}")
    print(f"  Errors: {validation['errors']}")

def demonstrate_estimator_info():
    """Demonstrate estimator information extraction."""
    print("\n" + "=" * 50)
    print("Estimator Information Demonstration")
    print("=" * 50)
    
    from universal_estimator import extract_estimator_info, get_estimator_tool_description
    
    estimators_to_info = ["svc", "gradient_boosting_regressor", "gaussian_nb"]
    
    for estimator_name in estimators_to_info:
        print(f"\n--- {estimator_name.upper()} ---")
        info = extract_estimator_info(estimator_name)
        
        if "error" not in info:
            print(f"  Class: {info['class_name']}")
            print(f"  Type: {info['type']}")
            print(f"  Metrics: {info['metrics']}")
            print(f"  Parameters: {list(info['parameters'].keys())[:5]}...")  # Show first 5
            
            # Show tool description
            description = get_estimator_tool_description(estimator_name)
            print(f"  Description: {description[:150]}...")
        else:
            print(f"  Error: {info['error']}")

def main():
    """Main demonstration function."""
    print("Universal Estimator - LangGraph Integration Example")
    print("=" * 60)
    
    # Show available estimators
    print("\nAvailable Estimators:")
    estimators = get_available_estimators()
    for estimator_type, type_estimators in estimators.items():
        print(f"\n{estimator_type.upper()} ({len(type_estimators)} estimators):")
        for name, info in type_estimators.items():
            print(f"  - {name}: {info['description']}")
    
    # Demonstrate LangGraph tools
    demonstrate_langgraph_tools()
    
    # Demonstrate universal estimator
    demonstrate_universal_estimator()
    
    # Demonstrate parameter validation
    demonstrate_parameter_validation()
    
    # Demonstrate estimator info
    demonstrate_estimator_info()
    
    print("\n" + "=" * 60)
    print("Demonstration completed!")
    print("\nTo use with LangGraph:")
    print("1. Import the universal_estimator module")
    print("2. Use create_langgraph_tool() to create tool definitions")
    print("3. Use universal_estimator() as your tool function")
    print("4. Handle the results in your LangGraph agent")

if __name__ == "__main__":
    main()
