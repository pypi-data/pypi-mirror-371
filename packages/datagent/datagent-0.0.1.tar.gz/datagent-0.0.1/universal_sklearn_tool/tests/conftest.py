"""
Pytest configuration and shared fixtures for the refactored universal sklearn tool tests.

This module provides shared fixtures and configuration that can be used across
all test modules for the refactored architecture.
"""

import pytest
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.datasets import (
    # Toy datasets (preferred)
    load_iris, load_digits, load_wine, load_breast_cancer, load_diabetes, load_linnerud,
    # Real world datasets (secondary)
    fetch_california_housing, fetch_olivetti_faces, fetch_lfw_people,
    # Generated datasets (fallback)
    make_classification, make_regression, make_blobs
)


@pytest.fixture(scope="session")
def sample_classification_data():
    """Create sample classification data for testing using sklearn datasets."""
    try:
        # Use Iris dataset for classification
        iris = load_iris()
        data = pd.DataFrame(iris.data, columns=iris.feature_names)
        data['target'] = iris.target
        return data
    except Exception:
        # Fallback to generated data if dataset loading fails
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 3, n_samples)  # 3 classes
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data['target'] = y
        return data


@pytest.fixture(scope="session")
def sample_binary_data():
    """Create sample binary classification data for testing using sklearn datasets."""
    try:
        # Use Breast Cancer dataset for binary classification
        breast_cancer = load_breast_cancer()
        data = pd.DataFrame(breast_cancer.data, columns=breast_cancer.feature_names)
        data['target'] = breast_cancer.target
        return data
    except Exception:
        # Fallback to generated data if dataset loading fails
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 2, n_samples)  # 2 classes
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data['target'] = y
        return data


@pytest.fixture(scope="session")
def sample_regression_data():
    """Create sample regression data for testing using sklearn datasets."""
    try:
        # Use Diabetes dataset for regression
        diabetes = load_diabetes()
        data = pd.DataFrame(diabetes.data, columns=diabetes.feature_names)
        data['target'] = diabetes.target
        return data
    except Exception:
        # Fallback to generated data if dataset loading fails
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        X = np.random.randn(n_samples, n_features)
        y = np.random.randn(n_samples)  # Continuous target
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data['target'] = y
        return data


@pytest.fixture(scope="session")
def sample_clustering_data():
    """Create sample clustering data for testing using sklearn datasets."""
    try:
        # Use Iris dataset without target for clustering
        iris = load_iris()
        data = pd.DataFrame(iris.data, columns=iris.feature_names)
        return data
    except Exception:
        # Fallback to generated data if dataset loading fails
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        X = np.random.randn(n_samples, n_features)
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        return data


@pytest.fixture(scope="session")
def sample_preprocessing_data():
    """Create sample preprocessing data for testing using sklearn datasets."""
    try:
        # Use Wine dataset without target for unsupervised preprocessing
        wine = load_wine()
        data = pd.DataFrame(wine.data, columns=wine.feature_names)
        return data
    except Exception:
        # Fallback to generated data if dataset loading fails
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        X = np.random.randn(n_samples, n_features)
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        return data


@pytest.fixture(scope="session")
def sample_preprocessing_data_with_target():
    """Create sample preprocessing data with target for supervised preprocessing using sklearn datasets."""
    try:
        # Use Digits dataset for supervised preprocessing
        digits = load_digits()
        data = pd.DataFrame(digits.data, columns=[f'pixel_{i}' for i in range(digits.data.shape[1])])
        data['target'] = digits.target
        return data
    except Exception:
        # Fallback to generated data if dataset loading fails
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 3, n_samples)  # 3 classes
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data['target'] = y
        return data


@pytest.fixture(scope="session")
def sample_data_with_categorical():
    """Create sample data with categorical features using sklearn datasets."""
    try:
        # Use Wine dataset and add some categorical features
        wine = load_wine()
        data = pd.DataFrame(wine.data, columns=wine.feature_names)
        data['target'] = wine.target
        
        # Add categorical features
        n_samples = len(data)
        data['categorical_1'] = np.random.choice(['A', 'B', 'C'], n_samples)
        data['categorical_2'] = np.random.choice(['X', 'Y'], n_samples)
        
        return data
    except Exception:
        # Fallback to generated data if dataset loading fails
        np.random.seed(42)
        n_samples = 100
        data = pd.DataFrame({
            'numeric_1': np.random.randn(n_samples),
            'numeric_2': np.random.randn(n_samples),
            'categorical_1': np.random.choice(['A', 'B', 'C'], n_samples),
            'categorical_2': np.random.choice(['X', 'Y'], n_samples),
            'target': np.random.randint(0, 3, n_samples)
        })
        return data


@pytest.fixture(scope="session")
def sample_data_with_missing():
    """Create sample data with missing values using sklearn datasets."""
    try:
        # Use Diabetes dataset and add missing values
        diabetes = load_diabetes()
        data = pd.DataFrame(diabetes.data, columns=diabetes.feature_names)
        data['target'] = diabetes.target
        
        # Add some missing values
        data.loc[10:15, diabetes.feature_names[0]] = np.nan
        data.loc[20:25, diabetes.feature_names[1]] = np.nan
        data.loc[30:35, 'target'] = np.nan
        
        return data
    except Exception:
        # Fallback to generated data if dataset loading fails
        np.random.seed(42)
        n_samples = 100
        data = pd.DataFrame({
            'feature_1': np.random.randn(n_samples),
            'feature_2': np.random.randn(n_samples),
            'feature_3': np.random.randn(n_samples),
            'target': np.random.randint(0, 3, n_samples)
        })
        
        # Add some missing values
        data.loc[10:15, 'feature_1'] = np.nan
        data.loc[20:25, 'feature_2'] = np.nan
        data.loc[30:35, 'target'] = np.nan
        
        return data


@pytest.fixture(scope="session")
def sample_empty_data():
    """Create empty DataFrame for testing."""
    return pd.DataFrame()


@pytest.fixture(scope="session")
def sample_single_feature_data():
    """Create sample data with single feature for testing edge cases using sklearn datasets."""
    try:
        # Use Diabetes dataset with only one feature
        diabetes = load_diabetes()
        data = pd.DataFrame({diabetes.feature_names[0]: diabetes.data[:, 0]})
        data['target'] = diabetes.target
        return data
    except Exception:
        # Fallback to generated data if dataset loading fails
        np.random.seed(42)
        n_samples = 50
        data = pd.DataFrame({
            'feature_1': np.random.randn(n_samples),
            'target': np.random.randint(0, 2, n_samples)
        })
        return data


@pytest.fixture(scope="session")
def sample_large_data():
    """Create larger sample data for performance testing using sklearn datasets."""
    try:
        # Use California Housing dataset for large data
        california = fetch_california_housing()
        data = pd.DataFrame(california.data, columns=california.feature_names)
        data['target'] = california.target
        return data
    except Exception:
        # Fallback to generated data if dataset loading fails
        np.random.seed(42)
        n_samples = 1000
        n_features = 20
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 3, n_samples)  # 3 classes
        data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        data['target'] = y
        return data


@pytest.fixture(scope="session")
def sample_clustering_data_with_categorical():
    """Create sample clustering data with categorical features using sklearn datasets."""
    try:
        # Use Wine dataset and add categorical features
        wine = load_wine()
        data = pd.DataFrame(wine.data, columns=wine.feature_names)
        
        # Add categorical features
        n_samples = len(data)
        data['categorical_1'] = np.random.choice(['A', 'B', 'C'], n_samples)
        data['categorical_2'] = np.random.choice(['X', 'Y'], n_samples)
        
        return data
    except Exception:
        # Fallback to generated data if dataset loading fails
        np.random.seed(42)
        n_samples = 100
        data = pd.DataFrame({
            'numeric_1': np.random.randn(n_samples),
            'numeric_2': np.random.randn(n_samples),
            'categorical_1': np.random.choice(['A', 'B', 'C'], n_samples),
            'categorical_2': np.random.choice(['X', 'Y'], n_samples)
        })
        return data


@pytest.fixture(scope="session")
def expected_classification_metrics():
    """Expected classification metrics."""
    return ["accuracy", "precision", "recall", "f1"]


@pytest.fixture(scope="session")
def expected_regression_metrics():
    """Expected regression metrics."""
    return ["mse", "mae", "r2"]


@pytest.fixture(scope="session")
def expected_clustering_metrics():
    """Expected clustering metrics."""
    return ["silhouette", "calinski_harabasz", "davies_bouldin"]


@pytest.fixture(scope="session")
def expected_preprocessing_metrics():
    """Expected preprocessing metrics."""
    return ["explained_variance_ratio", "feature_scores", "feature_ranking", "kurtosis"]


@pytest.fixture(scope="session")
def model_categories():
    """Model categories for testing."""
    return {
        "classification": ["linear_models", "tree_based", "support_vector_machines", 
                          "neural_networks", "naive_bayes", "discriminant_analysis", 
                          "gaussian_processes", "nearest_neighbors"],
        "regression": ["linear_models", "tree_based", "support_vector_regression", 
                      "neural_networks", "gaussian_processes", "nearest_neighbors", "other"],
        "clustering": ["partitioning", "density_based", "hierarchical", "spectral", "other"],
        "preprocessing": ["dimensionality_reduction", "feature_selection"]
    }


@pytest.fixture(scope="session")
def required_model_fields():
    """Required fields for model configuration."""
    return ["module", "class", "type", "metrics", "description"]


@pytest.fixture(scope="session")
def test_parameters():
    """Common test parameters."""
    return {
        "random_state": 42,
        "test_size": 0.2,
        "n_estimators": 10,
        "max_depth": 5,
        "n_clusters": 3,
        "n_components": 3,
        "n_neighbors": 5,
        "k": 3,
        "percentile": 50,
        "n_features_to_select": 3,
        "min_features_to_select": 1,
        "alpha": 1.0,
        "C": 1.0,
        "kernel": "rbf",
        "eps": 0.5,
        "min_samples": 5,
        "hidden_layer_sizes": (10,),
        "max_iter": 100
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "classification: marks tests as classification tests"
    )
    config.addinivalue_line(
        "markers", "regression: marks tests as regression tests"
    )
    config.addinivalue_line(
        "markers", "clustering: marks tests as clustering tests"
    )
    config.addinivalue_line(
        "markers", "preprocessing: marks tests as preprocessing tests"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names."""
    for item in items:
        # Mark tests based on test file names
        if "test_classification" in item.nodeid:
            item.add_marker(pytest.mark.classification)
        elif "test_regression" in item.nodeid:
            item.add_marker(pytest.mark.regression)
        elif "test_clustering" in item.nodeid:
            item.add_marker(pytest.mark.clustering)
        elif "test_preprocessing" in item.nodeid:
            item.add_marker(pytest.mark.preprocessing)
        elif "test_base_model" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_universal_estimator_refactored" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests based on certain patterns
        if any(pattern in item.nodeid for pattern in ["large_data", "performance", "slow"]):
            item.add_marker(pytest.mark.slow)
