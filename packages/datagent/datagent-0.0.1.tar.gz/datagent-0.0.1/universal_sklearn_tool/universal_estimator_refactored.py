"""
Universal Scikit-learn Estimator (Refactored Version).

This module provides a unified interface to all scikit-learn algorithms using the
refactored modular architecture. It combines classification, regression, clustering,
and preprocessing models into a single, easy-to-use interface.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
import logging

from algos import (
    ClassificationModels,
    RegressionModels,
    ClusteringModels,
    PreprocessingModels
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniversalSklearnEstimator:
    """
    Universal Scikit-learn Estimator using refactored modules.
    
    This class provides a unified interface to all scikit-learn algorithms,
    automatically routing requests to the appropriate specialized module.
    """
    
    def __init__(self):
        """Initialize the universal estimator with all algorithm modules."""
        self.classification_models = ClassificationModels()
        self.regression_models = RegressionModels()
        self.clustering_models = ClusteringModels()
        self.preprocessing_models = PreprocessingModels()
        
        # Combined model mappings
        self.all_models = self._combine_model_mappings()
        self.all_available_models = self._combine_available_models()
    
    def _combine_model_mappings(self) -> Dict[str, Any]:
        """Combine all model mappings from different modules."""
        combined = {}
        
        # Add classification models
        for name, config in self.classification_models.model_mapping.items():
            combined[f"classification_{name}"] = config
        
        # Add regression models
        for name, config in self.regression_models.model_mapping.items():
            combined[f"regression_{name}"] = config
        
        # Add clustering models
        for name, config in self.clustering_models.model_mapping.items():
            combined[f"clustering_{name}"] = config
        
        # Add preprocessing models
        for name, config in self.preprocessing_models.model_mapping.items():
            combined[f"preprocessing_{name}"] = config
        
        return combined
    
    def _combine_available_models(self) -> Dict[str, Any]:
        """Combine all available models from different modules."""
        combined = {
            "classification": self.classification_models.get_available_models(),
            "regression": self.regression_models.get_available_models(),
            "clustering": self.clustering_models.get_available_models(),
            "preprocessing": self.preprocessing_models.get_available_models()
        }
        return combined
    
    def _get_model_type_and_name(self, model_name: str) -> Tuple[str, str]:
        """
        Extract model type and name from the combined model name.
        
        Args:
            model_name: Combined model name (e.g., 'classification_random_forest_classifier')
            
        Returns:
            Tuple of (model_type, actual_model_name)
        """
        if model_name.startswith('classification_'):
            return 'classification', model_name.replace('classification_', '')
        elif model_name.startswith('regression_'):
            return 'regression', model_name.replace('regression_', '')
        elif model_name.startswith('clustering_'):
            return 'clustering', model_name.replace('clustering_', '')
        elif model_name.startswith('preprocessing_'):
            return 'preprocessing', model_name.replace('preprocessing_', '')
        else:
            # Try to infer the type based on the model name
            # Check for classification keywords first (more specific)
            if any(keyword in model_name for keyword in ['classifier', 'nb', 'svc', 'lda', 'qda', 'logistic']):
                return 'classification', model_name
            elif any(keyword in model_name for keyword in ['regressor', 'svr', 'linear']):
                return 'regression', model_name
            elif any(keyword in model_name for keyword in ['clustering', 'kmeans', 'dbscan']):
                return 'clustering', model_name
            elif any(keyword in model_name for keyword in ['pca', 'svd', 'ica', 'select', 'rfe']):
                return 'preprocessing', model_name
            else:
                raise ValueError(f"Could not determine model type for '{model_name}'")
    
    def fit_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Fit a model using the appropriate specialized module.
        
        Args:
            model_name: Name of the model to fit
            data: Input DataFrame
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing model fitting results
        """
        try:
            # Determine model type and actual model name
            model_type, actual_model_name = self._get_model_type_and_name(model_name)
            
            # Route to appropriate module
            if model_type == 'classification':
                return self.classification_models.fit_model(actual_model_name, data, **kwargs)
            elif model_type == 'regression':
                return self.regression_models.fit_model(actual_model_name, data, **kwargs)
            elif model_type == 'clustering':
                return self.clustering_models.fit_model(actual_model_name, data, **kwargs)
            elif model_type == 'preprocessing':
                return self.preprocessing_models.fit_model(actual_model_name, data, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown model type: {model_type}",
                    "model_name": model_name
                }
                
        except Exception as e:
            logger.error(f"Failed to fit model {model_name}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to fit model {model_name}: {str(e)}",
                "model_name": model_name
            }
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary containing model information
        """
        try:
            model_type, actual_model_name = self._get_model_type_and_name(model_name)
            
            if model_type == 'classification':
                return self.classification_models.extract_model_info(actual_model_name)
            elif model_type == 'regression':
                return self.regression_models.extract_model_info(actual_model_name)
            elif model_type == 'clustering':
                return self.clustering_models.extract_model_info(actual_model_name)
            elif model_type == 'preprocessing':
                return self.preprocessing_models.extract_model_info(actual_model_name)
            else:
                return {"error": f"Unknown model type: {model_type}"}
                
        except Exception as e:
            return {"error": f"Failed to get model info: {str(e)}"}
    
    def get_model_tool_description(self, model_name: str) -> str:
        """
        Get tool description for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Tool description string
        """
        try:
            model_type, actual_model_name = self._get_model_type_and_name(model_name)
            
            if model_type == 'classification':
                return self.classification_models.get_model_tool_description(actual_model_name)
            elif model_type == 'regression':
                return self.regression_models.get_model_tool_description(actual_model_name)
            elif model_type == 'clustering':
                return self.clustering_models.get_model_tool_description(actual_model_name)
            elif model_type == 'preprocessing':
                return self.preprocessing_models.get_model_tool_description(actual_model_name)
            else:
                return f"Error: Unknown model type: {model_type}"
                
        except Exception as e:
            return f"Error: Failed to get tool description: {str(e)}"
    
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
            model_type, actual_model_name = self._get_model_type_and_name(model_name)
            
            if model_type == 'classification':
                return self.classification_models.validate_model_parameters(actual_model_name, parameters)
            elif model_type == 'regression':
                return self.regression_models.validate_model_parameters(actual_model_name, parameters)
            elif model_type == 'clustering':
                return self.clustering_models.validate_model_parameters(actual_model_name, parameters)
            elif model_type == 'preprocessing':
                return self.preprocessing_models.validate_model_parameters(actual_model_name, parameters)
            else:
                return {
                    "valid": False,
                    "error": f"Unknown model type: {model_type}"
                }
                
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
        try:
            model_type, actual_model_name = self._get_model_type_and_name(model_name)
            
            if model_type == 'classification':
                return self.classification_models.create_langgraph_tool(actual_model_name)
            elif model_type == 'regression':
                return self.regression_models.create_langgraph_tool(actual_model_name)
            elif model_type == 'clustering':
                return self.clustering_models.create_langgraph_tool(actual_model_name)
            elif model_type == 'preprocessing':
                return self.preprocessing_models.create_langgraph_tool(actual_model_name)
            else:
                return {"error": f"Unknown model type: {model_type}"}
                
        except Exception as e:
            return {"error": f"Failed to create tool: {str(e)}"}
    
    def get_available_models(self) -> Dict[str, Any]:
        """
        Get all available models grouped by type.
        
        Returns:
            Dictionary of all available models
        """
        return self.all_available_models
    
    def get_all_model_names(self) -> List[str]:
        """
        Get a list of all available model names.
        
        Returns:
            List of all model names
        """
        return list(self.all_models.keys())
    
    def search_models(self, query: str) -> List[str]:
        """
        Search for models by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching model names
        """
        query = query.lower()
        matching_models = []
        
        for model_name, config in self.all_models.items():
            if (query in model_name.lower() or 
                query in config['description'].lower() or
                query in config['class'].lower()):
                matching_models.append(model_name)
        
        return matching_models
    
    def get_models_by_type(self, model_type: str) -> List[str]:
        """
        Get all models of a specific type.
        
        Args:
            model_type: Type of models to return ('classification', 'regression', 'clustering', 'preprocessing')
            
        Returns:
            List of model names of the specified type
        """
        if model_type not in ['classification', 'regression', 'clustering', 'preprocessing']:
            return []
        
        return [name for name in self.all_models.keys() if name.startswith(f"{model_type}_")]


# Convenience function for backward compatibility
def universal_estimator(
    estimator_name: str,
    data: pd.DataFrame,
    target_column: str = None,
    test_size: float = 0.2,
    random_state: int = 42,
    **estimator_params
) -> Dict[str, Any]:
    """
    Universal function to train any scikit-learn estimator (refactored version).
    
    This function provides backward compatibility with the original universal_estimator
    while using the new refactored architecture.
    
    Args:
        estimator_name: Name of the estimator
        data: Input DataFrame
        target_column: Name of the target column (not needed for clustering/preprocessing)
        test_size: Fraction of data to use for testing (for supervised learning)
        random_state: Random state for reproducibility
        **estimator_params: Parameters to pass to the estimator
        
    Returns:
        Dictionary containing training results
    """
    # Create universal estimator instance
    estimator = UniversalSklearnEstimator()
    
    # Determine model type and create prefixed name
    model_type = None
    try:
        model_type, actual_name = estimator._get_model_type_and_name(estimator_name)
        prefixed_name = f"{model_type}_{estimator_name}"
    except ValueError:
        # If model type inference fails, try the original name
        prefixed_name = estimator_name
    
    # Prepare parameters based on model type
    if model_type in ['classification', 'regression']:
        # Supervised learning models need target_column and test_size
        params = {
            'target_column': target_column,
            'test_size': test_size,
            'random_state': random_state,
            **estimator_params
        }
    else:
        # Unsupervised learning models (clustering, preprocessing) don't need target_column
        params = {
            'random_state': random_state,
            **estimator_params
        }
    
    # Fit the model
    return estimator.fit_model(prefixed_name, data, **params)


# Example usage and testing functions
def example_usage():
    """Example usage of the refactored universal estimator."""
    import pandas as pd
    import numpy as np
    from sklearn.datasets import load_iris, load_diabetes, load_wine
    
    # Create universal estimator instance
    estimator = UniversalSklearnEstimator()
    
    try:
        # Classification data - Iris dataset
        iris = load_iris()
        data_clf = pd.DataFrame(iris.data, columns=iris.feature_names)
        data_clf['target'] = iris.target
        
        # Regression data - Diabetes dataset
        diabetes = load_diabetes()
        data_reg = pd.DataFrame(diabetes.data, columns=diabetes.feature_names)
        data_reg['target'] = diabetes.target
        
        # Clustering data - Wine dataset without target
        wine = load_wine()
        data_cluster = pd.DataFrame(wine.data, columns=wine.feature_names)
        
    except Exception as e:
        print(f"Warning: Could not load scikit-learn datasets: {e}")
        print("Falling back to synthetic data...")
        
        # Fallback to synthetic data
        np.random.seed(42)
        n_samples = 1000
        n_features = 10
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 3, n_samples)  # 3 classes for classification
        
        data_clf = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data_clf['target'] = y
        
        y_reg = np.random.randn(n_samples)  # Continuous target for regression
        data_reg = data_clf.copy()
        data_reg['target'] = y_reg
        
        data_cluster = data_clf.drop(columns=['target'])
    
    # Example 1: Train a Random Forest Classifier
    print("=== Training Random Forest Classifier ===")
    result1 = estimator.fit_model(
        "classification_random_forest_classifier",
        data_clf,
        target_column="target",
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    print(f"Success: {result1['success']}")
    if result1['success']:
        print(f"Metrics: {result1['metrics']}")
    
    # Example 2: Train a Linear Regression
    print("\n=== Training Linear Regression ===")
    result2 = estimator.fit_model(
        "regression_linear_regression",
        data_reg,
        target_column="target"
    )
    print(f"Success: {result2['success']}")
    if result2['success']:
        print(f"Metrics: {result2['metrics']}")
    
    # Example 3: Perform K-Means Clustering
    print("\n=== Performing K-Means Clustering ===")
    result3 = estimator.fit_model(
        "clustering_kmeans",
        data_cluster,
        n_clusters=3,
        random_state=42
    )
    print(f"Success: {result3['success']}")
    if result3['success']:
        print(f"Number of clusters: {result3['n_clusters']}")
        print(f"Metrics: {result3['metrics']}")
    
    # Example 4: Perform PCA
    print("\n=== Performing PCA ===")
    result4 = estimator.fit_model(
        "preprocessing_pca",
        data_cluster,
        n_components=3
    )
    print(f"Success: {result4['success']}")
    if result4['success']:
        print(f"Explained variance ratio: {result4['metrics']['explained_variance_ratio']}")


if __name__ == "__main__":
    # Print available models
    print("Available models:")
    estimator = UniversalSklearnEstimator()
    models = estimator.get_available_models()
    
    for model_type, type_models in models.items():
        print(f"\n{model_type.upper()}:")
        for category, category_models in type_models.items():
            print(f"  {category}:")
            for name, info in category_models.items():
                print(f"    - {name}: {info['description']}")
    
    # Run example usage
    print("\n" + "="*50)
    example_usage()
