"""
Universal Scikit-learn Tools - Algorithms Package.

This package contains specialized algorithm implementations for different types
of machine learning tasks: classification, regression, clustering, and preprocessing.
"""

from .base_model import BaseSklearnModel
from .classification import ClassificationModels
from .regression import RegressionModels
from .clustering import ClusteringModels
from .preprocessing import PreprocessingModels

__all__ = [
    'BaseSklearnModel',
    'ClassificationModels',
    'RegressionModels', 
    'ClusteringModels',
    'PreprocessingModels'
]
