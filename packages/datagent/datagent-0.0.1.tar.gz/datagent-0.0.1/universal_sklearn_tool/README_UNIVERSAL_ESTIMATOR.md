# Universal Scikit-learn Estimator Module

This module provides a comprehensive template function that can handle all scikit-learn estimators through a unified interface, making it suitable for use with LLMs in LangGraph.

## Features

- **Universal Interface**: Single function to train any scikit-learn estimator
- **Automatic Preprocessing**: Handles categorical variables, missing values, and scaling
- **Comprehensive Metrics**: Calculates appropriate metrics for each estimator type
- **LangGraph Integration**: Ready-to-use tool definitions for LangGraph agents
- **Parameter Validation**: Validates estimator parameters before training
- **Error Handling**: Robust error handling with informative messages

## Supported Estimator Types

### Classification
- Linear Models: Logistic Regression, SGD Classifier
- Tree-based: Decision Tree, Random Forest, Gradient Boosting, Extra Trees, AdaBoost
- Support Vector Machines: SVC, LinearSVC
- Nearest Neighbors: KNN, Radius Neighbors
- Neural Networks: MLP Classifier
- Naive Bayes: Gaussian, Multinomial, Bernoulli, Complement
- Discriminant Analysis: LDA, QDA
- Gaussian Processes: Gaussian Process Classifier

### Regression
- Linear Models: Linear Regression, Ridge, Lasso, Elastic Net, SGD Regressor
- Tree-based: Decision Tree, Random Forest, Gradient Boosting, Extra Trees, AdaBoost
- Support Vector Machines: SVR, LinearSVR
- Nearest Neighbors: KNN, Radius Neighbors
- Neural Networks: MLP Regressor
- Gaussian Processes: Gaussian Process Regressor
- Isotonic Regression

### Clustering
- K-Means
- DBSCAN
- Agglomerative Clustering
- Spectral Clustering
- Mean Shift
- OPTICS

### Dimensionality Reduction & Feature Selection
- PCA
- Truncated SVD
- Factor Analysis
- Fast ICA
- Select K Best
- Select Percentile
- Recursive Feature Elimination (RFE, RFECV)

## Quick Start

### Basic Usage

```python
from universal_estimator import universal_estimator
import pandas as pd

# Load your data
data = pd.read_csv("your_data.csv")

# Train a Random Forest Classifier
result = universal_estimator(
    estimator_name="random_forest_classifier",
    data=data,
    target_column="target",
    n_estimators=100,
    max_depth=10,
    random_state=42
)

if result['success']:
    print(f"Accuracy: {result['metrics']['accuracy']}")
    print(f"Feature importance: {result['feature_importance']}")
else:
    print(f"Error: {result['error']}")
```

### Classification Example

```python
# Train a Support Vector Classifier
result = universal_estimator(
    estimator_name="svc",
    data=data,
    target_column="target",
    C=1.0,
    kernel="rbf",
    random_state=42
)
```

### Regression Example

```python
# Train a Linear Regression
result = universal_estimator(
    estimator_name="linear_regression",
    data=data,
    target_column="price"
)
```

### Clustering Example

```python
# Perform K-Means Clustering
result = universal_estimator(
    estimator_name="kmeans",
    data=data.drop(columns=['target']),  # No target needed for clustering
    target_column=None,
    n_clusters=3,
    random_state=42
)
```

### Dimensionality Reduction Example

```python
# Apply PCA
result = universal_estimator(
    estimator_name="pca",
    data=data.drop(columns=['target']),
    target_column=None,
    n_components=2
)
```

## API Reference

### Main Function

#### `universal_estimator(estimator_name, data, target_column=None, test_size=0.2, random_state=42, **estimator_params)`

Universal function to train any scikit-learn estimator.

**Parameters:**
- `estimator_name` (str): Name of the estimator from ESTIMATOR_MAPPING
- `data` (pd.DataFrame): Input DataFrame
- `target_column` (str, optional): Name of the target column (not needed for clustering/preprocessing)
- `test_size` (float): Fraction of data to use for testing (for supervised learning)
- `random_state` (int): Random state for reproducibility
- `**estimator_params`: Parameters to pass to the estimator

**Returns:**
- Dictionary containing training results with keys:
  - `success` (bool): Whether training was successful
  - `estimator_name` (str): Name of the estimator used
  - `estimator_type` (str): Type of estimator (classifier/regressor/clustering/preprocessor)
  - `model`: Trained scikit-learn model
  - `predictions`/`clusters`/`transformed_data`: Model outputs
  - `metrics` (dict): Performance metrics
  - `feature_importance` (dict, optional): Feature importance scores
  - `data_shape` (dict): Information about data shapes

### Utility Functions

#### `get_available_estimators()`
Returns a dictionary of all available estimators grouped by type.

#### `extract_estimator_info(estimator_name)`
Extracts estimator description, parameters, and their descriptions from docstring.

#### `get_estimator_tool_description(estimator_name)`
Generates a comprehensive tool description for LangGraph use.

#### `validate_estimator_parameters(estimator_name, parameters)`
Validates parameters for a specific estimator.

#### `create_langgraph_tool(estimator_name)`
Creates a LangGraph tool definition for a specific estimator.

## LangGraph Integration

The module provides seamless integration with LangGraph through the `create_langgraph_tool()` function:

```python
from universal_estimator import create_langgraph_tool

# Create a LangGraph tool for Random Forest
tool_definition = create_langgraph_tool("random_forest_classifier")

# Use in your LangGraph agent
tools = [tool_definition]
```

## Automatic Preprocessing

The module automatically handles:

1. **Categorical Variables**: Label encoding for categorical features
2. **Missing Values**: Median imputation for numeric features
3. **Feature Scaling**: Standard scaling for algorithms that require it (SVM, Neural Networks)
4. **Data Splitting**: Train/test split for supervised learning
5. **Target Validation**: Ensures target column exists for supervised learning

## Metrics Calculated

### Classification Metrics
- Accuracy
- Precision (weighted)
- Recall (weighted)
- F1-score (weighted)
- ROC AUC (for binary classification with probability support)

### Regression Metrics
- Mean Squared Error (MSE)
- Mean Absolute Error (MAE)
- R-squared (R²)

### Clustering Metrics
- Silhouette Score
- Calinski-Harabasz Score
- Davies-Bouldin Score

### Dimensionality Reduction Metrics
- Explained Variance Ratio
- Cumulative Variance Ratio

## Error Handling

The module provides comprehensive error handling:

- Invalid estimator names
- Missing target columns for supervised learning
- Invalid parameter combinations
- Data preprocessing errors
- Model training failures

All errors are returned with descriptive messages to help with debugging.

## Testing

Run the test script to verify functionality:

```bash
cd agent_dev/ml_agent
python test_universal_estimator.py
```

## Example Output

```python
# Successful training
{
    'success': True,
    'estimator_name': 'random_forest_classifier',
    'estimator_type': 'classifier',
    'model': RandomForestClassifier(...),
    'predictions': [0, 1, 0, ...],
    'metrics': {
        'accuracy': 0.85,
        'precision': 0.84,
        'recall': 0.85,
        'f1': 0.84
    },
    'feature_importance': {
        'feature_0': 0.15,
        'feature_1': 0.25,
        ...
    },
    'data_shape': {
        'train': (800, 10),
        'test': (200, 10)
    }
}

# Error case
{
    'success': False,
    'error': 'Estimator "invalid_estimator" not found',
    'estimator_name': 'invalid_estimator'
}
```

## Contributing

To add new estimators:

1. Add the estimator to the `ESTIMATOR_MAPPING` dictionary
2. Include the module path, class name, type, metrics, and description
3. Test with the provided test script
4. Update this documentation

## Dependencies

- scikit-learn
- pandas
- numpy
- matplotlib (for plotting, optional)
- seaborn (for plotting, optional)

## License

This module is part of the agent_dev project and follows the same licensing terms.
