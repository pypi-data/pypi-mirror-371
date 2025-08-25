"""
Tests for the ClassificationModels class.

This module tests the classification models functionality including
all supported classification algorithms from scikit-learn.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the classification models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from algos.classification import ClassificationModels


class TestClassificationModels:
    """Test class for ClassificationModels functionality."""
    
    @pytest.fixture
    def classification_models(self):
        """Create a classification models instance for testing."""
        return ClassificationModels()
    
    # Use fixtures from conftest.py instead of local data generation
    
    def test_initialization(self, classification_models):
        """Test classification models initialization."""
        assert classification_models.model_mapping is not None
        assert classification_models.available_models is not None
        
        # Check that we have classification models
        assert len(classification_models.model_mapping) > 0
        assert "logistic_regression" in classification_models.model_mapping
        assert "random_forest_classifier" in classification_models.model_mapping
    
    def test_get_available_models(self, classification_models):
        """Test getting available classification models."""
        models = classification_models.get_available_models()
        
        assert isinstance(models, dict)
        assert "linear_models" in models
        assert "tree_based" in models
        assert "support_vector_machines" in models
        assert "neural_networks" in models
        assert "naive_bayes" in models
        assert "discriminant_analysis" in models
        assert "gaussian_processes" in models
        assert "nearest_neighbors" in models
    
    @pytest.mark.parametrize("model_name", [
        "logistic_regression",
        "random_forest_classifier",
        "svc",
        "gaussian_nb",
        "knn_classifier"
    ])
    def test_model_mapping_contains_models(self, classification_models, model_name):
        """Test that specific models are in the mapping."""
        assert model_name in classification_models.model_mapping
        model_config = classification_models.model_mapping[model_name]
        
        assert "module" in model_config
        assert "class" in model_config
        assert "type" in model_config
        assert "metrics" in model_config
        assert "description" in model_config
        assert model_config["type"] == "classifier"
    
    def test_fit_model_logistic_regression(self, classification_models, sample_binary_data):
        """Test fitting logistic regression model."""
        result = classification_models.fit_model(
            "logistic_regression",
            sample_binary_data,
            target_column="target",
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "logistic_regression"
        assert "model" in result
        assert "metrics" in result
        assert "predictions" in result
        assert "data_shape" in result
        
        # Check metrics
        metrics = result["metrics"]
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics
        
        # Check that metrics are reasonable
        assert 0 <= metrics["accuracy"] <= 1
        assert 0 <= metrics["precision"] <= 1
        assert 0 <= metrics["recall"] <= 1
        assert 0 <= metrics["f1"] <= 1
    
    def test_fit_model_random_forest(self, classification_models, sample_classification_data):
        """Test fitting random forest classifier."""
        result = classification_models.fit_model(
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
        
        # Check feature importance
        feature_importance = result["feature_importance"]
        assert feature_importance is not None
        assert len(feature_importance) == 4  # 4 features (target is dropped)
    
    def test_fit_model_svc(self, classification_models, sample_binary_data):
        """Test fitting Support Vector Classifier."""
        result = classification_models.fit_model(
            "svc",
            sample_binary_data,
            target_column="target",
            kernel="rbf",
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "svc"
        assert "model" in result
        assert "metrics" in result
    
    def test_fit_model_gaussian_nb(self, classification_models, sample_classification_data):
        """Test fitting Gaussian Naive Bayes."""
        result = classification_models.fit_model(
            "gaussian_nb",
            sample_classification_data,
            target_column="target"
        )
        
        assert result["success"] is True
        assert result["model_name"] == "gaussian_nb"
        assert "model" in result
        assert "metrics" in result
    
    def test_fit_model_knn_classifier(self, classification_models, sample_classification_data):
        """Test fitting K-Nearest Neighbors classifier."""
        result = classification_models.fit_model(
            "knn_classifier",
            sample_classification_data,
            target_column="target",
            n_neighbors=5
        )
        
        assert result["success"] is True
        assert result["model_name"] == "knn_classifier"
        assert "model" in result
        assert "metrics" in result
    
    def test_fit_model_mlp_classifier(self, classification_models, sample_binary_data):
        """Test fitting Multi-layer Perceptron classifier."""
        result = classification_models.fit_model(
            "mlp_classifier",
            sample_binary_data,
            target_column="target",
            hidden_layer_sizes=(10,),
            max_iter=100,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "mlp_classifier"
        assert "model" in result
        assert "metrics" in result
    
    def test_fit_model_lda(self, classification_models, sample_classification_data):
        """Test fitting Linear Discriminant Analysis."""
        result = classification_models.fit_model(
            "lda",
            sample_classification_data,
            target_column="target"
        )
        
        assert result["success"] is True
        assert result["model_name"] == "lda"
        assert "model" in result
        assert "metrics" in result
    
    def test_fit_model_invalid_model(self, classification_models, sample_classification_data):
        """Test fitting with invalid model name."""
        result = classification_models.fit_model(
            "invalid_model",
            sample_classification_data,
            target_column="target"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_fit_model_missing_target(self, classification_models, sample_classification_data):
        """Test fitting without target column."""
        result = classification_models.fit_model(
            "logistic_regression",
            sample_classification_data
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "required" in result["error"].lower()
    
    def test_fit_model_missing_target_column(self, classification_models, sample_classification_data):
        """Test fitting with non-existent target column."""
        result = classification_models.fit_model(
            "logistic_regression",
            sample_classification_data,
            target_column="nonexistent"
        )
        
        assert result["success"] is False
        assert "error" in result
        # The error might be a list, so check if it's a string or list
        if isinstance(result["error"], list):
            error_msg = result["error"][0]
        else:
            error_msg = result["error"]
        assert "Target column 'nonexistent' not found" in error_msg
        assert "data columns" in error_msg
    
    def test_fit_model_with_categorical_features(self, classification_models):
        """Test fitting with categorical features."""
        np.random.seed(42)
        n_samples = 100
        
        # Create data with categorical features
        data = pd.DataFrame({
            'numeric_1': np.random.randn(n_samples),
            'numeric_2': np.random.randn(n_samples),
            'categorical_1': np.random.choice(['A', 'B', 'C'], n_samples),
            'categorical_2': np.random.choice(['X', 'Y'], n_samples),
            'target': np.random.randint(0, 2, n_samples)
        })
        
        result = classification_models.fit_model(
            "logistic_regression",
            data,
            target_column="target",
            random_state=42
        )
        
        assert result["success"] is True
        assert "label_encoders" in result
        assert len(result["label_encoders"]) > 0
    
    def test_fit_model_with_missing_values(self, classification_models):
        """Test fitting with missing values."""
        np.random.seed(42)
        n_samples = 100
        
        # Create data with missing values
        data = pd.DataFrame({
            'feature_1': np.random.randn(n_samples),
            'feature_2': np.random.randn(n_samples),
            'feature_3': np.random.randn(n_samples),
            'target': np.random.randint(0, 2, n_samples)
        })
        
        # Add some missing values
        data.loc[10:15, 'feature_1'] = np.nan
        data.loc[20:25, 'feature_2'] = np.nan
        
        result = classification_models.fit_model(
            "logistic_regression",
            data,
            target_column="target",
            random_state=42
        )
        
        assert result["success"] is True
        # Should handle missing values gracefully
    
    def test_extract_model_info_logistic_regression(self, classification_models):
        """Test extracting model info for logistic regression."""
        info = classification_models.extract_model_info("logistic_regression")
        
        assert "error" not in info
        assert info["model_name"] == "logistic_regression"
        assert info["class_name"] == "LogisticRegression"
        assert info["module_name"] == "sklearn.linear_model"
        assert info["type"] == "classifier"
        assert "accuracy" in info["metrics"]
        assert "precision" in info["metrics"]
        assert "recall" in info["metrics"]
        assert "f1" in info["metrics"]
    
    def test_extract_model_info_invalid_model(self, classification_models):
        """Test extracting model info for invalid model."""
        info = classification_models.extract_model_info("invalid_model")
        
        assert "error" in info
        assert "not found" in info["error"]
    
    def test_get_model_tool_description_logistic_regression(self, classification_models):
        """Test getting tool description for logistic regression."""
        description = classification_models.get_model_tool_description("logistic_regression")
        
        assert "Logistic regression" in description
        assert "LogisticRegression" in description
        assert "classifier" in description
        assert "accuracy" in description
        assert "precision" in description
        assert "recall" in description
        assert "f1" in description
    
    def test_get_model_tool_description_invalid_model(self, classification_models):
        """Test getting tool description for invalid model."""
        description = classification_models.get_model_tool_description("invalid_model")
        
        assert description.startswith("Error:")
    
    def test_validate_model_parameters_logistic_regression(self, classification_models):
        """Test parameter validation for logistic regression."""
        validation = classification_models.validate_model_parameters(
            "logistic_regression",
            {"C": 1.0, "random_state": 42}
        )
        
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
    
    def test_validate_model_parameters_invalid_model(self, classification_models):
        """Test parameter validation for invalid model."""
        validation = classification_models.validate_model_parameters(
            "invalid_model",
            {"C": 1.0}
        )
        
        assert validation["valid"] is False
        assert "not found" in validation["error"]
    
    def test_validate_model_parameters_unknown_param(self, classification_models):
        """Test parameter validation with unknown parameter."""
        validation = classification_models.validate_model_parameters(
            "logistic_regression",
            {"C": 1.0, "unknown_param": 42}
        )
        
        assert validation["valid"] is True
        assert len(validation["warnings"]) > 0
        assert "Unknown parameter" in validation["warnings"][0]
    
    def test_create_langgraph_tool_logistic_regression(self, classification_models):
        """Test creating LangGraph tool for logistic regression."""
        tool_def = classification_models.create_langgraph_tool("logistic_regression")
        
        assert "error" not in tool_def
        assert "name" in tool_def
        assert "description" in tool_def
        assert "parameters" in tool_def
        assert tool_def["name"] == "train_logistic_regression"
        assert "type" in tool_def["parameters"]
        assert "properties" in tool_def["parameters"]
    
    def test_create_langgraph_tool_invalid_model(self, classification_models):
        """Test creating LangGraph tool for invalid model."""
        tool_def = classification_models.create_langgraph_tool("invalid_model")
        
        assert "error" in tool_def
    
    @pytest.mark.parametrize("model_name,expected_metrics", [
        ("logistic_regression", ["accuracy", "precision", "recall", "f1"]),
        ("random_forest_classifier", ["accuracy", "precision", "recall", "f1"]),
        ("svc", ["accuracy", "precision", "recall", "f1"]),
        ("gaussian_nb", ["accuracy", "precision", "recall", "f1"]),
        ("knn_classifier", ["accuracy", "precision", "recall", "f1"]),
        ("mlp_classifier", ["accuracy", "precision", "recall", "f1"]),
        ("lda", ["accuracy", "precision", "recall", "f1"]),
        ("qda", ["accuracy", "precision", "recall", "f1"]),
        ("gaussian_process_classifier", ["accuracy", "precision", "recall", "f1"]),
        ("radius_neighbors_classifier", ["accuracy", "precision", "recall", "f1"])
    ])
    def test_model_metrics_consistency(self, classification_models, model_name, expected_metrics):
        """Test that all classification models have consistent metrics."""
        if model_name in classification_models.model_mapping:
            model_config = classification_models.model_mapping[model_name]
            actual_metrics = model_config["metrics"]
            
            for metric in expected_metrics:
                assert metric in actual_metrics, f"Missing metric {metric} in {model_name}"
    
    def test_all_models_have_required_fields(self, classification_models):
        """Test that all models have required configuration fields."""
        required_fields = ["module", "class", "type", "metrics", "description"]
        
        for model_name, config in classification_models.model_mapping.items():
            for field in required_fields:
                assert field in config, f"Missing field {field} in {model_name}"
            
            assert config["type"] == "classifier", f"Model {model_name} is not a classifier"
    
    def test_model_mapping_consistency(self, classification_models):
        """Test consistency between model mapping and available models."""
        mapping_models = set(classification_models.model_mapping.keys())
        
        # Get all models from available_models
        available_models = set()
        for category in classification_models.available_models.values():
            available_models.update(category.keys())
        
        # All available models should be in mapping
        assert available_models.issubset(mapping_models), "Available models not in mapping"
    
    def test_fit_model_with_different_test_sizes(self, classification_models, sample_binary_data):
        """Test fitting with different test sizes."""
        test_sizes = [0.1, 0.2, 0.3]
        
        for test_size in test_sizes:
            result = classification_models.fit_model(
                "logistic_regression",
                sample_binary_data,
                target_column="target",
                test_size=test_size,
                random_state=42
            )
            
            assert result["success"] is True
            assert "data_shape" in result
            
            # Check that train/test split is approximately correct
            train_shape, test_shape = result["data_shape"]
            total_samples = train_shape[0] + test_shape[0]
            actual_test_ratio = test_shape[0] / total_samples
            
            # Allow some tolerance for rounding
            assert abs(actual_test_ratio - test_size) < 0.1
    
    def test_fit_model_with_different_random_states(self, classification_models, sample_binary_data):
        """Test fitting with different random states produces different results."""
        results = []
        
        for random_state in [42, 123, 456]:
            result = classification_models.fit_model(
                "logistic_regression",
                sample_binary_data,
                target_column="target",
                random_state=random_state
            )
            
            assert result["success"] is True
            results.append(result["metrics"]["accuracy"])
        
        # Results should be different (though not guaranteed)
        # At least check that we get valid results
        for accuracy in results:
            assert 0 <= accuracy <= 1
    
    def test_feature_importance_consistency(self, classification_models, sample_classification_data):
        """Test that models with feature importance return consistent results."""
        models_with_importance = [
            "random_forest_classifier",
            "gradient_boosting_classifier",
            "extra_trees_classifier",
            "ada_boost_classifier"
        ]
        
        for model_name in models_with_importance:
            result = classification_models.fit_model(
                model_name,
                sample_classification_data,
                target_column="target",
                n_estimators=10,
                random_state=42
            )
            
            assert result["success"] is True
            assert "feature_importance" in result
            assert result["feature_importance"] is not None
            
            # Check feature importance structure
            importance = result["feature_importance"]
            assert isinstance(importance, dict)
            assert len(importance) == 4  # 4 features (target is dropped)
            
            # Check that importance values are non-negative
            for value in importance.values():
                assert value >= 0
    
    def test_probability_estimation_models(self, classification_models, sample_binary_data):
        """Test models that support probability estimation."""
        probability_models = [
            "logistic_regression",
            "random_forest_classifier",
            "gaussian_nb",
            "mlp_classifier"
        ]
        
        for model_name in probability_models:
            result = classification_models.fit_model(
                model_name,
                sample_binary_data,
                target_column="target",
                random_state=42
            )
            
            assert result["success"] is True
            # These models should have predict_proba method
            # The base class should handle this automatically
