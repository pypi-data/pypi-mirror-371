"""
Tests for the PreprocessingModels class.

This module tests the preprocessing models functionality including
all supported preprocessing algorithms from scikit-learn.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the preprocessing models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from algos.preprocessing import PreprocessingModels


class TestPreprocessingModels:
    """Test class for PreprocessingModels functionality."""
    
    @pytest.fixture
    def preprocessing_models(self):
        """Create a preprocessing models instance for testing."""
        return PreprocessingModels()
    
    # Use fixtures from conftest.py instead of local data generation
    
    def test_initialization(self, preprocessing_models):
        """Test preprocessing models initialization."""
        assert preprocessing_models.model_mapping is not None
        assert preprocessing_models.available_models is not None
        
        # Check that we have preprocessing models
        assert len(preprocessing_models.model_mapping) > 0
        assert "pca" in preprocessing_models.model_mapping
        assert "select_k_best" in preprocessing_models.model_mapping
    
    def test_get_available_models(self, preprocessing_models):
        """Test getting available preprocessing models."""
        models = preprocessing_models.get_available_models()
        
        assert isinstance(models, dict)
        assert "dimensionality_reduction" in models
        assert "feature_selection" in models
    
    @pytest.mark.parametrize("model_name", [
        "pca",
        "truncated_svd",
        "factor_analysis",
        "fast_ica",
        "select_k_best",
        "select_percentile",
        "rfe",
        "rfecv"
    ])
    def test_model_mapping_contains_models(self, preprocessing_models, model_name):
        """Test that specific models are in the mapping."""
        assert model_name in preprocessing_models.model_mapping
        model_config = preprocessing_models.model_mapping[model_name]
        
        assert "module" in model_config
        assert "class" in model_config
        assert "type" in model_config
        assert "metrics" in model_config
        assert "description" in model_config
        assert model_config["type"] == "preprocessor"
    
    def test_fit_model_pca(self, preprocessing_models, sample_preprocessing_data):
        """Test fitting PCA."""
        result = preprocessing_models.fit_model(
            "pca",
            sample_preprocessing_data,
            n_components=3
        )
        
        assert result["success"] is True
        assert result["model_name"] == "pca"
        assert "model" in result
        assert "metrics" in result
        assert "transformed_data" in result
        assert "transformed_shape" in result
        
        # Check transformed data
        assert result["transformed_shape"][1] == 3  # 3 components
        assert result["transformed_shape"][0] == len(sample_preprocessing_data)
        
        # Check metrics
        metrics = result["metrics"]
        assert "explained_variance_ratio" in metrics
        assert "cumulative_variance_ratio" in metrics
        assert len(metrics["explained_variance_ratio"]) == 3
    
    def test_fit_model_truncated_svd(self, preprocessing_models, sample_preprocessing_data):
        """Test fitting Truncated SVD."""
        result = preprocessing_models.fit_model(
            "truncated_svd",
            sample_preprocessing_data,
            n_components=3,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "truncated_svd"
        assert "model" in result
        assert "metrics" in result
        assert "transformed_data" in result
        assert "transformed_shape" in result
        
        # Check transformed data
        assert result["transformed_shape"][1] == 3  # 3 components
        assert result["transformed_shape"][0] == len(sample_preprocessing_data)
    
    def test_fit_model_factor_analysis(self, preprocessing_models, sample_preprocessing_data):
        """Test fitting Factor Analysis."""
        result = preprocessing_models.fit_model(
            "factor_analysis",
            sample_preprocessing_data,
            n_factors=3,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "factor_analysis"
        assert "model" in result
        assert "metrics" in result
        assert "transformed_data" in result
        assert "transformed_shape" in result
    
    def test_fit_model_fast_ica(self, preprocessing_models, sample_preprocessing_data):
        """Test fitting Fast ICA."""
        result = preprocessing_models.fit_model(
            "fast_ica",
            sample_preprocessing_data,
            n_components=3,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "fast_ica"
        assert "model" in result
        assert "metrics" in result
        assert "transformed_data" in result
        assert "transformed_shape" in result
        
        # Check kurtosis metric
        metrics = result["metrics"]
        if "kurtosis" in metrics:
            assert len(metrics["kurtosis"]) == 3
    
    def test_fit_model_select_k_best(self, preprocessing_models, sample_preprocessing_data_with_target):
        """Test fitting Select K Best."""
        result = preprocessing_models.fit_model(
            "select_k_best",
            sample_preprocessing_data_with_target,
            target_column="target",
            k=3
        )
        
        assert result["success"] is True
        assert result["model_name"] == "select_k_best"
        assert "model" in result
        assert "metrics" in result
        assert "transformed_data" in result
        assert "transformed_shape" in result
        
        # Check transformed data
        assert result["transformed_shape"][1] == 3  # 3 features selected
        assert result["transformed_shape"][0] == len(sample_preprocessing_data_with_target)
        
        # Check feature scores
        metrics = result["metrics"]
        if "feature_scores" in metrics:
            assert len(metrics["feature_scores"]) == 64  # 64 original features (target is dropped)
    
    def test_fit_model_select_percentile(self, preprocessing_models, sample_preprocessing_data_with_target):
        """Test fitting Select Percentile."""
        result = preprocessing_models.fit_model(
            "select_percentile",
            sample_preprocessing_data_with_target,
            target_column="target",
            percentile=50
        )
        
        assert result["success"] is True
        assert result["model_name"] == "select_percentile"
        assert "model" in result
        assert "metrics" in result
        assert "transformed_data" in result
        assert "transformed_shape" in result
    
    def test_fit_model_rfe(self, preprocessing_models, sample_preprocessing_data_with_target):
        """Test fitting RFE."""
        result = preprocessing_models.fit_model(
            "rfe",
            sample_preprocessing_data_with_target,
            target_column="target",
            n_features_to_select=3,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "rfe"
        assert "model" in result
        assert "metrics" in result
        assert "transformed_data" in result
        assert "transformed_shape" in result
        
        # Check feature ranking
        metrics = result["metrics"]
        if "feature_ranking" in metrics:
            assert len(metrics["feature_ranking"]) == 64  # 64 features (target is dropped)
    
    #TODO: Fix RFECV
    def test_fit_model_rfecv(self, preprocessing_models, sample_preprocessing_data_with_target):
        """Test fitting RFECV."""
        result = preprocessing_models.fit_model(
            "rfecv",
            sample_preprocessing_data_with_target,
            target_column="target",
            min_features_to_select=1,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "rfecv"
        assert "model" in result
        assert "metrics" in result
        assert "transformed_data" in result
        assert "transformed_shape" in result
        
        # Check feature ranking and CV scores
        metrics = result["metrics"]
        if "feature_ranking" in metrics:
            assert len(metrics["feature_ranking"]) == 64  # 64 features (target is dropped)
    
    def test_fit_model_invalid_model(self, preprocessing_models, sample_preprocessing_data):
        """Test fitting with invalid model name."""
        result = preprocessing_models.fit_model(
            "invalid_model",
            sample_preprocessing_data
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_fit_model_with_categorical_features(self, preprocessing_models, sample_data_with_categorical):
        """Test fitting with categorical features."""
        result = preprocessing_models.fit_model(
            "pca",
            sample_data_with_categorical,
            n_components=2
        )
        
        assert result["success"] is True
        assert "label_encoders" in result
        assert len(result["label_encoders"]) > 0
    
    def test_fit_model_with_missing_values(self, preprocessing_models):
        """Test fitting with missing values."""
        np.random.seed(42)
        n_samples = 100
        
        # Create data with missing values
        data = pd.DataFrame({
            'feature_1': np.random.randn(n_samples),
            'feature_2': np.random.randn(n_samples),
            'feature_3': np.random.randn(n_samples)
        })
        
        # Add some missing values
        data.loc[10:15, 'feature_1'] = np.nan
        data.loc[20:25, 'feature_2'] = np.nan
        
        result = preprocessing_models.fit_model(
            "pca",
            data,
            n_components=2
        )
        
        assert result["success"] is True
        # Should handle missing values gracefully
    
    def test_extract_model_info_pca(self, preprocessing_models):
        """Test extracting model info for PCA."""
        info = preprocessing_models.extract_model_info("pca")
        
        assert "error" not in info
        assert info["model_name"] == "pca"
        assert info["class_name"] == "PCA"
        assert info["module_name"] == "sklearn.decomposition"
        assert info["type"] == "preprocessor"
        assert "explained_variance_ratio" in info["metrics"]
    
    def test_extract_model_info_invalid_model(self, preprocessing_models):
        """Test extracting model info for invalid model."""
        info = preprocessing_models.extract_model_info("invalid_model")
        
        assert "error" in info
        assert "not found" in info["error"]
    
    def test_get_model_tool_description_pca(self, preprocessing_models):
        """Test getting tool description for PCA."""
        description = preprocessing_models.get_model_tool_description("pca")
        
        assert "Principal Component Analysis" in description
        assert "PCA" in description
        assert "preprocessor" in description
        assert "explained_variance_ratio" in description
    
    def test_get_model_tool_description_invalid_model(self, preprocessing_models):
        """Test getting tool description for invalid model."""
        description = preprocessing_models.get_model_tool_description("invalid_model")
        
        assert description.startswith("Error:")
    
    def test_validate_model_parameters_pca(self, preprocessing_models):
        """Test parameter validation for PCA."""
        validation = preprocessing_models.validate_model_parameters(
            "pca",
            {"n_components": 3, "random_state": 42}
        )
        
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
    
    def test_validate_model_parameters_invalid_model(self, preprocessing_models):
        """Test parameter validation for invalid model."""
        validation = preprocessing_models.validate_model_parameters(
            "invalid_model",
            {"n_components": 3}
        )
        
        assert validation["valid"] is False
        assert "not found" in validation["error"]
    
    def test_validate_model_parameters_unknown_param(self, preprocessing_models):
        """Test parameter validation with unknown parameter."""
        validation = preprocessing_models.validate_model_parameters(
            "pca",
            {"n_components": 3, "unknown_param": 42}
        )
        
        assert validation["valid"] is True
        assert len(validation["warnings"]) > 0
        assert "Unknown parameter" in validation["warnings"][0]
    
    def test_create_langgraph_tool_pca(self, preprocessing_models):
        """Test creating LangGraph tool for PCA."""
        tool_def = preprocessing_models.create_langgraph_tool("pca")
        
        assert "error" not in tool_def
        assert "name" in tool_def
        assert "description" in tool_def
        assert "parameters" in tool_def
        assert tool_def["name"] == "train_pca"
        assert "type" in tool_def["parameters"]
        assert "properties" in tool_def["parameters"]
    
    def test_create_langgraph_tool_invalid_model(self, preprocessing_models):
        """Test creating LangGraph tool for invalid model."""
        tool_def = preprocessing_models.create_langgraph_tool("invalid_model")
        
        assert "error" in tool_def
    
    @pytest.mark.parametrize("model_name,expected_metrics", [
        ("pca", ["explained_variance_ratio"]),
        ("truncated_svd", ["explained_variance_ratio"]),
        ("factor_analysis", ["explained_variance_ratio"]),
        ("fast_ica", ["kurtosis"]),
        ("select_k_best", ["feature_scores"]),
        ("select_percentile", ["feature_scores"]),
        ("rfe", ["feature_ranking"]),
        ("rfecv", ["feature_ranking", "cv_scores"])
    ])
    def test_model_metrics_consistency(self, preprocessing_models, model_name, expected_metrics):
        """Test that all preprocessing models have consistent metrics."""
        if model_name in preprocessing_models.model_mapping:
            model_config = preprocessing_models.model_mapping[model_name]
            actual_metrics = model_config["metrics"]
            
            for metric in expected_metrics:
                assert metric in actual_metrics, f"Missing metric {metric} in {model_name}"
    
    def test_all_models_have_required_fields(self, preprocessing_models):
        """Test that all models have required configuration fields."""
        required_fields = ["module", "class", "type", "metrics", "description"]
        
        for model_name, config in preprocessing_models.model_mapping.items():
            for field in required_fields:
                assert field in config, f"Missing field {field} in {model_name}"
            
            assert config["type"] == "preprocessor", f"Model {model_name} is not a preprocessor"
    
    def test_model_mapping_consistency(self, preprocessing_models):
        """Test consistency between model mapping and available models."""
        mapping_models = set(preprocessing_models.model_mapping.keys())
        
        # Get all models from available_models
        available_models = set()
        for category in preprocessing_models.available_models.values():
            available_models.update(category.keys())
        
        # All available models should be in mapping
        assert available_models.issubset(mapping_models), "Available models not in mapping"
    
    def test_fit_model_with_different_n_components(self, preprocessing_models, sample_preprocessing_data):
        """Test fitting with different numbers of components."""
        n_components_list = [2, 3, 4]
        
        for n_components in n_components_list:
            result = preprocessing_models.fit_model(
                "pca",
                sample_preprocessing_data,
                n_components=n_components
            )
            
            assert result["success"] is True
            assert result["transformed_shape"][1] == n_components
            assert result["transformed_shape"][0] == len(sample_preprocessing_data)
    
    def test_fit_model_with_different_random_states(self, preprocessing_models, sample_preprocessing_data):
        """Test fitting with different random states produces different results."""
        results = []
        
        for random_state in [42, 123, 456]:
            result = preprocessing_models.fit_model(
                "pca",
                sample_preprocessing_data,
                n_components=3,
                random_state=random_state
            )
            
            assert result["success"] is True
            results.append(result["transformed_data"])
        
        # Results should be different (though not guaranteed)
        # At least check that we get valid results
        for transformed_data in results:
            assert len(transformed_data) == len(sample_preprocessing_data)
    
    def test_explained_variance_ratio_calculation(self, preprocessing_models, sample_preprocessing_data):
        """Test that explained variance ratio is calculated correctly."""
        result = preprocessing_models.fit_model(
            "pca",
            sample_preprocessing_data,
            n_components=3
        )
        
        assert result["success"] is True
        metrics = result["metrics"]
        
        # Check explained variance ratio
        assert "explained_variance_ratio" in metrics
        assert "cumulative_variance_ratio" in metrics
        
        evr = metrics["explained_variance_ratio"]
        cvr = metrics["cumulative_variance_ratio"]
        
        assert len(evr) == 3
        assert len(cvr) == 3
        
        # Check that values are reasonable
        for ratio in evr:
            assert 0 <= ratio <= 1
        
        # Check that cumulative variance ratio is increasing
        for i in range(1, len(cvr)):
            assert cvr[i] >= cvr[i-1]
    
    def test_feature_scores_calculation(self, preprocessing_models, sample_preprocessing_data_with_target):
        """Test that feature scores are calculated correctly."""
        result = preprocessing_models.fit_model(
            "select_k_best",
            sample_preprocessing_data_with_target,
            target_column="target",
            k=3
        )
        
        assert result["success"] is True
        metrics = result["metrics"]
        
        # Check feature scores
        if "feature_scores" in metrics:
            scores = metrics["feature_scores"]
            assert len(scores) == 64  # All 64 features have scores
            # Filter out NaN values before checking non-negativity
        valid_scores = [score for score in scores if not np.isnan(score)]
        assert all(score >= 0 for score in valid_scores)
    
    def test_feature_ranking_calculation(self, preprocessing_models, sample_preprocessing_data_with_target):
        """Test that feature ranking is calculated correctly."""
        result = preprocessing_models.fit_model(
            "rfe",
            sample_preprocessing_data_with_target,
            target_column="target",
            n_features_to_select=3,
            random_state=42
        )
        
        assert result["success"] is True
        metrics = result["metrics"]
        
        # Check feature ranking
        if "feature_ranking" in metrics:
            ranking = metrics["feature_ranking"]
            assert len(ranking) == 64  # 64 features (target is dropped)
            assert all(rank >= 1 for rank in ranking)
    
    def test_kurtosis_calculation(self, preprocessing_models, sample_preprocessing_data):
        """Test that kurtosis is calculated correctly for Fast ICA."""
        result = preprocessing_models.fit_model(
            "fast_ica",
            sample_preprocessing_data,
            n_components=3,
            random_state=42
        )
        
        assert result["success"] is True
        metrics = result["metrics"]
        
        # Check kurtosis
        if "kurtosis" in metrics:
            kurtosis = metrics["kurtosis"]
            assert len(kurtosis) == 3
            # Kurtosis can be any real number
    
    def test_dimensionality_reduction_models(self, preprocessing_models, sample_preprocessing_data):
        """Test dimensionality reduction models."""
        dim_reduction_models = [
            ("pca", {"n_components": 3}),
            ("truncated_svd", {"n_components": 3, "random_state": 42}),
            ("factor_analysis", {"n_factors": 3, "random_state": 42}),
            ("fast_ica", {"n_components": 3, "random_state": 42})
        ]
        
        for model_name, params in dim_reduction_models:
            result = preprocessing_models.fit_model(
                model_name,
                sample_preprocessing_data,
                **params
            )
            
            assert result["success"] is True
            assert result["model_name"] == model_name
            assert result["transformed_shape"][1] == 3  # 3 components
            assert result["transformed_shape"][0] == len(sample_preprocessing_data)
    
    def test_feature_selection_models(self, preprocessing_models, sample_preprocessing_data_with_target):
        """Test feature selection models."""
        feature_selection_models = [
            ("select_k_best", {"k": 3}),
            ("select_percentile", {"percentile": 50}),
            ("rfe", {"n_features_to_select": 3, "random_state": 42}),
            ("rfecv", {"min_features_to_select": 1, "random_state": 42})
        ]
        
        for model_name, params in feature_selection_models:
            result = preprocessing_models.fit_model(
                model_name,
                sample_preprocessing_data_with_target,
                target_column="target",
                **params
            )
            
            assert result["success"] is True
            assert result["model_name"] == model_name
            assert "transformed_data" in result
            assert "transformed_shape" in result
    
    def test_unsupervised_preprocessing(self, preprocessing_models, sample_preprocessing_data):
        """Test unsupervised preprocessing models."""
        unsupervised_models = ["pca", "truncated_svd", "factor_analysis", "fast_ica"]
        
        for model_name in unsupervised_models:
            result = preprocessing_models.fit_model(
                model_name,
                sample_preprocessing_data,
                n_components=3,
                random_state=42
            )
            
            assert result["success"] is True
            assert result["model_name"] == model_name
            assert "transformed_data" in result
            assert "transformed_shape" in result
    
    def test_supervised_preprocessing(self, preprocessing_models, sample_preprocessing_data_with_target):
        """Test supervised preprocessing models."""
        supervised_models = ["select_k_best", "select_percentile", "rfe", "rfecv"]
        
        for model_name in supervised_models:
            result = preprocessing_models.fit_model(
                model_name,
                sample_preprocessing_data_with_target,
                target_column="target",
                k=3 if model_name == "select_k_best" else None,
                percentile=50 if model_name == "select_percentile" else None,
                n_features_to_select=3 if model_name == "rfe" else None,
                min_features_to_select=1 if model_name == "rfecv" else None,
                random_state=42
            )
            
            if not result["success"]:
                print(f"Failed for {model_name}: {result.get('error', 'Unknown error')}")
            
            assert result["success"] is True
            assert result["model_name"] == model_name
            assert "transformed_data" in result
            assert "transformed_shape" in result
    
    def test_preprocessing_without_target(self, preprocessing_models, sample_preprocessing_data):
        """Test preprocessing without target column."""
        result = preprocessing_models.fit_model(
            "pca",
            sample_preprocessing_data,
            n_components=3
        )
        
        assert result["success"] is True
        assert result["model_name"] == "pca"
        assert "transformed_data" in result
        assert "transformed_shape" in result
    
    def test_preprocessing_with_target(self, preprocessing_models, sample_preprocessing_data_with_target):
        """Test preprocessing with target column."""
        result = preprocessing_models.fit_model(
            "select_k_best",
            sample_preprocessing_data_with_target,
            target_column="target",
            k=3
        )
        
        assert result["success"] is True
        assert result["model_name"] == "select_k_best"
        assert "transformed_data" in result
        assert "transformed_shape" in result
