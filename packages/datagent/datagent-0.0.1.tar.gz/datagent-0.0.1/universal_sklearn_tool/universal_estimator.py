"""
Universal Scikit-learn Estimator Template for LangGraph Agent.

This module provides a comprehensive template function that can handle all scikit-learn
estimators through a unified interface, making it suitable for use with LLMs in LangGraph.
"""

import json
import inspect
import importlib
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    # Classification metrics
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score,
    # Regression metrics
    mean_squared_error, mean_absolute_error, r2_score,
    # Clustering metrics
    silhouette_score, calinski_harabasz_score, davies_bouldin_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive mapping of all scikit-learn estimators
ESTIMATOR_MAPPING = {
    # Linear Models
    "linear_regression": {
        "module": "sklearn.linear_model",
        "class": "LinearRegression",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Ordinary least squares Linear Regression"
    },
    "ridge_regression": {
        "module": "sklearn.linear_model",
        "class": "Ridge",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Ridge regression with L2 regularization"
    },
    "lasso_regression": {
        "module": "sklearn.linear_model",
        "class": "Lasso",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Lasso regression with L1 regularization"
    },
    "elastic_net": {
        "module": "sklearn.linear_model",
        "class": "ElasticNet",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Elastic Net regression with L1 and L2 regularization"
    },
    "logistic_regression": {
        "module": "sklearn.linear_model",
        "class": "LogisticRegression",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Logistic regression for classification"
    },
    "sgd_classifier": {
        "module": "sklearn.linear_model",
        "class": "SGDClassifier",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Stochastic Gradient Descent classifier"
    },
    "sgd_regressor": {
        "module": "sklearn.linear_model",
        "class": "SGDRegressor",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Stochastic Gradient Descent regressor"
    },
    
    # Tree-based Models
    "decision_tree_classifier": {
        "module": "sklearn.tree",
        "class": "DecisionTreeClassifier",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Decision Tree classifier"
    },
    "decision_tree_regressor": {
        "module": "sklearn.tree",
        "class": "DecisionTreeRegressor",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Decision Tree regressor"
    },
    "random_forest_classifier": {
        "module": "sklearn.ensemble",
        "class": "RandomForestClassifier",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Random Forest classifier"
    },
    "random_forest_regressor": {
        "module": "sklearn.ensemble",
        "class": "RandomForestRegressor",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Random Forest regressor"
    },
    "gradient_boosting_classifier": {
        "module": "sklearn.ensemble",
        "class": "GradientBoostingClassifier",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Gradient Boosting classifier"
    },
    "gradient_boosting_regressor": {
        "module": "sklearn.ensemble",
        "class": "GradientBoostingRegressor",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Gradient Boosting regressor"
    },
    "extra_trees_classifier": {
        "module": "sklearn.ensemble",
        "class": "ExtraTreesClassifier",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Extra Trees classifier"
    },
    "extra_trees_regressor": {
        "module": "sklearn.ensemble",
        "class": "ExtraTreesRegressor",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Extra Trees regressor"
    },
    "ada_boost_classifier": {
        "module": "sklearn.ensemble",
        "class": "AdaBoostClassifier",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "AdaBoost classifier"
    },
    "ada_boost_regressor": {
        "module": "sklearn.ensemble",
        "class": "AdaBoostRegressor",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "AdaBoost regressor"
    },
    
    # Support Vector Machines
    "svc": {
        "module": "sklearn.svm",
        "class": "SVC",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Support Vector Classification"
    },
    "svr": {
        "module": "sklearn.svm",
        "class": "SVR",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Support Vector Regression"
    },
    "linear_svc": {
        "module": "sklearn.svm",
        "class": "LinearSVC",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Linear Support Vector Classification"
    },
    "linear_svr": {
        "module": "sklearn.svm",
        "class": "LinearSVR",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Linear Support Vector Regression"
    },
    
    # Nearest Neighbors
    "knn_classifier": {
        "module": "sklearn.neighbors",
        "class": "KNeighborsClassifier",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "K-Nearest Neighbors classifier"
    },
    "knn_regressor": {
        "module": "sklearn.neighbors",
        "class": "KNeighborsRegressor",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "K-Nearest Neighbors regressor"
    },
    "radius_neighbors_classifier": {
        "module": "sklearn.neighbors",
        "class": "RadiusNeighborsClassifier",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Radius-based neighbors classifier"
    },
    "radius_neighbors_regressor": {
        "module": "sklearn.neighbors",
        "class": "RadiusNeighborsRegressor",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Radius-based neighbors regressor"
    },
    
    # Neural Networks
    "mlp_classifier": {
        "module": "sklearn.neural_network",
        "class": "MLPClassifier",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Multi-layer Perceptron classifier"
    },
    "mlp_regressor": {
        "module": "sklearn.neural_network",
        "class": "MLPRegressor",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Multi-layer Perceptron regressor"
    },
    
    # Naive Bayes
    "gaussian_nb": {
        "module": "sklearn.naive_bayes",
        "class": "GaussianNB",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Gaussian Naive Bayes classifier"
    },
    "multinomial_nb": {
        "module": "sklearn.naive_bayes",
        "class": "MultinomialNB",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Multinomial Naive Bayes classifier"
    },
    "bernoulli_nb": {
        "module": "sklearn.naive_bayes",
        "class": "BernoulliNB",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Bernoulli Naive Bayes classifier"
    },
    "complement_nb": {
        "module": "sklearn.naive_bayes",
        "class": "ComplementNB",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Complement Naive Bayes classifier"
    },
    
    # Clustering
    "kmeans": {
        "module": "sklearn.cluster",
        "class": "KMeans",
        "type": "clustering",
        "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
        "description": "K-Means clustering"
    },
    "dbscan": {
        "module": "sklearn.cluster",
        "class": "DBSCAN",
        "type": "clustering",
        "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
        "description": "DBSCAN clustering"
    },
    "agglomerative_clustering": {
        "module": "sklearn.cluster",
        "class": "AgglomerativeClustering",
        "type": "clustering",
        "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
        "description": "Agglomerative clustering"
    },
    "spectral_clustering": {
        "module": "sklearn.cluster",
        "class": "SpectralClustering",
        "type": "clustering",
        "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
        "description": "Spectral clustering"
    },
    "mean_shift": {
        "module": "sklearn.cluster",
        "class": "MeanShift",
        "type": "clustering",
        "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
        "description": "Mean shift clustering"
    },
    "optics": {
        "module": "sklearn.cluster",
        "class": "OPTICS",
        "type": "clustering",
        "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
        "description": "OPTICS clustering"
    },
    
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
    },
    
    # Discriminant Analysis
    "lda": {
        "module": "sklearn.discriminant_analysis",
        "class": "LinearDiscriminantAnalysis",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Linear Discriminant Analysis"
    },
    "qda": {
        "module": "sklearn.discriminant_analysis",
        "class": "QuadraticDiscriminantAnalysis",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Quadratic Discriminant Analysis"
    },
    
    # Gaussian Processes
    "gaussian_process_classifier": {
        "module": "sklearn.gaussian_process",
        "class": "GaussianProcessClassifier",
        "type": "classifier",
        "metrics": ["accuracy", "precision", "recall", "f1"],
        "description": "Gaussian Process classifier"
    },
    "gaussian_process_regressor": {
        "module": "sklearn.gaussian_process",
        "class": "GaussianProcessRegressor",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Gaussian Process regressor"
    },
    
    # Isotonic Regression
    "isotonic_regression": {
        "module": "sklearn.isotonic",
        "class": "IsotonicRegression",
        "type": "regressor",
        "metrics": ["mse", "mae", "r2"],
        "description": "Isotonic regression"
    }
}


def extract_estimator_info(estimator_name: str) -> Dict[str, Any]:
    """
    Extract estimator description, parameters, and their descriptions from docstring.
    
    Args:
        estimator_name: Name of the estimator in the mapping
        
    Returns:
        Dictionary containing estimator information
    """
    try:
        if estimator_name not in ESTIMATOR_MAPPING:
            return {"error": f"Estimator '{estimator_name}' not found in mapping"}
        
        mapping = ESTIMATOR_MAPPING[estimator_name]
        module_name = mapping["module"]
        class_name = mapping["class"]
        
        # Import the module and get the class
        module = importlib.import_module(module_name)
        estimator_class = getattr(module, class_name)
        
        # Get docstring
        docstring = estimator_class.__doc__ or ""
        
        # Extract parameters from docstring
        parameters = {}
        if docstring:
            # Simple parameter extraction from docstring
            lines = docstring.split('\n')
            in_params = False
            current_param = None
            
            for line in lines:
                line = line.strip()
                if 'Parameters' in line and '---' in line:
                    in_params = True
                    continue
                elif in_params and (line.startswith('Returns') or line.startswith('Attributes') or line.startswith('Examples')):
                    break
                elif in_params and line:
                    if ' : ' in line and not line.startswith('    '):
                        # This is a parameter name
                        param_name = line.split(' : ')[0].strip()
                        param_desc = line.split(' : ')[1].strip() if len(line.split(' : ')) > 1 else ""
                        current_param = param_name
                        parameters[param_name] = param_desc
                    elif line.startswith('    ') and current_param:
                        # This is a continuation of parameter description
                        parameters[current_param] += " " + line.strip()
        
        # Get signature for default values
        sig = inspect.signature(estimator_class.__init__)
        param_defaults = {}
        for name, param in sig.parameters.items():
            if name != 'self':
                if param.default != inspect.Parameter.empty:
                    param_defaults[name] = str(param.default)
                else:
                    param_defaults[name] = "Required"
        
        return {
            "estimator_name": estimator_name,
            "class_name": class_name,
            "module_name": module_name,
            "description": mapping["description"],
            "type": mapping["type"],
            "metrics": mapping["metrics"],
            "docstring": docstring,
            "parameters": parameters,
            "parameter_defaults": param_defaults,
            "full_signature": str(sig)
        }
        
    except Exception as e:
        logger.error(f"Failed to extract estimator info for {estimator_name}: {str(e)}")
        return {"error": f"Failed to extract estimator info: {str(e)}"}


def get_estimator_tool_description(estimator_name: str) -> str:
    """
    Generate a comprehensive tool description for LangGraph use.
    
    Args:
        estimator_name: Name of the estimator
        
    Returns:
        Formatted tool description string
    """
    info = extract_estimator_info(estimator_name)
    if "error" in info:
        return f"Error: {info['error']}"
    
    description = f"""
Train a {info['description']} ({info['class_name']}).

This tool trains a {info['type']} model using scikit-learn's {info['class_name']} class.

Parameters:
"""
    
    for param_name, param_desc in info['parameters'].items():
        default = info['parameter_defaults'].get(param_name, "Required")
        description += f"- {param_name}: {param_desc} (Default: {default})\n"
    
    description += f"""
Metrics calculated: {', '.join(info['metrics'])}

Returns:
- Trained model
- Predictions on test set
- Performance metrics
- Feature importance (if available)
"""
    
    return description


def universal_estimator(
    estimator_name: str,
    data: pd.DataFrame,
    target_column: str = None,
    test_size: float = 0.2,
    random_state: int = 42,
    **estimator_params
) -> Dict[str, Any]:
    """
    Universal function to train any scikit-learn estimator.
    
    Args:
        estimator_name: Name of the estimator from ESTIMATOR_MAPPING
        data: Input DataFrame
        target_column: Name of the target column (not needed for clustering/preprocessing)
        test_size: Fraction of data to use for testing (for supervised learning)
        random_state: Random state for reproducibility
        **estimator_params: Parameters to pass to the estimator
        
    Returns:
        Dictionary containing training results
    """
    try:
        # Validate estimator name
        if estimator_name not in ESTIMATOR_MAPPING:
            return {
                "success": False,
                "error": f"Estimator '{estimator_name}' not found. Available estimators: {list(ESTIMATOR_MAPPING.keys())}"
            }
        
        mapping = ESTIMATOR_MAPPING[estimator_name]
        estimator_type = mapping["type"]
        
        # Validate target column for supervised learning
        if estimator_type in ["classifier", "regressor"]:
            if target_column is None:
                return {
                    "success": False,
                    "error": f"Target column is required for {estimator_type} estimators"
                }
            if target_column not in data.columns:
                return {
                    "success": False,
                    "error": f"Target column '{target_column}' not found in data columns: {list(data.columns)}"
                }
        
        # Prepare data
        if estimator_type in ["classifier", "regressor"]:
            X = data.drop(columns=[target_column])
            y = data[target_column]
        else:
            # For clustering and preprocessing, use all data
            X = data.copy()
            y = None
        
        # Handle data preprocessing based on estimator type
        if estimator_type in ["classifier", "regressor"]:
            # For supervised learning, we need train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # Basic preprocessing
            if X_train.select_dtypes(include=['object']).shape[1] > 0:
                # Handle categorical variables
                categorical_columns = X_train.select_dtypes(include=['object']).columns
                label_encoders = {}
                
                for col in categorical_columns:
                    le = LabelEncoder()
                    X_train[col] = le.fit_transform(X_train[col].astype(str))
                    X_test[col] = le.transform(X_test[col].astype(str))
                    label_encoders[col] = le
            
            # Handle missing values
            X_train = X_train.fillna(X_train.median())
            X_test = X_test.fillna(X_test.median())
            
            # Scale features for certain estimators
            if estimator_name in ["svc", "svr", "linear_svc", "linear_svr", "mlp_classifier", "mlp_regressor"]:
                scaler = StandardScaler()
                X_train = scaler.fit_transform(X_train)
                X_test = scaler.transform(X_test)
            
        elif estimator_type == "clustering":
            # For clustering, use all data
            X_train = X.copy()
            X_test = None
            y_train = None
            y_test = None
            
            # Handle categorical variables
            if X_train.select_dtypes(include=['object']).shape[1] > 0:
                categorical_columns = X_train.select_dtypes(include=['object']).columns
                for col in categorical_columns:
                    le = LabelEncoder()
                    X_train[col] = le.fit_transform(X_train[col].astype(str))
            
            # Handle missing values
            X_train = X_train.fillna(X_train.median())
            
            # Scale features for clustering
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            
        elif estimator_type == "preprocessor":
            # For preprocessors, use all data
            X_train = X.copy()
            X_test = None
            y_train = None
            y_test = None
            
            # Handle categorical variables
            if X_train.select_dtypes(include=['object']).shape[1] > 0:
                categorical_columns = X_train.select_dtypes(include=['object']).columns
                for col in categorical_columns:
                    le = LabelEncoder()
                    X_train[col] = le.fit_transform(X_train[col].astype(str))
            
            # Handle missing values
            X_train = X_train.fillna(X_train.median())
        
        # Import and instantiate estimator
        module = importlib.import_module(mapping["module"])
        estimator_class = getattr(module, mapping["class"])
        estimator = estimator_class(**estimator_params)
        
        # Train the model
        if estimator_type in ["classifier", "regressor"]:
            estimator.fit(X_train, y_train)
            y_pred = estimator.predict(X_test)
            
            # Calculate metrics
            metrics = {}
            if estimator_type == "classifier":
                metrics["accuracy"] = accuracy_score(y_test, y_pred)
                metrics["precision"] = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                metrics["recall"] = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                metrics["f1"] = f1_score(y_test, y_pred, average='weighted', zero_division=0)
                
                # Additional classification metrics
                if hasattr(estimator, 'predict_proba'):
                    try:
                        y_pred_proba = estimator.predict_proba(X_test)
                        if len(np.unique(y_test)) == 2:  # Binary classification
                            metrics["roc_auc"] = roc_auc_score(y_test, y_pred_proba[:, 1])
                    except:
                        pass
                        
            elif estimator_type == "regressor":
                metrics["mse"] = mean_squared_error(y_test, y_pred)
                metrics["mae"] = mean_absolute_error(y_test, y_pred)
                metrics["r2"] = r2_score(y_test, y_pred)
            
            # Get feature importance if available
            feature_importance = None
            if hasattr(estimator, 'feature_importances_'):
                feature_importance = dict(zip(X.columns, estimator.feature_importances_))
            elif hasattr(estimator, 'coef_'):
                feature_importance = dict(zip(X.columns, estimator.coef_))
            
            result = {
                "success": True,
                "estimator_name": estimator_name,
                "estimator_type": estimator_type,
                "model": estimator,
                "predictions": y_pred.tolist() if hasattr(y_pred, 'tolist') else y_pred,
                "metrics": metrics,
                "feature_importance": feature_importance,
                "data_shape": {
                    "train": X_train.shape,
                    "test": X_test.shape if X_test is not None else None
                }
            }
            
        elif estimator_type == "clustering":
            # For clustering, predict clusters
            clusters = estimator.fit_predict(X_train)
            
            # Calculate clustering metrics
            metrics = {}
            if len(np.unique(clusters)) > 1:  # Need at least 2 clusters for metrics
                try:
                    metrics["silhouette"] = silhouette_score(X_train, clusters)
                except:
                    pass
                try:
                    metrics["calinski_harabasz"] = calinski_harabasz_score(X_train, clusters)
                except:
                    pass
                try:
                    metrics["davies_bouldin"] = davies_bouldin_score(X_train, clusters)
                except:
                    pass
            
            result = {
                "success": True,
                "estimator_name": estimator_name,
                "estimator_type": estimator_type,
                "model": estimator,
                "clusters": clusters.tolist() if hasattr(clusters, 'tolist') else clusters,
                "n_clusters": len(np.unique(clusters)),
                "metrics": metrics,
                "cluster_centers": estimator.cluster_centers_.tolist() if hasattr(estimator, 'cluster_centers_') else None,
                "data_shape": {"train": X_train.shape}
            }
            
        elif estimator_type == "preprocessor":
            # For preprocessors, transform the data
            if hasattr(estimator, 'fit_transform'):
                transformed_data = estimator.fit_transform(X_train)
            else:
                estimator.fit(X_train)
                transformed_data = estimator.transform(X_train)
            
            # Calculate preprocessing metrics
            metrics = {}
            if hasattr(estimator, 'explained_variance_ratio_'):
                metrics["explained_variance_ratio"] = estimator.explained_variance_ratio_.tolist()
                metrics["cumulative_variance_ratio"] = np.cumsum(estimator.explained_variance_ratio_).tolist()
            
            result = {
                "success": True,
                "estimator_name": estimator_name,
                "estimator_type": estimator_type,
                "model": estimator,
                "transformed_data": transformed_data.tolist() if hasattr(transformed_data, 'tolist') else transformed_data,
                "metrics": metrics,
                "data_shape": {"original": X_train.shape, "transformed": transformed_data.shape}
            }
        
        logger.info(f"Successfully trained {estimator_name} with metrics: {metrics}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to train {estimator_name}: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to train {estimator_name}: {str(e)}",
            "estimator_name": estimator_name
        }


def get_available_estimators() -> Dict[str, Any]:
    """
    Get list of all available estimators grouped by type.
    
    Returns:
        Dictionary of estimators grouped by type
    """
    estimators_by_type = {}
    
    for name, info in ESTIMATOR_MAPPING.items():
        estimator_type = info["type"]
        if estimator_type not in estimators_by_type:
            estimators_by_type[estimator_type] = {}
        
        estimators_by_type[estimator_type][name] = {
            "description": info["description"],
            "class": info["class"],
            "module": info["module"],
            "metrics": info["metrics"]
        }
    
    return estimators_by_type


def validate_estimator_parameters(estimator_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate parameters for a specific estimator.
    
    Args:
        estimator_name: Name of the estimator
        parameters: Dictionary of parameters to validate
        
    Returns:
        Validation result dictionary
    """
    try:
        if estimator_name not in ESTIMATOR_MAPPING:
            return {
                "valid": False,
                "error": f"Estimator '{estimator_name}' not found"
            }
        
        mapping = ESTIMATOR_MAPPING[estimator_name]
        module = importlib.import_module(mapping["module"])
        estimator_class = getattr(module, mapping["class"])
        
        # Get the signature
        sig = inspect.signature(estimator_class.__init__)
        
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check if all parameters are valid
        for param_name, param_value in parameters.items():
            if param_name not in sig.parameters:
                validation_result["warnings"].append(f"Unknown parameter: {param_name}")
        
        # Check for required parameters
        for param_name, param in sig.parameters.items():
            if param_name != 'self' and param.default == inspect.Parameter.empty:
                if param_name not in parameters:
                    validation_result["errors"].append(f"Missing required parameter: {param_name}")
                    validation_result["valid"] = False
        
        return validation_result
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation failed: {str(e)}"
        }


def create_langgraph_tool(estimator_name: str) -> Dict[str, Any]:
    """
    Create a LangGraph tool definition for a specific estimator.
    
    Args:
        estimator_name: Name of the estimator
        
    Returns:
        Dictionary containing LangGraph tool definition
    """
    info = extract_estimator_info(estimator_name)
    if "error" in info:
        return {"error": info["error"]}
    
    # Create parameter schema
    parameters = {
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "description": "Path to the CSV file containing the data"
            },
            "target_column": {
                "type": "string",
                "description": "Name of the target column (required for classification/regression)"
            },
            "test_size": {
                "type": "number",
                "description": "Fraction of data to use for testing",
                "default": 0.2
            },
            "random_state": {
                "type": "integer",
                "description": "Random state for reproducibility",
                "default": 42
            }
        },
        "required": ["data"]
    }
    
    # Add estimator-specific parameters
    for param_name, param_info in info["parameter_defaults"].items():
        if param_name not in ["data", "target_column", "test_size", "random_state"]:
            param_type = "number" if param_info != "Required" else "string"
            parameters["properties"][param_name] = {
                "type": param_type,
                "description": info["parameters"].get(param_name, f"Parameter {param_name}"),
                "default": param_info if param_info != "Required" else None
            }
            if param_info == "Required":
                parameters["required"].append(param_name)
    
    return {
        "name": f"train_{estimator_name}",
        "description": get_estimator_tool_description(estimator_name),
        "parameters": parameters
    }


# Example usage and testing functions
def example_usage():
    """Example usage of the universal estimator."""
    import pandas as pd
    import numpy as np
    from sklearn.datasets import load_iris, load_diabetes, load_wine
    
    # Use scikit-learn datasets instead of synthetic data
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
    result1 = universal_estimator(
        estimator_name="random_forest_classifier",
        data=data_clf,
        target_column="target",
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    print(f"Success: {result1['success']}")
    if result1['success']:
        print(f"Metrics: {result1['metrics']}")
    
    # Example 2: Train a Linear Regression (with regression data)
    print("\n=== Training Linear Regression ===")
    result2 = universal_estimator(
        estimator_name="linear_regression",
        data=data_reg,
        target_column="target"
    )
    print(f"Success: {result2['success']}")
    if result2['success']:
        print(f"Metrics: {result2['metrics']}")
    
    # Example 3: Perform K-Means Clustering
    print("\n=== Performing K-Means Clustering ===")
    result3 = universal_estimator(
        estimator_name="kmeans",
        data=data_cluster,
        target_column=None,  # Not needed for clustering
        n_clusters=3,
        random_state=42
    )
    print(f"Success: {result3['success']}")
    if result3['success']:
        print(f"Number of clusters: {result3['n_clusters']}")
        print(f"Metrics: {result3['metrics']}")


if __name__ == "__main__":
    # Print available estimators
    print("Available estimators:")
    estimators = get_available_estimators()
    for estimator_type, type_estimators in estimators.items():
        print(f"\n{estimator_type.upper()}:")
        for name, info in type_estimators.items():
            print(f"  - {name}: {info['description']}")
    
    # Run example usage
    print("\n" + "="*50)
    example_usage()
