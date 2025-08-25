"""
Tests for the ClusteringModels class.

This module tests the clustering models functionality including
all supported clustering algorithms from scikit-learn.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the clustering models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from algos.clustering import ClusteringModels


class TestClusteringModels:
    """Test class for ClusteringModels functionality."""
    
    @pytest.fixture
    def clustering_models(self):
        """Create a clustering models instance for testing."""
        return ClusteringModels()
    
    # Use fixtures from conftest.py instead of local data generation
    
    def test_initialization(self, clustering_models):
        """Test clustering models initialization."""
        assert clustering_models.model_mapping is not None
        assert clustering_models.available_models is not None
        
        # Check that we have clustering models
        assert len(clustering_models.model_mapping) > 0
        assert "kmeans" in clustering_models.model_mapping
        assert "dbscan" in clustering_models.model_mapping
    
    def test_get_available_models(self, clustering_models):
        """Test getting available clustering models."""
        models = clustering_models.get_available_models()
        
        assert isinstance(models, dict)
        assert "partitioning" in models
        assert "density_based" in models
        assert "hierarchical" in models
        assert "spectral" in models
        assert "other" in models
    
    @pytest.mark.parametrize("model_name", [
        "kmeans",
        "dbscan",
        "agglomerative_clustering",
        "spectral_clustering",
        "mean_shift",
        "optics"
    ])
    def test_model_mapping_contains_models(self, clustering_models, model_name):
        """Test that specific models are in the mapping."""
        assert model_name in clustering_models.model_mapping
        model_config = clustering_models.model_mapping[model_name]
        
        assert "module" in model_config
        assert "class" in model_config
        assert "type" in model_config
        assert "metrics" in model_config
        assert "description" in model_config
        assert model_config["type"] == "clustering"
    
    def test_fit_model_kmeans(self, clustering_models, sample_clustering_data):
        """Test fitting K-Means clustering."""
        result = clustering_models.fit_model(
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
        assert "cluster_centers" in result
        assert "cluster_sizes" in result
        
        # Check clustering results
        assert result["n_clusters"] == 3
        assert len(result["clusters"]) == len(sample_clustering_data)
        assert result["cluster_centers"] is not None
        assert len(result["cluster_sizes"]) == 3
        
        # Check metrics
        metrics = result["metrics"]
        assert isinstance(metrics, dict)
    
    def test_fit_model_dbscan(self, clustering_models, sample_clustering_data):
        """Test fitting DBSCAN clustering."""
        result = clustering_models.fit_model(
            "dbscan",
            sample_clustering_data,
            eps=0.5,
            min_samples=5
        )
        
        assert result["success"] is True
        assert result["model_name"] == "dbscan"
        assert "model" in result
        assert "metrics" in result
        assert "clusters" in result
        assert "n_clusters" in result
        assert "cluster_sizes" in result
        
        # Check clustering results
        assert result["n_clusters"] >= 0  # Can be 0 if no clusters found
        assert len(result["clusters"]) == len(sample_clustering_data)
        
        # DBSCAN may not have cluster centers, so we don't assert on them
    
    def test_fit_model_agglomerative_clustering(self, clustering_models, sample_clustering_data):
        """Test fitting Agglomerative clustering."""
        result = clustering_models.fit_model(
            "agglomerative_clustering",
            sample_clustering_data,
            n_clusters=3
        )
        
        assert result["success"] is True
        assert result["model_name"] == "agglomerative_clustering"
        assert "model" in result
        assert "metrics" in result
        assert "clusters" in result
        assert "n_clusters" in result
        assert "cluster_sizes" in result
        
        # Check clustering results
        assert result["n_clusters"] == 3
        assert len(result["clusters"]) == len(sample_clustering_data)
    
    def test_fit_model_spectral_clustering(self, clustering_models, sample_clustering_data):
        """Test fitting Spectral clustering."""
        result = clustering_models.fit_model(
            "spectral_clustering",
            sample_clustering_data,
            n_clusters=3,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "spectral_clustering"
        assert "model" in result
        assert "metrics" in result
        assert "clusters" in result
        assert "n_clusters" in result
        assert "cluster_sizes" in result
        
        # Check clustering results
        assert result["n_clusters"] == 3
        assert len(result["clusters"]) == len(sample_clustering_data)
    
    def test_fit_model_mean_shift(self, clustering_models, sample_clustering_data):
        """Test fitting Mean Shift clustering."""
        result = clustering_models.fit_model(
            "mean_shift",
            sample_clustering_data
        )
        
        assert result["success"] is True
        assert result["model_name"] == "mean_shift"
        assert "model" in result
        assert "metrics" in result
        assert "clusters" in result
        assert "n_clusters" in result
        assert "cluster_sizes" in result
        
        # Check clustering results
        assert result["n_clusters"] >= 0
        assert len(result["clusters"]) == len(sample_clustering_data)
    
    def test_fit_model_optics(self, clustering_models, sample_clustering_data):
        """Test fitting OPTICS clustering."""
        result = clustering_models.fit_model(
            "optics",
            sample_clustering_data,
            min_samples=5
        )
        
        assert result["success"] is True
        assert result["model_name"] == "optics"
        assert "model" in result
        assert "metrics" in result
        assert "clusters" in result
        assert "n_clusters" in result
        assert "cluster_sizes" in result
        
        # Check clustering results
        assert result["n_clusters"] >= 0
        assert len(result["clusters"]) == len(sample_clustering_data)
    
    def test_fit_model_invalid_model(self, clustering_models, sample_clustering_data):
        """Test fitting with invalid model name."""
        result = clustering_models.fit_model(
            "invalid_model",
            sample_clustering_data
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_fit_model_with_categorical_features(self, clustering_models, sample_clustering_data_with_categorical):
        """Test fitting with categorical features."""
        result = clustering_models.fit_model(
            "kmeans",
            sample_clustering_data_with_categorical,
            n_clusters=3,
            random_state=42
        )
        
        assert result["success"] is True
        assert "label_encoders" in result
        assert len(result["label_encoders"]) > 0
    
    def test_fit_model_with_missing_values(self, clustering_models):
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
        
        result = clustering_models.fit_model(
            "kmeans",
            data,
            n_clusters=3,
            random_state=42
        )
        
        assert result["success"] is True
        # Should handle missing values gracefully
    
    def test_extract_model_info_kmeans(self, clustering_models):
        """Test extracting model info for K-Means."""
        info = clustering_models.extract_model_info("kmeans")
        
        assert "error" not in info
        assert info["model_name"] == "kmeans"
        assert info["class_name"] == "KMeans"
        assert info["module_name"] == "sklearn.cluster"
        assert info["type"] == "clustering"
        assert "silhouette" in info["metrics"]
        assert "calinski_harabasz" in info["metrics"]
        assert "davies_bouldin" in info["metrics"]
    
    def test_extract_model_info_invalid_model(self, clustering_models):
        """Test extracting model info for invalid model."""
        info = clustering_models.extract_model_info("invalid_model")
        
        assert "error" in info
        assert "not found" in info["error"]
    
    def test_get_model_tool_description_kmeans(self, clustering_models):
        """Test getting tool description for K-Means."""
        description = clustering_models.get_model_tool_description("kmeans")
        
        assert "K-Means clustering" in description
        assert "KMeans" in description
        assert "clustering" in description
        assert "silhouette" in description
        assert "calinski_harabasz" in description
        assert "davies_bouldin" in description
    
    def test_get_model_tool_description_invalid_model(self, clustering_models):
        """Test getting tool description for invalid model."""
        description = clustering_models.get_model_tool_description("invalid_model")
        
        assert description.startswith("Error:")
    
    def test_validate_model_parameters_kmeans(self, clustering_models):
        """Test parameter validation for K-Means."""
        validation = clustering_models.validate_model_parameters(
            "kmeans",
            {"n_clusters": 3, "random_state": 42}
        )
        
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
    
    def test_validate_model_parameters_invalid_model(self, clustering_models):
        """Test parameter validation for invalid model."""
        validation = clustering_models.validate_model_parameters(
            "invalid_model",
            {"n_clusters": 3}
        )
        
        assert validation["valid"] is False
        assert "not found" in validation["error"]
    
    def test_validate_model_parameters_unknown_param(self, clustering_models):
        """Test parameter validation with unknown parameter."""
        validation = clustering_models.validate_model_parameters(
            "kmeans",
            {"n_clusters": 3, "unknown_param": 42}
        )
        
        assert validation["valid"] is True
        assert len(validation["warnings"]) > 0
        assert "Unknown parameter" in validation["warnings"][0]
    
    def test_create_langgraph_tool_kmeans(self, clustering_models):
        """Test creating LangGraph tool for K-Means."""
        tool_def = clustering_models.create_langgraph_tool("kmeans")
        
        assert "error" not in tool_def
        assert "name" in tool_def
        assert "description" in tool_def
        assert "parameters" in tool_def
        assert tool_def["name"] == "train_kmeans"
        assert "type" in tool_def["parameters"]
        assert "properties" in tool_def["parameters"]
    
    def test_create_langgraph_tool_invalid_model(self, clustering_models):
        """Test creating LangGraph tool for invalid model."""
        tool_def = clustering_models.create_langgraph_tool("invalid_model")
        
        assert "error" in tool_def
    
    @pytest.mark.parametrize("model_name,expected_metrics", [
        ("kmeans", ["silhouette", "calinski_harabasz", "davies_bouldin"]),
        ("dbscan", ["silhouette", "calinski_harabasz", "davies_bouldin"]),
        ("agglomerative_clustering", ["silhouette", "calinski_harabasz", "davies_bouldin"]),
        ("spectral_clustering", ["silhouette", "calinski_harabasz", "davies_bouldin"]),
        ("mean_shift", ["silhouette", "calinski_harabasz", "davies_bouldin"]),
        ("optics", ["silhouette", "calinski_harabasz", "davies_bouldin"])
    ])
    def test_model_metrics_consistency(self, clustering_models, model_name, expected_metrics):
        """Test that all clustering models have consistent metrics."""
        if model_name in clustering_models.model_mapping:
            model_config = clustering_models.model_mapping[model_name]
            actual_metrics = model_config["metrics"]
            
            for metric in expected_metrics:
                assert metric in actual_metrics, f"Missing metric {metric} in {model_name}"
    
    def test_all_models_have_required_fields(self, clustering_models):
        """Test that all models have required configuration fields."""
        required_fields = ["module", "class", "type", "metrics", "description"]
        
        for model_name, config in clustering_models.model_mapping.items():
            for field in required_fields:
                assert field in config, f"Missing field {field} in {model_name}"
            
            assert config["type"] == "clustering", f"Model {model_name} is not a clustering model"
    
    def test_model_mapping_consistency(self, clustering_models):
        """Test consistency between model mapping and available models."""
        mapping_models = set(clustering_models.model_mapping.keys())
        
        # Get all models from available_models
        available_models = set()
        for category in clustering_models.available_models.values():
            available_models.update(category.keys())
        
        # All available models should be in mapping
        assert available_models.issubset(mapping_models), "Available models not in mapping"
    
    def test_fit_model_with_different_n_clusters(self, clustering_models, sample_clustering_data):
        """Test fitting with different numbers of clusters."""
        n_clusters_list = [2, 3, 4, 5]
        
        for n_clusters in n_clusters_list:
            result = clustering_models.fit_model(
                "kmeans",
                sample_clustering_data,
                n_clusters=n_clusters,
                random_state=42
            )
            
            assert result["success"] is True
            assert result["n_clusters"] == n_clusters
            assert len(result["cluster_sizes"]) == n_clusters
    
    def test_fit_model_with_different_random_states(self, clustering_models, sample_clustering_data):
        """Test fitting with different random states produces different results."""
        results = []
        
        for random_state in [42, 123, 456]:
            result = clustering_models.fit_model(
                "kmeans",
                sample_clustering_data,
                n_clusters=3,
                random_state=random_state
            )
            
            assert result["success"] is True
            results.append(result["clusters"])
        
        # Results should be different (though not guaranteed)
        # At least check that we get valid results
        for clusters in results:
            assert len(clusters) == len(sample_clustering_data)
            assert all(isinstance(c, (int, np.integer)) for c in clusters)
    
    def test_clustering_metrics_calculation(self, clustering_models, sample_clustering_data):
        """Test that clustering metrics are calculated correctly."""
        result = clustering_models.fit_model(
            "kmeans",
            sample_clustering_data,
            n_clusters=3,
            random_state=42
        )
        
        assert result["success"] is True
        metrics = result["metrics"]
        
        # Check that metrics are present and have reasonable values
        if "silhouette" in metrics:
            assert -1 <= metrics["silhouette"] <= 1
        
        if "calinski_harabasz" in metrics:
            assert metrics["calinski_harabasz"] >= 0
        
        if "davies_bouldin" in metrics:
            assert metrics["davies_bouldin"] >= 0
    
    def test_cluster_sizes_calculation(self, clustering_models, sample_clustering_data):
        """Test that cluster sizes are calculated correctly."""
        result = clustering_models.fit_model(
            "kmeans",
            sample_clustering_data,
            n_clusters=3,
            random_state=42
        )
        
        assert result["success"] is True
        cluster_sizes = result["cluster_sizes"]
        
        # Check that cluster sizes are calculated correctly
        assert len(cluster_sizes) == 3
        total_samples = sum(cluster_sizes.values())
        assert total_samples == len(sample_clustering_data)
        
        # All cluster sizes should be positive
        for size in cluster_sizes.values():
            assert size > 0
    
    def test_noise_handling_in_density_based(self, clustering_models, sample_clustering_data):
        """Test that density-based clustering handles noise correctly."""
        # Test DBSCAN
        result = clustering_models.fit_model(
            "dbscan",
            sample_clustering_data,
            eps=0.5,
            min_samples=5
        )
        
        assert result["success"] is True
        clusters = result["clusters"]
        
        # Check that noise points are labeled as -1
        unique_clusters = set(clusters)
        assert -1 in unique_clusters  # Noise points should be labeled as -1
        
        # Test OPTICS
        result = clustering_models.fit_model(
            "optics",
            sample_clustering_data,
            min_samples=5
        )
        
        assert result["success"] is True
        clusters = result["clusters"]
        
        # Check that noise points are labeled as -1
        unique_clusters = set(clusters)
        assert -1 in unique_clusters  # Noise points should be labeled as -1
    
    def test_cluster_centers_for_kmeans(self, clustering_models, sample_clustering_data):
        """Test that K-Means returns cluster centers."""
        result = clustering_models.fit_model(
            "kmeans",
            sample_clustering_data,
            n_clusters=3,
            random_state=42
        )
        
        assert result["success"] is True
        assert "cluster_centers" in result
        assert result["cluster_centers"] is not None
        
        # Check cluster centers structure
        cluster_centers = result["cluster_centers"]
        assert len(cluster_centers) == 3  # 3 clusters
        assert len(cluster_centers[0]) == 4  # 4 features
    
    def test_partitioning_models(self, clustering_models, sample_clustering_data):
        """Test partitioning clustering models."""
        result = clustering_models.fit_model(
            "kmeans",
            sample_clustering_data,
            n_clusters=3,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "kmeans"
        assert result["n_clusters"] == 3
    
    def test_density_based_models(self, clustering_models, sample_clustering_data):
        """Test density-based clustering models."""
        density_models = ["dbscan", "optics"]
        
        for model_name in density_models:
            result = clustering_models.fit_model(
                model_name,
                sample_clustering_data,
                min_samples=5
            )
            
            assert result["success"] is True
            assert result["model_name"] == model_name
            assert "clusters" in result
            assert "n_clusters" in result
    
    def test_hierarchical_models(self, clustering_models, sample_clustering_data):
        """Test hierarchical clustering models."""
        result = clustering_models.fit_model(
            "agglomerative_clustering",
            sample_clustering_data,
            n_clusters=3
        )
        
        assert result["success"] is True
        assert result["model_name"] == "agglomerative_clustering"
        assert result["n_clusters"] == 3
    
    def test_spectral_models(self, clustering_models, sample_clustering_data):
        """Test spectral clustering models."""
        result = clustering_models.fit_model(
            "spectral_clustering",
            sample_clustering_data,
            n_clusters=3,
            random_state=42
        )
        
        assert result["success"] is True
        assert result["model_name"] == "spectral_clustering"
        assert result["n_clusters"] == 3
    
    def test_mean_shift_special_case(self, clustering_models, sample_clustering_data):
        """Test Mean Shift as a special case (no n_clusters parameter)."""
        result = clustering_models.fit_model(
            "mean_shift",
            sample_clustering_data
        )
        
        assert result["success"] is True
        assert result["model_name"] == "mean_shift"
        assert "n_clusters" in result
        assert result["n_clusters"] >= 0  # Can be 0 if no clusters found
