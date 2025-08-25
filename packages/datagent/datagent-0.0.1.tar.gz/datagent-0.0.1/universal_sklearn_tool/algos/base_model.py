"""
Base class for Universal Scikit-learn Tools.

This module provides a base class with common functionality that can be inherited
by specific algorithm implementations (classification, regression, clustering, preprocessing, etc.).
"""

import json
import inspect
import importlib
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
import logging
from abc import ABC, abstractmethod
from sklearn.base import BaseEstimator
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    silhouette_score, calinski_harabasz_score, davies_bouldin_score,
    roc_auc_score
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseSklearnModel(ABC):
    """
    Base class for all scikit-learn algorithm implementations.
    
    This class provides common functionality including:
    - Model mapping and validation
    - Parameter extraction and validation
    - Tool description generation
    - LangGraph tool creation
    - Common utility methods
    """
    
    def __init__(self):
        """Initialize the base class with common attributes."""
        self.model_mapping = self._get_model_mapping()
        self.available_models = self._get_available_models()
    
    @abstractmethod
    def _get_model_mapping(self) -> Dict[str, Any]:
        """Abstract method to define the model mapping for each algorithm type."""
        pass
    
    @abstractmethod
    def _get_available_models(self) -> Dict[str, Any]:
        """Abstract method to define available models for each algorithm type."""
        pass
    
    @abstractmethod
    def fit_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Abstract method to fit a specific model."""
        pass
    
    def extract_model_info(self, model_name: str) -> Dict[str, Any]:
        """Extract model description, parameters, and their descriptions from docstring."""
        try:
            if model_name not in self.model_mapping:
                return {"error": f"Model '{model_name}' not found in mapping"}
            
            mapping = self.model_mapping[model_name]
            module_name = mapping["module"]
            class_name = mapping["class"]
            
            # Import the module and get the class
            module = importlib.import_module(module_name)
            model_class = getattr(module, class_name)
            
            # Get docstring
            docstring = model_class.__doc__ or ""
            
            # Extract parameters from docstring
            parameters = {}
            if docstring:
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
                            param_name = line.split(' : ')[0].strip()
                            param_desc = line.split(' : ')[1].strip() if len(line.split(' : ')) > 1 else ""
                            current_param = param_name
                            parameters[param_name] = param_desc
                        elif line.startswith('    ') and current_param:
                            parameters[current_param] += " " + line.strip()
            
            # Get signature for default values
            sig = inspect.signature(model_class.__init__)
            param_defaults = {}
            for name, param in sig.parameters.items():
                if name != 'self':
                    if param.default != inspect.Parameter.empty:
                        param_defaults[name] = str(param.default)
                    else:
                        param_defaults[name] = "Required"
            
            return {
                "model_name": model_name,
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
            logger.error(f"Failed to extract model info for {model_name}: {str(e)}")
            return {"error": f"Failed to extract model info: {str(e)}"}
    
    def get_model_tool_description(self, model_name: str) -> str:
        """Generate a comprehensive tool description for LangGraph use."""
        info = self.extract_model_info(model_name)
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
    
    def validate_model_parameters(self, model_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters for a specific model."""
        try:
            if model_name not in self.model_mapping:
                return {
                    "valid": False,
                    "error": f"Model '{model_name}' not found"
                }
            
            mapping = self.model_mapping[model_name]
            module = importlib.import_module(mapping["module"])
            model_class = getattr(module, mapping["class"])
            
            # Get the signature
            sig = inspect.signature(model_class.__init__)
            
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
    
    def create_langgraph_tool(self, model_name: str) -> Dict[str, Any]:
        """Create a LangGraph tool definition for a specific model."""
        info = self.extract_model_info(model_name)
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
        
        # Add model-specific parameters
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
            "name": f"train_{model_name}",
            "description": self.get_model_tool_description(model_name),
            "parameters": parameters
        }
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of all available models grouped by type."""
        return self.available_models
    
    def validate_data(self, data: pd.DataFrame, target_column: str = None) -> Dict[str, Any]:
        """Common data validation method."""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check if data is empty
        if data is None or data.empty:
            validation_result["errors"].append("Data is empty or None")
            validation_result["valid"] = False
            return validation_result
        
        # Check target column
        if target_column and target_column not in data.columns:
            validation_result["errors"].append(
                f"Target column '{target_column}' not found in data columns: {list(data.columns)}"
            )
            validation_result["valid"] = False
            return validation_result  # Return early if target column is missing
        
        # Check for missing values
        if target_column and data[target_column].isnull().any():
            validation_result["warnings"].append(f"Target column '{target_column}' contains missing values")
        
        # Check for categorical variables
        categorical_columns = data.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            validation_result["warnings"].append(f"Categorical columns found: {list(categorical_columns)}")
        
        return validation_result
    
    def clean_data(self, data: pd.DataFrame, target_column: str = None) -> pd.DataFrame:
        """Common data cleaning method."""
        # Create a copy to avoid modifying original data
        data_clean = data.copy()
        
        # Determine columns to check for missing values
        columns_to_check = []
        if target_column:
            columns_to_check.append(target_column)
        
        # Drop rows with missing values in relevant columns
        if columns_to_check:
            data_clean = data_clean.dropna(subset=columns_to_check)
        
        # Log cleaning information
        if len(data_clean) < len(data):
            dropped_rows = len(data) - len(data_clean)
            logger.warning(f"Dropped {dropped_rows} rows with missing values")
        
        return data_clean
    
    def prepare_data_for_supervised_learning(self, data: pd.DataFrame, target_column: str,
                                           test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        """Prepare data for supervised learning (classification/regression)."""
        # Validate data
        validation = self.validate_data(data, target_column)
        if not validation["valid"]:
            return {"error": validation["errors"]}
        
        # Clean data
        data_clean = self.clean_data(data, target_column)
        
        # Split features and target
        X = data_clean.drop(columns=[target_column])
        y = data_clean[target_column]
        
        # Split into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Handle categorical variables
        label_encoders = {}
        if X_train.select_dtypes(include=['object']).shape[1] > 0:
            categorical_columns = X_train.select_dtypes(include=['object']).columns
            
            for col in categorical_columns:
                le = LabelEncoder()
                X_train[col] = le.fit_transform(X_train[col].astype(str))
                X_test[col] = le.transform(X_test[col].astype(str))
                label_encoders[col] = le
        
        # Handle missing values
        X_train = X_train.fillna(X_train.median())
        X_test = X_test.fillna(X_test.median())
        
        return {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "label_encoders": label_encoders,
            "data_clean": data_clean
        }
    
    def prepare_data_for_unsupervised_learning(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data for unsupervised learning (clustering/preprocessing)."""
        # Validate data
        validation = self.validate_data(data)
        if not validation["valid"]:
            return {"error": validation["errors"]}
        
        # Clean data
        data_clean = self.clean_data(data)
        
        # Handle categorical variables
        label_encoders = {}
        if data_clean.select_dtypes(include=['object']).shape[1] > 0:
            categorical_columns = data_clean.select_dtypes(include=['object']).columns
            
            for col in categorical_columns:
                le = LabelEncoder()
                data_clean[col] = le.fit_transform(data_clean[col].astype(str))
                label_encoders[col] = le
        
        # Handle missing values
        data_clean = data_clean.fillna(data_clean.median())
        
        return {
            "X": data_clean,
            "label_encoders": label_encoders,
            "data_clean": data_clean
        }
    
    def calculate_classification_metrics(self, y_true, y_pred, y_pred_proba=None) -> Dict[str, Any]:
        """Calculate classification metrics."""
        metrics = {}
        
        metrics["accuracy"] = accuracy_score(y_true, y_pred)
        metrics["precision"] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        metrics["recall"] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        metrics["f1"] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Additional classification metrics
        if y_pred_proba is not None:
            try:
                if len(np.unique(y_true)) == 2:  # Binary classification
                    metrics["roc_auc"] = roc_auc_score(y_true, y_pred_proba[:, 1])
            except:
                pass
        
        return metrics
    
    def calculate_regression_metrics(self, y_true, y_pred) -> Dict[str, Any]:
        """Calculate regression metrics."""
        metrics = {}
        
        metrics["mse"] = mean_squared_error(y_true, y_pred)
        metrics["mae"] = mean_absolute_error(y_true, y_pred)
        metrics["r2"] = r2_score(y_true, y_pred)
        
        return metrics
    
    def calculate_clustering_metrics(self, X, clusters) -> Dict[str, Any]:
        """Calculate clustering metrics."""
        metrics = {}
        
        if len(np.unique(clusters)) > 1:  # Need at least 2 clusters for metrics
            try:
                metrics["silhouette"] = silhouette_score(X, clusters)
            except:
                pass
            try:
                metrics["calinski_harabasz"] = calinski_harabasz_score(X, clusters)
            except:
                pass
            try:
                metrics["davies_bouldin"] = davies_bouldin_score(X, clusters)
            except:
                pass
        
        return metrics
    
    def get_feature_importance(self, model, feature_names) -> Optional[Dict[str, float]]:
        """Extract feature importance from model."""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            if hasattr(importances, '__iter__') and len(importances) == len(feature_names):
                return dict(zip(feature_names, importances))
        elif hasattr(model, 'coef_'):
            coef = model.coef_
            if hasattr(coef, '__iter__') and len(coef) == len(feature_names):
                return dict(zip(feature_names, coef))
        return None
    
    def create_result_dict(self, model_name: str, model, data_shape: Tuple[int, int],
                          metrics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create a standardized result dictionary."""
        result = {
            "success": True,
            "model_name": model_name,
            "model": model,
            "data_shape": data_shape,
            "metrics": metrics
        }
        
        # Add additional information
        result.update(kwargs)
        
        return result
    
    def create_error_result(self, model_name: str, error: str, **kwargs) -> Dict[str, Any]:
        """Create a standardized error result dictionary."""
        result = {
            "success": False,
            "error": error,
            "model_name": model_name
        }
        
        # Add additional information
        result.update(kwargs)
        
        return result
