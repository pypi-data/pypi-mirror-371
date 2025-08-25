"""
Regression Models for Universal Scikit-learn Tools.

This module provides regression model implementations including:
- Linear models (Linear Regression, Ridge, Lasso, Elastic Net)
- Tree-based models (Decision Tree, Random Forest, Gradient Boosting)
- Support Vector Regression
- Neural Networks
- Gaussian Processes
- Isotonic Regression
"""

import importlib
from typing import Dict, Any
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from .base_model import BaseSklearnModel


class RegressionModels(BaseSklearnModel):
    """
    Regression models implementation.
    
    This class provides functionality for training and evaluating various
    regression models from scikit-learn.
    """
    
    def _get_model_mapping(self) -> Dict[str, Any]:
        """Define the model mapping for regression algorithms."""
        return {
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
            "sgd_regressor": {
                "module": "sklearn.linear_model",
                "class": "SGDRegressor",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "Stochastic Gradient Descent regressor"
            },
            
            # Tree-based Models
            "decision_tree_regressor": {
                "module": "sklearn.tree",
                "class": "DecisionTreeRegressor",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "Decision Tree regressor"
            },
            "random_forest_regressor": {
                "module": "sklearn.ensemble",
                "class": "RandomForestRegressor",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "Random Forest regressor"
            },
            "gradient_boosting_regressor": {
                "module": "sklearn.ensemble",
                "class": "GradientBoostingRegressor",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "Gradient Boosting regressor"
            },
            "extra_trees_regressor": {
                "module": "sklearn.ensemble",
                "class": "ExtraTreesRegressor",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "Extra Trees regressor"
            },
            "ada_boost_regressor": {
                "module": "sklearn.ensemble",
                "class": "AdaBoostRegressor",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "AdaBoost regressor"
            },
            
            # Support Vector Regression
            "svr": {
                "module": "sklearn.svm",
                "class": "SVR",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "Support Vector Regression"
            },
            "linear_svr": {
                "module": "sklearn.svm",
                "class": "LinearSVR",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "Linear Support Vector Regression"
            },
            
            # Neural Networks
            "mlp_regressor": {
                "module": "sklearn.neural_network",
                "class": "MLPRegressor",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "Multi-layer Perceptron regressor"
            },
            
            # Gaussian Processes
            "gaussian_process_regressor": {
                "module": "sklearn.gaussian_process",
                "class": "GaussianProcessRegressor",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "Gaussian Process regressor"
            },
            
            # Nearest Neighbors
            "knn_regressor": {
                "module": "sklearn.neighbors",
                "class": "KNeighborsRegressor",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "K-Nearest Neighbors regressor"
            },
            "radius_neighbors_regressor": {
                "module": "sklearn.neighbors",
                "class": "RadiusNeighborsRegressor",
                "type": "regressor",
                "metrics": ["mse", "mae", "r2"],
                "description": "Radius-based neighbors regressor"
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
    
    def _get_available_models(self) -> Dict[str, Any]:
        """Define available regression models grouped by type."""
        return {
            "linear_models": {
                "linear_regression": {
                    "description": "Ordinary least squares Linear Regression",
                    "class": "LinearRegression",
                    "module": "sklearn.linear_model",
                    "metrics": ["mse", "mae", "r2"]
                },
                "ridge_regression": {
                    "description": "Ridge regression with L2 regularization",
                    "class": "Ridge",
                    "module": "sklearn.linear_model",
                    "metrics": ["mse", "mae", "r2"]
                },
                "lasso_regression": {
                    "description": "Lasso regression with L1 regularization",
                    "class": "Lasso",
                    "module": "sklearn.linear_model",
                    "metrics": ["mse", "mae", "r2"]
                },
                "elastic_net": {
                    "description": "Elastic Net regression with L1 and L2 regularization",
                    "class": "ElasticNet",
                    "module": "sklearn.linear_model",
                    "metrics": ["mse", "mae", "r2"]
                },
                "sgd_regressor": {
                    "description": "Stochastic Gradient Descent regressor",
                    "class": "SGDRegressor",
                    "module": "sklearn.linear_model",
                    "metrics": ["mse", "mae", "r2"]
                }
            },
            "tree_based": {
                "decision_tree_regressor": {
                    "description": "Decision Tree regressor",
                    "class": "DecisionTreeRegressor",
                    "module": "sklearn.tree",
                    "metrics": ["mse", "mae", "r2"]
                },
                "random_forest_regressor": {
                    "description": "Random Forest regressor",
                    "class": "RandomForestRegressor",
                    "module": "sklearn.ensemble",
                    "metrics": ["mse", "mae", "r2"]
                },
                "gradient_boosting_regressor": {
                    "description": "Gradient Boosting regressor",
                    "class": "GradientBoostingRegressor",
                    "module": "sklearn.ensemble",
                    "metrics": ["mse", "mae", "r2"]
                },
                "extra_trees_regressor": {
                    "description": "Extra Trees regressor",
                    "class": "ExtraTreesRegressor",
                    "module": "sklearn.ensemble",
                    "metrics": ["mse", "mae", "r2"]
                },
                "ada_boost_regressor": {
                    "description": "AdaBoost regressor",
                    "class": "AdaBoostRegressor",
                    "module": "sklearn.ensemble",
                    "metrics": ["mse", "mae", "r2"]
                }
            },
            "support_vector_regression": {
                "svr": {
                    "description": "Support Vector Regression",
                    "class": "SVR",
                    "module": "sklearn.svm",
                    "metrics": ["mse", "mae", "r2"]
                },
                "linear_svr": {
                    "description": "Linear Support Vector Regression",
                    "class": "LinearSVR",
                    "module": "sklearn.svm",
                    "metrics": ["mse", "mae", "r2"]
                }
            },
            "neural_networks": {
                "mlp_regressor": {
                    "description": "Multi-layer Perceptron regressor",
                    "class": "MLPRegressor",
                    "module": "sklearn.neural_network",
                    "metrics": ["mse", "mae", "r2"]
                }
            },
            "gaussian_processes": {
                "gaussian_process_regressor": {
                    "description": "Gaussian Process regressor",
                    "class": "GaussianProcessRegressor",
                    "module": "sklearn.gaussian_process",
                    "metrics": ["mse", "mae", "r2"]
                }
            },
            "nearest_neighbors": {
                "knn_regressor": {
                    "description": "K-Nearest Neighbors regressor",
                    "class": "KNeighborsRegressor",
                    "module": "sklearn.neighbors",
                    "metrics": ["mse", "mae", "r2"]
                },
                "radius_neighbors_regressor": {
                    "description": "Radius-based neighbors regressor",
                    "class": "RadiusNeighborsRegressor",
                    "module": "sklearn.neighbors",
                    "metrics": ["mse", "mae", "r2"]
                }
            },
            "other": {
                "isotonic_regression": {
                    "description": "Isotonic regression",
                    "class": "IsotonicRegression",
                    "module": "sklearn.isotonic",
                    "metrics": ["mse", "mae", "r2"]
                }
            }
        }
    
    def fit_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Fit a regression model."""
        try:
            # Validate model name
            if model_name not in self.model_mapping:
                return self.create_error_result(
                    model_name,
                    f"Model '{model_name}' not found. Available models: {list(self.model_mapping.keys())}"
                )
            
            # Extract parameters
            target_column = kwargs.get('target_column')
            test_size = kwargs.get('test_size', 0.2)
            random_state = kwargs.get('random_state', 42)
            
            # Remove non-model parameters
            model_params = {k: v for k, v in kwargs.items() 
                          if k not in ['target_column', 'test_size', 'random_state']}
            
            # Validate target column
            if target_column is None:
                return self.create_error_result(
                    model_name,
                    "Target column is required for regression models"
                )
            
            # Prepare data
            data_prep = self.prepare_data_for_supervised_learning(
                data, target_column, test_size, random_state
            )
            
            if "error" in data_prep:
                return self.create_error_result(model_name, data_prep["error"])
            
            X_train = data_prep["X_train"]
            X_test = data_prep["X_test"]
            y_train = data_prep["y_train"]
            y_test = data_prep["y_test"]
            
            # Handle special cases
            if model_name == "isotonic_regression":
                # IsotonicRegression expects 1D input or 2D with 1 feature
                # Use only the first feature and ensure no NaN values
                X_train_scaled = X_train.iloc[:, 0].values
                X_test_scaled = X_test.iloc[:, 0].values
                y_train_orig = y_train.values if hasattr(y_train, 'values') else y_train
                y_test_orig = y_test.values if hasattr(y_test, 'values') else y_test
                
                # Debug: Check for NaN values
                print(f"X_train NaN count: {np.isnan(X_train_scaled).sum()}")
                print(f"X_test NaN count: {np.isnan(X_test_scaled).sum()}")
                print(f"y_train NaN count: {np.isnan(y_train_orig).sum()}")
                print(f"y_test NaN count: {np.isnan(y_test_orig).sum()}")
                
                # Remove any NaN values from both X and y
                mask_train = ~(np.isnan(X_train_scaled) | np.isnan(y_train_orig))
                mask_test = ~(np.isnan(X_test_scaled) | np.isnan(y_test_orig))
                
                X_train_scaled = X_train_scaled[mask_train]
                X_test_scaled = X_test_scaled[mask_test]
                y_train = y_train_orig[mask_train]
                y_test = y_test_orig[mask_test]
                
                # Ensure we have enough data
                if len(X_train_scaled) < 2:
                    return self.create_error_result(
                        model_name,
                        "Not enough valid data points for isotonic regression after removing NaN values"
                    )
            elif model_name in ["svr", "linear_svr", "mlp_regressor"]:
                # Scale features for certain estimators
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
            else:
                X_train_scaled = X_train
                X_test_scaled = X_test
            
            # Import and instantiate model
            mapping = self.model_mapping[model_name]
            module = importlib.import_module(mapping["module"])
            model_class = getattr(module, mapping["class"])
            model = model_class(**model_params)
            
            # Train the model
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            metrics = self.calculate_regression_metrics(y_test, y_pred)
            
            # Get feature importance
            feature_importance = self.get_feature_importance(model, X_train.columns)
            
            return self.create_result_dict(
                model_name=model_name,
                model=model,
                data_shape=(X_train.shape, X_test.shape),
                metrics=metrics,
                predictions=y_pred.tolist() if hasattr(y_pred, 'tolist') else y_pred,
                feature_importance=feature_importance,
                label_encoders=data_prep["label_encoders"]
            )
            
        except Exception as e:
            return self.create_error_result(model_name, f"Failed to train {model_name}: {str(e)}")
