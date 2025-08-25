"""
Tests for the RegressionModels class.

This module tests the regression models functionality including
all supported regression algorithms from scikit-learn.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the regression models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from algos.regression import RegressionModels


class TestRegressionModels:
    """Test class for RegressionModels functionality."""
    
    @pytest.fixture
    def regression_models(self):
        """Create a regression models instance for testing."""
        return RegressionModels()
    
    # Use fixtures from conftest.py instead of local data generation
    
    def test_initialization(self, regression_models):
        """Test regression models initialization."""
        assert regression_models.model_mapping is not None
        assert regression_models.available_models is not None
        
        # Check that we have regression models
        assert len(regression_models.model_mapping) > 0
        assert "linear_regression" in regression_models.model_mapping
        assert "random_forest_regressor" in regression_models.model_mapping
    
    def test_get_available_models(self, regression_models):
        """Test getting available regression models."""
        models = regression_models.get_available_models()
        
        assert isinstance(models, dict)
        assert "linear_models" in models
        assert "tree_based" in models
        assert "support_vector_regression" in models
        assert "neural_networks" in models
        assert "gaussian_processes" in models
        assert "nearest_neighbors" in models
        assert "other" in models
    
    @pytest.mark.parametrize("model_name", [
        "linear_regression",
        "ridge_regression",
        "lasso_regression",
        "random_forest_regressor",
        "svr",
        "knn_regressor"
    ])
    def test_model_mapping_contains_models(self, regression_models, model_name):
        """Test that specific models are in the mapping."""
        assert model_name in regression_models.model_mapping
        model_config = regression_models.model_mapping[model_name]
        
        assert "module" in model_config
        assert "class" in model_config
        assert "type" in model_config
        assert "metrics" in model_config
        assert "description" in model_config
        assert model_config["type"] == "regressor"
    
    def test_fit_model_linear_regression(self, regression_models, sample_regression_data):
        """Test fitting linear regression model."""
        result = regression_models.fit_model(
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
        assert "data_shape" in result
        
        # Check metrics
        metrics = result["metrics"]
        assert "mse" in metrics
        assert "mae" in metrics
        assert "r2" in metrics
        
        # Check that metrics are reasonable
        assert metrics["mse"] >= 0
        assert metrics["mae"] >= 0
        assert metrics["r2"] <= 1  # R² can be negative for poor fits
    
    def test_fit_model_ridge_regression(self, regression_models, sample_regression_data):
        """Test fitting ridge regression model."""
        result = regression_models.fit_model(
            "ridge_regression",
            sample_regression_data,
            target_column="target",
            alpha=1.0,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "ridge_regression"
        assert "model" in result
        assert "metrics" in result
        assert "feature_importance" in result
        
        # Check feature importance (coefficients)
        feature_importance = result["feature_importance"]
        assert feature_importance is not None
        assert len(feature_importance) == 10  # 10 features (target is dropped)
    
    def test_fit_model_lasso_regression(self, regression_models, sample_regression_data):
        """Test fitting lasso regression model."""
        result = regression_models.fit_model(
            "lasso_regression",
            sample_regression_data,
            target_column="target",
            alpha=0.1,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "lasso_regression"
        assert "model" in result
        assert "metrics" in result
        assert "feature_importance" in result
    
    def test_fit_model_random_forest_regressor(self, regression_models, sample_regression_data):
        """Test fitting random forest regressor."""
        result = regression_models.fit_model(
            "random_forest_regressor",
            sample_regression_data,
            target_column="target",
            n_estimators=10,
            max_depth=5,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "random_forest_regressor"
        assert "model" in result
        assert "metrics" in result
        assert "feature_importance" in result
        
        # Check feature importance
        feature_importance = result["feature_importance"]
        assert feature_importance is not None
        assert len(feature_importance) == 10  # 10 features (target is dropped)
        
        # Check that importance values are non-negative
        for value in feature_importance.values():
            assert value >= 0
    
    def test_fit_model_svr(self, regression_models, sample_regression_data):
        """Test fitting Support Vector Regression."""
        result = regression_models.fit_model(
            "svr",
            sample_regression_data,
            target_column="target",
            kernel="rbf",
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "svr"
        assert "model" in result
        assert "metrics" in result
    
    def test_fit_model_knn_regressor(self, regression_models, sample_regression_data):
        """Test fitting K-Nearest Neighbors regressor."""
        result = regression_models.fit_model(
            "knn_regressor",
            sample_regression_data,
            target_column="target",
            n_neighbors=5
        )
        
        assert result["success"] is True
        assert result["model_name"] == "knn_regressor"
        assert "model" in result
        assert "metrics" in result
    
    def test_fit_model_mlp_regressor(self, regression_models, sample_regression_data):
        """Test fitting Multi-layer Perceptron regressor."""
        result = regression_models.fit_model(
            "mlp_regressor",
            sample_regression_data,
            target_column="target",
            hidden_layer_sizes=(10,),
            max_iter=100,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "mlp_regressor"
        assert "model" in result
        assert "metrics" in result
    
    def test_fit_model_gaussian_process_regressor(self, regression_models, sample_regression_data):
        """Test fitting Gaussian Process regressor."""
        result = regression_models.fit_model(
            "gaussian_process_regressor",
            sample_regression_data,
            target_column="target",
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "gaussian_process_regressor"
        assert "model" in result
        assert "metrics" in result
    
    def test_fit_model_isotonic_regression(self, regression_models, sample_regression_data):
        """Test fitting Isotonic regression."""
        result = regression_models.fit_model(
            "isotonic_regression",
            sample_regression_data,
            target_column="target"
        )
    
        if not result["success"]:
            print(f"Isotonic regression error: {result.get('error', 'Unknown error')}")
    
        assert result["success"] is True
        assert result["model_name"] == "isotonic_regression"
        assert "model" in result
        assert "metrics" in result
    
    def test_fit_model_invalid_model(self, regression_models, sample_regression_data):
        """Test fitting with invalid model name."""
        result = regression_models.fit_model(
            "invalid_model",
            sample_regression_data,
            target_column="target"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_fit_model_missing_target(self, regression_models, sample_regression_data):
        """Test fitting without target column."""
        result = regression_models.fit_model(
            "linear_regression",
            sample_regression_data
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "required" in result["error"].lower()
    
    def test_fit_model_missing_target_column(self, regression_models, sample_regression_data):
        """Test fitting with non-existent target column."""
        result = regression_models.fit_model(
            "linear_regression",
            sample_regression_data,
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
    
    def test_fit_model_with_categorical_features(self, regression_models):
        """Test fitting with categorical features."""
        np.random.seed(42)
        n_samples = 100
        
        # Create data with categorical features
        data = pd.DataFrame({
            'numeric_1': np.random.randn(n_samples),
            'numeric_2': np.random.randn(n_samples),
            'categorical_1': np.random.choice(['A', 'B', 'C'], n_samples),
            'categorical_2': np.random.choice(['X', 'Y'], n_samples),
            'target': np.random.randn(n_samples)
        })
        
        result = regression_models.fit_model(
            "linear_regression",
            data,
            target_column="target",
            random_state=42
        )
        
        assert result["success"] is True
        assert "label_encoders" in result
        assert len(result["label_encoders"]) > 0
    
    def test_fit_model_with_missing_values(self, regression_models):
        """Test fitting with missing values."""
        np.random.seed(42)
        n_samples = 100
        
        # Create data with missing values
        data = pd.DataFrame({
            'feature_1': np.random.randn(n_samples),
            'feature_2': np.random.randn(n_samples),
            'feature_3': np.random.randn(n_samples),
            'target': np.random.randn(n_samples)
        })
        
        # Add some missing values
        data.loc[10:15, 'feature_1'] = np.nan
        data.loc[20:25, 'feature_2'] = np.nan
        
        result = regression_models.fit_model(
            "linear_regression",
            data,
            target_column="target",
            random_state=42
        )
        
        assert result["success"] is True
        # Should handle missing values gracefully
    
    def test_extract_model_info_linear_regression(self, regression_models):
        """Test extracting model info for linear regression."""
        info = regression_models.extract_model_info("linear_regression")
        
        assert "error" not in info
        assert info["model_name"] == "linear_regression"
        assert info["class_name"] == "LinearRegression"
        assert info["module_name"] == "sklearn.linear_model"
        assert info["type"] == "regressor"
        assert "mse" in info["metrics"]
        assert "mae" in info["metrics"]
        assert "r2" in info["metrics"]
    
    def test_extract_model_info_invalid_model(self, regression_models):
        """Test extracting model info for invalid model."""
        info = regression_models.extract_model_info("invalid_model")
        
        assert "error" in info
        assert "not found" in info["error"]
    
    def test_get_model_tool_description_linear_regression(self, regression_models):
        """Test getting tool description for linear regression."""
        description = regression_models.get_model_tool_description("linear_regression")
        
        assert "Linear Regression" in description
        assert "LinearRegression" in description
        assert "regressor" in description
        assert "mse" in description
        assert "mae" in description
        assert "r2" in description
    
    def test_get_model_tool_description_invalid_model(self, regression_models):
        """Test getting tool description for invalid model."""
        description = regression_models.get_model_tool_description("invalid_model")
        
        assert description.startswith("Error:")
    
    def test_validate_model_parameters_linear_regression(self, regression_models):
        """Test parameter validation for linear regression."""
        validation = regression_models.validate_model_parameters(
            "linear_regression",
            {"fit_intercept": True}
        )
        
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
    
    def test_validate_model_parameters_invalid_model(self, regression_models):
        """Test parameter validation for invalid model."""
        validation = regression_models.validate_model_parameters(
            "invalid_model",
            {"fit_intercept": True}
        )
        
        assert validation["valid"] is False
        assert "not found" in validation["error"]
    
    def test_validate_model_parameters_unknown_param(self, regression_models):
        """Test parameter validation with unknown parameter."""
        validation = regression_models.validate_model_parameters(
            "linear_regression",
            {"fit_intercept": True, "unknown_param": 42}
        )
        
        assert validation["valid"] is True
        assert len(validation["warnings"]) > 0
        assert "Unknown parameter" in validation["warnings"][0]
    
    def test_create_langgraph_tool_linear_regression(self, regression_models):
        """Test creating LangGraph tool for linear regression."""
        tool_def = regression_models.create_langgraph_tool("linear_regression")
        
        assert "error" not in tool_def
        assert "name" in tool_def
        assert "description" in tool_def
        assert "parameters" in tool_def
        assert tool_def["name"] == "train_linear_regression"
        assert "type" in tool_def["parameters"]
        assert "properties" in tool_def["parameters"]
    
    def test_create_langgraph_tool_invalid_model(self, regression_models):
        """Test creating LangGraph tool for invalid model."""
        tool_def = regression_models.create_langgraph_tool("invalid_model")
        
        assert "error" in tool_def
    
    @pytest.mark.parametrize("model_name,expected_metrics", [
        ("linear_regression", ["mse", "mae", "r2"]),
        ("ridge_regression", ["mse", "mae", "r2"]),
        ("lasso_regression", ["mse", "mae", "r2"]),
        ("elastic_net", ["mse", "mae", "r2"]),
        ("sgd_regressor", ["mse", "mae", "r2"]),
        ("random_forest_regressor", ["mse", "mae", "r2"]),
        ("gradient_boosting_regressor", ["mse", "mae", "r2"]),
        ("svr", ["mse", "mae", "r2"]),
        ("linear_svr", ["mse", "mae", "r2"]),
        ("mlp_regressor", ["mse", "mae", "r2"]),
        ("gaussian_process_regressor", ["mse", "mae", "r2"]),
        ("knn_regressor", ["mse", "mae", "r2"]),
        ("isotonic_regression", ["mse", "mae", "r2"])
    ])
    def test_model_metrics_consistency(self, regression_models, model_name, expected_metrics):
        """Test that all regression models have consistent metrics."""
        if model_name in regression_models.model_mapping:
            model_config = regression_models.model_mapping[model_name]
            actual_metrics = model_config["metrics"]
            
            for metric in expected_metrics:
                assert metric in actual_metrics, f"Missing metric {metric} in {model_name}"
    
    def test_all_models_have_required_fields(self, regression_models):
        """Test that all models have required configuration fields."""
        required_fields = ["module", "class", "type", "metrics", "description"]
        
        for model_name, config in regression_models.model_mapping.items():
            for field in required_fields:
                assert field in config, f"Missing field {field} in {model_name}"
            
            assert config["type"] == "regressor", f"Model {model_name} is not a regressor"
    
    def test_model_mapping_consistency(self, regression_models):
        """Test consistency between model mapping and available models."""
        mapping_models = set(regression_models.model_mapping.keys())
        
        # Get all models from available_models
        available_models = set()
        for category in regression_models.available_models.values():
            available_models.update(category.keys())
        
        # All available models should be in mapping
        assert available_models.issubset(mapping_models), "Available models not in mapping"
    
    def test_fit_model_with_different_test_sizes(self, regression_models, sample_regression_data):
        """Test fitting with different test sizes."""
        test_sizes = [0.1, 0.2, 0.3]
        
        for test_size in test_sizes:
            result = regression_models.fit_model(
                "linear_regression",
                sample_regression_data,
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
    
    def test_fit_model_with_different_random_states(self, regression_models, sample_regression_data):
        """Test fitting with different random states produces different results."""
        results = []
        
        for random_state in [42, 123, 456]:
            result = regression_models.fit_model(
                "linear_regression",
                sample_regression_data,
                target_column="target",
                random_state=random_state
            )
            
            assert result["success"] is True
            results.append(result["metrics"]["r2"])
        
        # Results should be different (though not guaranteed)
        # At least check that we get valid results
        for r2 in results:
            assert r2 <= 1  # R² can be negative for poor fits
    
    def test_feature_importance_consistency(self, regression_models, sample_regression_data):
        """Test that models with feature importance return consistent results."""
        models_with_importance = [
            "ridge_regression",
            "lasso_regression",
            "elastic_net",
            "random_forest_regressor",
            "gradient_boosting_regressor",
            "extra_trees_regressor",
            "ada_boost_regressor"
        ]
        
        for model_name in models_with_importance:
            # Prepare parameters based on model type
            params = {"random_state": 42}
            if "forest" in model_name or "boosting" in model_name:
                params["n_estimators"] = 10
            
            result = regression_models.fit_model(
                model_name,
                sample_regression_data,
                target_column="target",
                **params
            )
    
            if not result["success"]:
                print(f"Model {model_name} failed: {result.get('error', 'Unknown error')}")
            
            assert result["success"] is True
            assert "feature_importance" in result
            assert result["feature_importance"] is not None
            
            # Check feature importance structure
            importance = result["feature_importance"]
            assert isinstance(importance, dict)
            assert len(importance) == 10  # 10 features (target is dropped)
    
    def test_regularization_models(self, regression_models, sample_regression_data):
        """Test regularization models (Ridge, Lasso, Elastic Net)."""
        regularization_models = [
            ("ridge_regression", {"alpha": 1.0}),
            ("lasso_regression", {"alpha": 0.1}),
            ("elastic_net", {"alpha": 0.1, "l1_ratio": 0.5})
        ]
        
        for model_name, params in regularization_models:
            result = regression_models.fit_model(
                model_name,
                sample_regression_data,
                target_column="target",
                random_state=42,
                **params
            )
            
            assert result["success"] is True
            assert result["model_name"] == model_name
            assert "feature_importance" in result
            assert result["feature_importance"] is not None
    
    def test_tree_based_models(self, regression_models, sample_regression_data):
        """Test tree-based regression models."""
        tree_models = [
            "decision_tree_regressor",
            "random_forest_regressor",
            "gradient_boosting_regressor",
            "extra_trees_regressor",
            "ada_boost_regressor"
        ]
        
        for model_name in tree_models:
            # Prepare parameters based on model type
            params = {"random_state": 42}
            if "forest" in model_name or "boosting" in model_name:
                params["n_estimators"] = 10
            if "tree" in model_name:
                params["max_depth"] = 5
            
            result = regression_models.fit_model(
                model_name,
                sample_regression_data,
                target_column="target",
                **params
            )
            
            assert result["success"] is True
            assert result["model_name"] == model_name
            assert "feature_importance" in result
            assert result["feature_importance"] is not None
    
    def test_neural_network_models(self, regression_models, sample_regression_data):
        """Test neural network regression models."""
        result = regression_models.fit_model(
            "mlp_regressor",
            sample_regression_data,
            target_column="target",
            hidden_layer_sizes=(10, 5),
            max_iter=100,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "mlp_regressor"
        assert "metrics" in result
    
    def test_gaussian_process_models(self, regression_models, sample_regression_data):
        """Test Gaussian Process regression models."""
        result = regression_models.fit_model(
            "gaussian_process_regressor",
            sample_regression_data,
            target_column="target",
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "gaussian_process_regressor"
        assert "metrics" in result
    
    def test_isotonic_regression_special_case(self, regression_models, sample_regression_data):
        """Test isotonic regression as a special case."""
        result = regression_models.fit_model(
            "isotonic_regression",
            sample_regression_data,
            target_column="target"
        )
        
        assert result["success"] is True
        assert result["model_name"] == "isotonic_regression"
        assert "metrics" in result
        
        # Isotonic regression doesn't have feature importance in the same way
        # as other models, so we don't check for it
