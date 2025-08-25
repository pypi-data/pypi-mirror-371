"""
Preprocessing Models for Universal Scikit-learn Tools.

This module provides preprocessing model implementations including:
- Dimensionality reduction (PCA, TruncatedSVD, Factor Analysis, FastICA)
- Feature selection (SelectKBest, SelectPercentile, RFE, RFECV)
"""

import importlib
from typing import Dict, Any
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from .base_model import BaseSklearnModel


class PreprocessingModels(BaseSklearnModel):
    """
    Preprocessing models implementation.
    
    This class provides functionality for training and evaluating various
    preprocessing models from scikit-learn.
    """
    
    def _get_model_mapping(self) -> Dict[str, Any]:
        """Define the model mapping for preprocessing algorithms."""
        return {
            # Dimensionality Reduction
            "pca": {
                "module": "sklearn.decomposition",
                "class": "PCA",
                "type": "preprocessor",
                "metrics": ["explained_variance_ratio"],
                "description": "Principal Component Analysis"
            },
            "truncated_svd": {
                "module": "sklearn.decomposition",
                "class": "TruncatedSVD",
                "type": "preprocessor",
                "metrics": ["explained_variance_ratio"],
                "description": "Truncated Singular Value Decomposition"
            },
            "factor_analysis": {
                "module": "sklearn.decomposition",
                "class": "FactorAnalysis",
                "type": "preprocessor",
                "metrics": ["explained_variance_ratio"],
                "description": "Factor Analysis"
            },
            "fast_ica": {
                "module": "sklearn.decomposition",
                "class": "FastICA",
                "type": "preprocessor",
                "metrics": ["kurtosis"],
                "description": "Fast Independent Component Analysis"
            },
            
            # Feature Selection
            "select_k_best": {
                "module": "sklearn.feature_selection",
                "class": "SelectKBest",
                "type": "preprocessor",
                "metrics": ["feature_scores"],
                "description": "Select K best features"
            },
            "select_percentile": {
                "module": "sklearn.feature_selection",
                "class": "SelectPercentile",
                "type": "preprocessor",
                "metrics": ["feature_scores"],
                "description": "Select features based on percentile"
            },
            "rfe": {
                "module": "sklearn.feature_selection",
                "class": "RFE",
                "type": "preprocessor",
                "metrics": ["feature_ranking"],
                "description": "Recursive Feature Elimination"
            },
            "rfecv": {
                "module": "sklearn.feature_selection",
                "class": "RFECV",
                "type": "preprocessor",
                "metrics": ["feature_ranking", "cv_scores"],
                "description": "Recursive Feature Elimination with Cross-Validation"
            }
        }
    
    def _get_available_models(self) -> Dict[str, Any]:
        """Define available preprocessing models grouped by type."""
        return {
            "dimensionality_reduction": {
                "pca": {
                    "description": "Principal Component Analysis",
                    "class": "PCA",
                    "module": "sklearn.decomposition",
                    "metrics": ["explained_variance_ratio"]
                },
                "truncated_svd": {
                    "description": "Truncated Singular Value Decomposition",
                    "class": "TruncatedSVD",
                    "module": "sklearn.decomposition",
                    "metrics": ["explained_variance_ratio"]
                },
                "factor_analysis": {
                    "description": "Factor Analysis",
                    "class": "FactorAnalysis",
                    "module": "sklearn.decomposition",
                    "metrics": ["explained_variance_ratio"]
                },
                "fast_ica": {
                    "description": "Fast Independent Component Analysis",
                    "class": "FastICA",
                    "module": "sklearn.decomposition",
                    "metrics": ["kurtosis"]
                }
            },
            "feature_selection": {
                "select_k_best": {
                    "description": "Select K best features",
                    "class": "SelectKBest",
                    "module": "sklearn.feature_selection",
                    "metrics": ["feature_scores"]
                },
                "select_percentile": {
                    "description": "Select features based on percentile",
                    "class": "SelectPercentile",
                    "module": "sklearn.feature_selection",
                    "metrics": ["feature_scores"]
                },
                "rfe": {
                    "description": "Recursive Feature Elimination",
                    "class": "RFE",
                    "module": "sklearn.feature_selection",
                    "metrics": ["feature_ranking"]
                },
                "rfecv": {
                    "description": "Recursive Feature Elimination with Cross-Validation",
                    "class": "RFECV",
                    "module": "sklearn.feature_selection",
                    "metrics": ["feature_ranking", "cv_scores"]
                }
            }
        }
    
    def fit_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Fit a preprocessing model."""
        try:
            # Validate model name
            if model_name not in self.model_mapping:
                return self.create_error_result(
                    model_name,
                    f"Model '{model_name}' not found. Available models: {list(self.model_mapping.keys())}"
                )
            
            # Extract parameters
            target_column = kwargs.get('target_column')
            random_state = kwargs.get('random_state', 42)
            
            # Remove non-model parameters
            model_params = {k: v for k, v in kwargs.items() 
                          if k not in ['target_column', 'random_state']}
            
            # Filter parameters based on model type
            if model_name == "select_k_best":
                model_params = {k: v for k, v in model_params.items() if k in ['k', 'score_func']}
            elif model_name == "select_percentile":
                model_params = {k: v for k, v in model_params.items() if k in ['percentile', 'score_func']}
            elif model_name == "rfe":
                model_params = {k: v for k, v in model_params.items() if k in ['n_features_to_select', 'step', 'verbose']}
            elif model_name == "rfecv":
                model_params = {k: v for k, v in model_params.items() if k in ['min_features_to_select', 'step', 'cv', 'scoring', 'verbose']}
            
            # Prepare data
            if target_column and target_column in data.columns:
                # If target column is provided, use it for supervised preprocessing
                data_prep = self.prepare_data_for_supervised_learning(
                    data, target_column, test_size=0.2, random_state=random_state
                )
                if "error" in data_prep:
                    return self.create_error_result(model_name, data_prep["error"])
                X_train = data_prep["X_train"]  # Use training data for fitting
                # Remove target column from full data for transformation
                X_full = data_prep["data_clean"].drop(columns=[target_column])
                y_train = data_prep["y_train"]
                data_shape = X_full.shape
            else:
                # For unsupervised preprocessing, use all data
                data_prep = self.prepare_data_for_unsupervised_learning(data)
                if "error" in data_prep:
                    return self.create_error_result(model_name, data_prep["error"])
                X_train = data_prep["X"]
                X_full = data_prep["X"]
                y_train = None
                data_shape = X_full.shape
            
            # Scale features for certain preprocessors
            if model_name in ["pca", "truncated_svd", "factor_analysis", "fast_ica"]:
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_full_scaled = scaler.transform(X_full)
            else:
                X_train_scaled = X_train
                X_full_scaled = X_full
            
            # Import and instantiate model
            mapping = self.model_mapping[model_name]
            module = importlib.import_module(mapping["module"])
            model_class = getattr(module, mapping["class"])
            
            # Handle special cases
            if model_name in ["rfe", "rfecv"]:
                # RFE and RFECV need an estimator
                from sklearn.linear_model import LogisticRegression
                estimator = LogisticRegression(random_state=random_state)
                model_params['estimator'] = estimator
            
            # Handle parameter name differences
            if model_name == "factor_analysis" and "n_factors" in model_params:
                model_params["n_components"] = model_params.pop("n_factors")
            
            # Add random_state if the model supports it
            if hasattr(model_class, 'random_state'):
                model_params['random_state'] = random_state
            
            model = model_class(**model_params)
            
            # Fit and transform the data
            if hasattr(model, 'fit_transform'):
                if y_train is not None and hasattr(model, 'fit'):
                    # For supervised preprocessing
                    model.fit(X_train_scaled, y_train)
                    transformed_data = model.transform(X_full_scaled)
                else:
                    # For unsupervised preprocessing
                    transformed_data = model.fit_transform(X_full_scaled)
            else:
                # For models that don't have fit_transform
                if y_train is not None and hasattr(model, 'fit'):
                    model.fit(X_train_scaled, y_train)
                else:
                    model.fit(X_train_scaled)
                transformed_data = model.transform(X_full_scaled)
            
            # Calculate preprocessing metrics
            metrics = {}
            
            # Explained variance ratio for dimensionality reduction
            if hasattr(model, 'explained_variance_ratio_'):
                metrics["explained_variance_ratio"] = model.explained_variance_ratio_.tolist()
                metrics["cumulative_variance_ratio"] = np.cumsum(model.explained_variance_ratio_).tolist()
            
            # Feature scores for feature selection
            if hasattr(model, 'scores_'):
                metrics["feature_scores"] = model.scores_.tolist()
            
            # Feature ranking for RFE
            if hasattr(model, 'ranking_'):
                metrics["feature_ranking"] = model.ranking_.tolist()
            
            # CV scores for RFECV
            if hasattr(model, 'cv_results_'):
                metrics["cv_scores"] = model.cv_results_
            
            # Kurtosis for ICA
            if model_name == "fast_ica":
                try:
                    from scipy.stats import kurtosis
                    transformed_kurtosis = kurtosis(transformed_data, axis=0)
                    metrics["kurtosis"] = transformed_kurtosis.tolist()
                except:
                    pass
            
            return self.create_result_dict(
                model_name=model_name,
                model=model,
                data_shape=data_shape,
                metrics=metrics,
                transformed_data=transformed_data.tolist() if hasattr(transformed_data, 'tolist') else transformed_data,
                transformed_shape=transformed_data.shape,
                label_encoders=data_prep["label_encoders"]
            )
            
        except Exception as e:
            return self.create_error_result(model_name, f"Failed to train {model_name}: {str(e)}")
