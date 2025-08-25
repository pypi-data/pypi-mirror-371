"""
Tests for the UniversalSklearnEstimator class (refactored version).

This module tests the main universal estimator interface that combines
all specialized algorithm modules.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the universal estimator
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from universal_estimator_refactored import UniversalSklearnEstimator, universal_estimator


class TestUniversalSklearnEstimator:
    """Test class for UniversalSklearnEstimator functionality."""
    
    @pytest.fixture
    def universal_estimator_instance(self):
        """Create a universal estimator instance for testing."""
        return UniversalSklearnEstimator()
    
    @pytest.fixture
    def sample_classification_data(self):
        """Create sample classification data for testing."""
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        # Create sample data
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 3, n_samples)  # 3 classes
        
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data['target'] = y
        
        return data
    
    @pytest.fixture
    def sample_regression_data(self):
        """Create sample regression data for testing."""
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        # Create sample data with continuous target
        X = np.random.randn(n_samples, n_features)
        y = np.random.randn(n_samples)  # Continuous target
        
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data['target'] = y
        
        return data
    
    @pytest.fixture
    def sample_clustering_data(self):
        """Create sample clustering data for testing."""
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        # Create sample data (no target column for clustering)
        X = np.random.randn(n_samples, n_features)
        
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        
        return data
    
    def test_initialization(self, universal_estimator_instance):
        """Test universal estimator initialization."""
        assert universal_estimator_instance.classification_models is not None
        assert universal_estimator_instance.regression_models is not None
        assert universal_estimator_instance.clustering_models is not None
        assert universal_estimator_instance.preprocessing_models is not None
        assert universal_estimator_instance.all_models is not None
        assert universal_estimator_instance.all_available_models is not None
    
    def test_combine_model_mappings(self, universal_estimator_instance):
        """Test that model mappings are combined correctly."""
        all_models = universal_estimator_instance.all_models
        
        # Check that we have models from all categories
        classification_models = [name for name in all_models.keys() if name.startswith('classification_')]
        regression_models = [name for name in all_models.keys() if name.startswith('regression_')]
        clustering_models = [name for name in all_models.keys() if name.startswith('clustering_')]
        preprocessing_models = [name for name in all_models.keys() if name.startswith('preprocessing_')]
        
        assert len(classification_models) > 0
        assert len(regression_models) > 0
        assert len(clustering_models) > 0
        assert len(preprocessing_models) > 0
    
    def test_combine_available_models(self, universal_estimator_instance):
        """Test that available models are combined correctly."""
        all_available_models = universal_estimator_instance.all_available_models
        
        assert "classification" in all_available_models
        assert "regression" in all_available_models
        assert "clustering" in all_available_models
        assert "preprocessing" in all_available_models
    
    @pytest.mark.parametrize("model_name,expected_type", [
        ("classification_logistic_regression", "classification"),
        ("regression_linear_regression", "regression"),
        ("clustering_kmeans", "clustering"),
        ("preprocessing_pca", "preprocessing")
    ])
    def test_get_model_type_and_name(self, universal_estimator_instance, model_name, expected_type):
        """Test model type and name extraction."""
        model_type, actual_name = universal_estimator_instance._get_model_type_and_name(model_name)
        
        assert model_type == expected_type
        # The actual name should be the class name without the prefix
        expected_class_name = model_name.split("_", 1)[1]  # Remove prefix
        assert actual_name == expected_class_name
    
    def test_get_model_type_and_name_inference(self, universal_estimator_instance):
        """Test model type inference from model name."""
        # Test inference for models without prefix - should infer type based on keywords
        model_type, actual_name = universal_estimator_instance._get_model_type_and_name("svc")
        assert model_type == "classification"
        
        model_type, actual_name = universal_estimator_instance._get_model_type_and_name("linear_regression")
        assert model_type == "regression"
        
        model_type, actual_name = universal_estimator_instance._get_model_type_and_name("kmeans")
        assert model_type == "clustering"
        
        model_type, actual_name = universal_estimator_instance._get_model_type_and_name("pca")
        assert model_type == "preprocessing"
    
    def test_get_model_type_and_name_invalid(self, universal_estimator_instance):
        """Test model type extraction for invalid model name."""
        with pytest.raises(ValueError):
            universal_estimator_instance._get_model_type_and_name("invalid_model")
    
    def test_fit_model_classification(self, universal_estimator_instance, sample_classification_data):
        """Test fitting classification model through universal interface."""
        result = universal_estimator_instance.fit_model(
            "classification_logistic_regression",
            sample_classification_data,
            target_column="target",
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "logistic_regression"
        assert "model" in result
        assert "metrics" in result
        assert "predictions" in result
    
    def test_fit_model_regression(self, universal_estimator_instance, sample_regression_data):
        """Test fitting regression model through universal interface."""
        result = universal_estimator_instance.fit_model(
            "regression_linear_regression",
            sample_regression_data,
            target_column="target",
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "linear_regression"
        assert "model" in result
        assert "metrics" in result
        assert "predictions" in result
    
    def test_fit_model_clustering(self, universal_estimator_instance, sample_clustering_data):
        """Test fitting clustering model through universal interface."""
        result = universal_estimator_instance.fit_model(
            "clustering_kmeans",
            sample_clustering_data,
            n_clusters=3,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "kmeans"
        assert "model" in result
        assert "metrics" in result
        assert "clusters" in result
        assert "n_clusters" in result
    
    def test_fit_model_preprocessing(self, universal_estimator_instance, sample_clustering_data):
        """Test fitting preprocessing model through universal interface."""
        result = universal_estimator_instance.fit_model(
            "preprocessing_pca",
            sample_clustering_data,
            n_components=3
        )
        
        assert result["success"] is True
        assert result["model_name"] == "pca"
        assert "model" in result
        assert "metrics" in result
        assert "transformed_data" in result
        assert "transformed_shape" in result
    
    def test_fit_model_invalid_type(self, universal_estimator_instance, sample_classification_data):
        """Test fitting with invalid model type."""
        result = universal_estimator_instance.fit_model(
            "invalid_type_logistic_regression",
            sample_classification_data,
            target_column="target"
        )
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    def test_fit_model_invalid_model(self, universal_estimator_instance, sample_classification_data):
        """Test fitting with invalid model name."""
        result = universal_estimator_instance.fit_model(
            "classification_invalid_model",
            sample_classification_data,
            target_column="target"
        )
        
        assert result["success"] is False
        assert "error" in result
    
    def test_get_model_info_classification(self, universal_estimator_instance):
        """Test getting model info for classification model."""
        info = universal_estimator_instance.get_model_info("classification_logistic_regression")
        
        assert "error" not in info
        assert info["model_name"] == "logistic_regression"
        assert info["type"] == "classifier"
    
    def test_get_model_info_regression(self, universal_estimator_instance):
        """Test getting model info for regression model."""
        info = universal_estimator_instance.get_model_info("regression_linear_regression")
        
        assert "error" not in info
        assert info["model_name"] == "linear_regression"
        assert info["type"] == "regressor"
    
    def test_get_model_info_clustering(self, universal_estimator_instance):
        """Test getting model info for clustering model."""
        info = universal_estimator_instance.get_model_info("clustering_kmeans")
        
        assert "error" not in info
        assert info["model_name"] == "kmeans"
        assert info["type"] == "clustering"
    
    def test_get_model_info_preprocessing(self, universal_estimator_instance):
        """Test getting model info for preprocessing model."""
        info = universal_estimator_instance.get_model_info("preprocessing_pca")
        
        assert "error" not in info
        assert info["model_name"] == "pca"
        assert info["type"] == "preprocessor"
    
    def test_get_model_info_invalid(self, universal_estimator_instance):
        """Test getting model info for invalid model."""
        info = universal_estimator_instance.get_model_info("invalid_model")
        
        assert "error" in info
    
    def test_get_model_tool_description_classification(self, universal_estimator_instance):
        """Test getting tool description for classification model."""
        description = universal_estimator_instance.get_model_tool_description("classification_logistic_regression")
        
        assert "Logistic regression" in description
        assert "classifier" in description
    
    def test_get_model_tool_description_regression(self, universal_estimator_instance):
        """Test getting tool description for regression model."""
        description = universal_estimator_instance.get_model_tool_description("regression_linear_regression")
        
        assert "Linear Regression" in description
        assert "regressor" in description
    
    def test_get_model_tool_description_clustering(self, universal_estimator_instance):
        """Test getting tool description for clustering model."""
        description = universal_estimator_instance.get_model_tool_description("clustering_kmeans")
        
        assert "K-Means clustering" in description
        assert "clustering" in description
    
    def test_get_model_tool_description_preprocessing(self, universal_estimator_instance):
        """Test getting tool description for preprocessing model."""
        description = universal_estimator_instance.get_model_tool_description("preprocessing_pca")
        
        assert "Principal Component Analysis" in description
        assert "preprocessor" in description
    
    def test_get_model_tool_description_invalid(self, universal_estimator_instance):
        """Test getting tool description for invalid model."""
        description = universal_estimator_instance.get_model_tool_description("invalid_model")
        
        assert description.startswith("Error:")
    
    def test_validate_model_parameters_classification(self, universal_estimator_instance):
        """Test parameter validation for classification model."""
        validation = universal_estimator_instance.validate_model_parameters(
            "classification_logistic_regression",
            {"C": 1.0, "random_state": 42}
        )
        
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
    
    def test_validate_model_parameters_regression(self, universal_estimator_instance):
        """Test parameter validation for regression model."""
        validation = universal_estimator_instance.validate_model_parameters(
            "regression_linear_regression",
            {"fit_intercept": True}
        )
        
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
    
    def test_validate_model_parameters_clustering(self, universal_estimator_instance):
        """Test parameter validation for clustering model."""
        validation = universal_estimator_instance.validate_model_parameters(
            "clustering_kmeans",
            {"n_clusters": 3, "random_state": 42}
        )
        
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
    
    def test_validate_model_parameters_preprocessing(self, universal_estimator_instance):
        """Test parameter validation for preprocessing model."""
        validation = universal_estimator_instance.validate_model_parameters(
            "preprocessing_pca",
            {"n_components": 3, "random_state": 42}
        )
        
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
    
    def test_validate_model_parameters_invalid(self, universal_estimator_instance):
        """Test parameter validation for invalid model."""
        validation = universal_estimator_instance.validate_model_parameters(
            "invalid_model",
            {"param": 1.0}
        )
        
        assert validation["valid"] is False
        assert "Could not determine model type" in validation["error"]
    
    def test_create_langgraph_tool_classification(self, universal_estimator_instance):
        """Test creating LangGraph tool for classification model."""
        tool_def = universal_estimator_instance.create_langgraph_tool("classification_logistic_regression")
        
        assert "error" not in tool_def
        assert "name" in tool_def
        assert "description" in tool_def
        assert "parameters" in tool_def
        assert tool_def["name"] == "train_logistic_regression"
    
    def test_create_langgraph_tool_regression(self, universal_estimator_instance):
        """Test creating LangGraph tool for regression model."""
        tool_def = universal_estimator_instance.create_langgraph_tool("regression_linear_regression")
        
        assert "error" not in tool_def
        assert "name" in tool_def
        assert "description" in tool_def
        assert "parameters" in tool_def
        assert tool_def["name"] == "train_linear_regression"
    
    def test_create_langgraph_tool_clustering(self, universal_estimator_instance):
        """Test creating LangGraph tool for clustering model."""
        tool_def = universal_estimator_instance.create_langgraph_tool("clustering_kmeans")
        
        assert "error" not in tool_def
        assert "name" in tool_def
        assert "description" in tool_def
        assert "parameters" in tool_def
        assert tool_def["name"] == "train_kmeans"
    
    def test_create_langgraph_tool_preprocessing(self, universal_estimator_instance):
        """Test creating LangGraph tool for preprocessing model."""
        tool_def = universal_estimator_instance.create_langgraph_tool("preprocessing_pca")
        
        assert "error" not in tool_def
        assert "name" in tool_def
        assert "description" in tool_def
        assert "parameters" in tool_def
        assert tool_def["name"] == "train_pca"
    
    def test_create_langgraph_tool_invalid(self, universal_estimator_instance):
        """Test creating LangGraph tool for invalid model."""
        tool_def = universal_estimator_instance.create_langgraph_tool("invalid_model")
        
        assert "error" in tool_def
    
    def test_get_available_models(self, universal_estimator_instance):
        """Test getting all available models."""
        models = universal_estimator_instance.get_available_models()
        
        assert "classification" in models
        assert "regression" in models
        assert "clustering" in models
        assert "preprocessing" in models
        
        # Check that each category has models
        assert len(models["classification"]) > 0
        assert len(models["regression"]) > 0
        assert len(models["clustering"]) > 0
        assert len(models["preprocessing"]) > 0
    
    def test_get_all_model_names(self, universal_estimator_instance):
        """Test getting all model names."""
        model_names = universal_estimator_instance.get_all_model_names()
        
        assert len(model_names) > 0
        assert all(isinstance(name, str) for name in model_names)
        
        # Check that we have models from all categories
        classification_models = [name for name in model_names if name.startswith('classification_')]
        regression_models = [name for name in model_names if name.startswith('regression_')]
        clustering_models = [name for name in model_names if name.startswith('clustering_')]
        preprocessing_models = [name for name in model_names if name.startswith('preprocessing_')]
        
        assert len(classification_models) > 0
        assert len(regression_models) > 0
        assert len(clustering_models) > 0
        assert len(preprocessing_models) > 0
    
    def test_search_models(self, universal_estimator_instance):
        """Test searching for models."""
        # Search for random forest models
        random_forest_models = universal_estimator_instance.search_models("random forest")
        
        assert len(random_forest_models) > 0
        assert all("random_forest" in name.lower() for name in random_forest_models)
        
        # Search for linear models
        linear_models = universal_estimator_instance.search_models("linear")
        
        assert len(linear_models) > 0
        # Most should contain "linear", but some like LDA (Linear Discriminant Analysis) might not
        linear_containing = [name for name in linear_models if "linear" in name.lower()]
        assert len(linear_containing) > 0  # At least some should contain "linear"
        
        # Search for clustering models
        clustering_models = universal_estimator_instance.search_models("clustering")
        
        assert len(clustering_models) > 0
        assert all("clustering" in name.lower() for name in clustering_models)
    
    def test_get_models_by_type(self, universal_estimator_instance):
        """Test getting models by type."""
        # Get classification models
        classification_models = universal_estimator_instance.get_models_by_type("classification")
        
        assert len(classification_models) > 0
        assert all(name.startswith('classification_') for name in classification_models)
        
        # Get regression models
        regression_models = universal_estimator_instance.get_models_by_type("regression")
        
        assert len(regression_models) > 0
        assert all(name.startswith('regression_') for name in regression_models)
        
        # Get clustering models
        clustering_models = universal_estimator_instance.get_models_by_type("clustering")
        
        assert len(clustering_models) > 0
        assert all(name.startswith('clustering_') for name in clustering_models)
        
        # Get preprocessing models
        preprocessing_models = universal_estimator_instance.get_models_by_type("preprocessing")
        
        assert len(preprocessing_models) > 0
        assert all(name.startswith('preprocessing_') for name in preprocessing_models)
        
        # Test invalid type
        invalid_models = universal_estimator_instance.get_models_by_type("invalid")
        assert len(invalid_models) == 0
    
    def test_integration_all_model_types(self, universal_estimator_instance, sample_classification_data, sample_regression_data, sample_clustering_data):
        """Test integration of all model types through the universal interface."""
        # Test classification
        result_clf = universal_estimator_instance.fit_model(
            "classification_logistic_regression",
            sample_classification_data,
            target_column="target",
            random_state=42
        )
        assert result_clf["success"] is True
        
        # Test regression
        result_reg = universal_estimator_instance.fit_model(
            "regression_linear_regression",
            sample_regression_data,
            target_column="target",
            random_state=42
        )
        assert result_reg["success"] is True
        
        # Test clustering
        result_cluster = universal_estimator_instance.fit_model(
            "clustering_kmeans",
            sample_clustering_data,
            n_clusters=3,
            random_state=42
        )
        assert result_cluster["success"] is True
        
        # Test preprocessing
        result_preproc = universal_estimator_instance.fit_model(
            "preprocessing_pca",
            sample_clustering_data,
            n_components=3
        )
        assert result_preproc["success"] is True


class TestUniversalEstimatorFunction:
    """Test class for the universal_estimator function (backward compatibility)."""
    
    @pytest.fixture
    def sample_classification_data(self):
        """Create sample classification data for testing."""
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        # Create sample data
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 3, n_samples)  # 3 classes
        
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data['target'] = y
        
        return data
    
    @pytest.fixture
    def sample_regression_data(self):
        """Create sample regression data for testing."""
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        # Create sample data with continuous target
        X = np.random.randn(n_samples, n_features)
        y = np.random.randn(n_samples)  # Continuous target
        
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data['target'] = y
        
        return data
    
    @pytest.fixture
    def sample_clustering_data(self):
        """Create sample clustering data for testing."""
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        # Create sample data (no target column for clustering)
        X = np.random.randn(n_samples, n_features)
        
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        
        return data
    
    def test_universal_estimator_classification(self, sample_classification_data):
        """Test universal_estimator function with classification."""
        result = universal_estimator(
            "logistic_regression",
            sample_classification_data,
            target_column="target",
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "logistic_regression"
        assert "model" in result
        assert "metrics" in result
        assert "predictions" in result
    
    def test_universal_estimator_regression(self, sample_regression_data):
        """Test universal_estimator function with regression."""
        result = universal_estimator(
            "linear_regression",
            sample_regression_data,
            target_column="target",
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "linear_regression"
        assert "model" in result
        assert "metrics" in result
        assert "predictions" in result
    
    def test_universal_estimator_clustering(self, sample_clustering_data):
        """Test universal_estimator function with clustering."""
        result = universal_estimator(
            "kmeans",
            sample_clustering_data,
            n_clusters=3,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "kmeans"
        assert "model" in result
        assert "metrics" in result
        assert "clusters" in result
        assert "n_clusters" in result
    
    def test_universal_estimator_preprocessing(self, sample_clustering_data):
        """Test universal_estimator function with preprocessing."""
        result = universal_estimator(
            "pca",
            sample_clustering_data,
            n_components=3
        )
        
        assert result["success"] is True
        assert result["model_name"] == "pca"
        assert "model" in result
        assert "metrics" in result
        assert "transformed_data" in result
        assert "transformed_shape" in result
    
    def test_universal_estimator_with_parameters(self, sample_classification_data):
        """Test universal_estimator function with additional parameters."""
        result = universal_estimator(
            "random_forest_classifier",
            sample_classification_data,
            target_column="target",
            n_estimators=10,
            max_depth=5,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "random_forest_classifier"
        assert "model" in result
        assert "metrics" in result
        assert "feature_importance" in result
    
    def test_universal_estimator_invalid_model(self, sample_classification_data):
        """Test universal_estimator function with invalid model."""
        result = universal_estimator(
            "invalid_model",
            sample_classification_data,
            target_column="target"
        )
        
        assert result["success"] is False
        assert "error" in result
    
    def test_universal_estimator_missing_target(self, sample_classification_data):
        """Test universal_estimator function without target column."""
        result = universal_estimator(
            "logistic_regression",
            sample_classification_data
        )
        
        assert result["success"] is False
        assert "error" in result
    
    def test_universal_estimator_different_test_sizes(self, sample_classification_data):
        """Test universal_estimator function with different test sizes."""
        test_sizes = [0.1, 0.2, 0.3]
        
        for test_size in test_sizes:
            result = universal_estimator(
                "logistic_regression",
                sample_classification_data,
                target_column="target",
                test_size=test_size,
                random_state=42
            )
            
            assert result["success"] is True
            assert "data_shape" in result
    
    def test_universal_estimator_different_random_states(self, sample_classification_data):
        """Test universal_estimator function with different random states."""
        random_states = [42, 123, 456]
        
        for random_state in random_states:
            result = universal_estimator(
                "logistic_regression",
                sample_classification_data,
                target_column="target",
                random_state=random_state
            )
            
            assert result["success"] is True
            assert "metrics" in result
