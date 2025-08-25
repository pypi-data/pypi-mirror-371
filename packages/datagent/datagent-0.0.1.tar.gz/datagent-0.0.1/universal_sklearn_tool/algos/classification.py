"""
Classification Models for Universal Scikit-learn Tools.

This module provides classification model implementations including:
- Linear models (Logistic Regression, SGD Classifier)
- Tree-based models (Decision Tree, Random Forest, Gradient Boosting)
- Support Vector Machines
- Neural Networks
- Naive Bayes
- Discriminant Analysis
- Gaussian Processes
"""

import importlib
from typing import Dict, Any
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from .base_model import BaseSklearnModel


class ClassificationModels(BaseSklearnModel):
    """
    Classification models implementation.
    
    This class provides functionality for training and evaluating various
    classification models from scikit-learn.
    """
    
    def _get_model_mapping(self) -> Dict[str, Any]:
        """Define the model mapping for classification algorithms."""
        return {
            # Linear Models
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
            
            # Tree-based Models
            "decision_tree_classifier": {
                "module": "sklearn.tree",
                "class": "DecisionTreeClassifier",
                "type": "classifier",
                "metrics": ["accuracy", "precision", "recall", "f1"],
                "description": "Decision Tree classifier"
            },
            "random_forest_classifier": {
                "module": "sklearn.ensemble",
                "class": "RandomForestClassifier",
                "type": "classifier",
                "metrics": ["accuracy", "precision", "recall", "f1"],
                "description": "Random Forest classifier"
            },
            "gradient_boosting_classifier": {
                "module": "sklearn.ensemble",
                "class": "GradientBoostingClassifier",
                "type": "classifier",
                "metrics": ["accuracy", "precision", "recall", "f1"],
                "description": "Gradient Boosting classifier"
            },
            "extra_trees_classifier": {
                "module": "sklearn.ensemble",
                "class": "ExtraTreesClassifier",
                "type": "classifier",
                "metrics": ["accuracy", "precision", "recall", "f1"],
                "description": "Extra Trees classifier"
            },
            "ada_boost_classifier": {
                "module": "sklearn.ensemble",
                "class": "AdaBoostClassifier",
                "type": "classifier",
                "metrics": ["accuracy", "precision", "recall", "f1"],
                "description": "AdaBoost classifier"
            },
            
            # Support Vector Machines
            "svc": {
                "module": "sklearn.svm",
                "class": "SVC",
                "type": "classifier",
                "metrics": ["accuracy", "precision", "recall", "f1"],
                "description": "Support Vector Classification"
            },
            "linear_svc": {
                "module": "sklearn.svm",
                "class": "LinearSVC",
                "type": "classifier",
                "metrics": ["accuracy", "precision", "recall", "f1"],
                "description": "Linear Support Vector Classification"
            },
            
            # Neural Networks
            "mlp_classifier": {
                "module": "sklearn.neural_network",
                "class": "MLPClassifier",
                "type": "classifier",
                "metrics": ["accuracy", "precision", "recall", "f1"],
                "description": "Multi-layer Perceptron classifier"
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
            
            # Nearest Neighbors
            "knn_classifier": {
                "module": "sklearn.neighbors",
                "class": "KNeighborsClassifier",
                "type": "classifier",
                "metrics": ["accuracy", "precision", "recall", "f1"],
                "description": "K-Nearest Neighbors classifier"
            },
            "radius_neighbors_classifier": {
                "module": "sklearn.neighbors",
                "class": "RadiusNeighborsClassifier",
                "type": "classifier",
                "metrics": ["accuracy", "precision", "recall", "f1"],
                "description": "Radius-based neighbors classifier"
            }
        }
    
    def _get_available_models(self) -> Dict[str, Any]:
        """Define available classification models grouped by type."""
        return {
            "linear_models": {
                "logistic_regression": {
                    "description": "Logistic regression for classification",
                    "class": "LogisticRegression",
                    "module": "sklearn.linear_model",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "sgd_classifier": {
                    "description": "Stochastic Gradient Descent classifier",
                    "class": "SGDClassifier",
                    "module": "sklearn.linear_model",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                }
            },
            "tree_based": {
                "decision_tree_classifier": {
                    "description": "Decision Tree classifier",
                    "class": "DecisionTreeClassifier",
                    "module": "sklearn.tree",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "random_forest_classifier": {
                    "description": "Random Forest classifier",
                    "class": "RandomForestClassifier",
                    "module": "sklearn.ensemble",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "gradient_boosting_classifier": {
                    "description": "Gradient Boosting classifier",
                    "class": "GradientBoostingClassifier",
                    "module": "sklearn.ensemble",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "extra_trees_classifier": {
                    "description": "Extra Trees classifier",
                    "class": "ExtraTreesClassifier",
                    "module": "sklearn.ensemble",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "ada_boost_classifier": {
                    "description": "AdaBoost classifier",
                    "class": "AdaBoostClassifier",
                    "module": "sklearn.ensemble",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                }
            },
            "support_vector_machines": {
                "svc": {
                    "description": "Support Vector Classification",
                    "class": "SVC",
                    "module": "sklearn.svm",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "linear_svc": {
                    "description": "Linear Support Vector Classification",
                    "class": "LinearSVC",
                    "module": "sklearn.svm",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                }
            },
            "neural_networks": {
                "mlp_classifier": {
                    "description": "Multi-layer Perceptron classifier",
                    "class": "MLPClassifier",
                    "module": "sklearn.neural_network",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                }
            },
            "naive_bayes": {
                "gaussian_nb": {
                    "description": "Gaussian Naive Bayes classifier",
                    "class": "GaussianNB",
                    "module": "sklearn.naive_bayes",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "multinomial_nb": {
                    "description": "Multinomial Naive Bayes classifier",
                    "class": "MultinomialNB",
                    "module": "sklearn.naive_bayes",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "bernoulli_nb": {
                    "description": "Bernoulli Naive Bayes classifier",
                    "class": "BernoulliNB",
                    "module": "sklearn.naive_bayes",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "complement_nb": {
                    "description": "Complement Naive Bayes classifier",
                    "class": "ComplementNB",
                    "module": "sklearn.naive_bayes",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                }
            },
            "discriminant_analysis": {
                "lda": {
                    "description": "Linear Discriminant Analysis",
                    "class": "LinearDiscriminantAnalysis",
                    "module": "sklearn.discriminant_analysis",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "qda": {
                    "description": "Quadratic Discriminant Analysis",
                    "class": "QuadraticDiscriminantAnalysis",
                    "module": "sklearn.discriminant_analysis",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                }
            },
            "gaussian_processes": {
                "gaussian_process_classifier": {
                    "description": "Gaussian Process classifier",
                    "class": "GaussianProcessClassifier",
                    "module": "sklearn.gaussian_process",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                }
            },
            "nearest_neighbors": {
                "knn_classifier": {
                    "description": "K-Nearest Neighbors classifier",
                    "class": "KNeighborsClassifier",
                    "module": "sklearn.neighbors",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "radius_neighbors_classifier": {
                    "description": "Radius-based neighbors classifier",
                    "class": "RadiusNeighborsClassifier",
                    "module": "sklearn.neighbors",
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                }
            }
        }
    
    def fit_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Fit a classification model."""
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
                    "Target column is required for classification models"
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
            
            # Scale features for certain estimators
            if model_name in ["svc", "linear_svc", "mlp_classifier"]:
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
            
            # Get prediction probabilities if available
            y_pred_proba = None
            if hasattr(model, 'predict_proba'):
                try:
                    y_pred_proba = model.predict_proba(X_test_scaled)
                except:
                    pass
            
            # Calculate metrics
            metrics = self.calculate_classification_metrics(y_test, y_pred, y_pred_proba)
            
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
