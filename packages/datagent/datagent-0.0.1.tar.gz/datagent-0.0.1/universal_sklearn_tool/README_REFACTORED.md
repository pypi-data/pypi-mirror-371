# Universal Scikit-learn Tools - Refactored Version

This is the refactored version of the Universal Scikit-learn Tools, following the same modular architecture as the statsmodels tool. The code has been split into specialized modules for better maintainability and extensibility.

## Architecture Overview

The refactored version consists of the following structure:

```
universal_sklearn_tool/
├── algos/
│   ├── __init__.py
│   ├── base_model.py          # Base class with common functionality
│   ├── classification.py      # Classification models
│   ├── regression.py          # Regression models
│   ├── clustering.py          # Clustering models
│   └── preprocessing.py       # Preprocessing models
├── universal_estimator_refactored.py  # Main interface
└── universal_estimator.py     # Original version (for comparison)
```

## Key Components

### 1. Base Model (`algos/base_model.py`)

The `BaseSklearnModel` class provides common functionality that all specialized modules inherit from:

- Model mapping and validation
- Parameter extraction and validation
- Tool description generation
- LangGraph tool creation
- Data validation and cleaning
- Common utility methods

### 2. Specialized Modules

Each specialized module inherits from `BaseSklearnModel` and implements specific functionality:

#### Classification Models (`algos/classification.py`)
- Linear models (Logistic Regression, SGD Classifier)
- Tree-based models (Decision Tree, Random Forest, Gradient Boosting)
- Support Vector Machines
- Neural Networks
- Naive Bayes
- Discriminant Analysis
- Gaussian Processes
- Nearest Neighbors

#### Regression Models (`algos/regression.py`)
- Linear models (Linear Regression, Ridge, Lasso, Elastic Net)
- Tree-based models (Decision Tree, Random Forest, Gradient Boosting)
- Support Vector Regression
- Neural Networks
- Gaussian Processes
- Isotonic Regression
- Nearest Neighbors

#### Clustering Models (`algos/clustering.py`)
- K-Means clustering
- DBSCAN clustering
- Agglomerative clustering
- Spectral clustering
- Mean shift clustering
- OPTICS clustering

#### Preprocessing Models (`algos/preprocessing.py`)
- Dimensionality reduction (PCA, TruncatedSVD, Factor Analysis, FastICA)
- Feature selection (SelectKBest, SelectPercentile, RFE, RFECV)

### 3. Main Interface (`universal_estimator_refactored.py`)

The `UniversalSklearnEstimator` class provides a unified interface that:

- Automatically routes requests to appropriate specialized modules
- Combines all model mappings and available models
- Provides backward compatibility with the original interface
- Offers additional utility methods for model discovery and search

## Usage Examples

### Basic Usage

```python
from universal_sklearn_tool.universal_estimator_refactored import UniversalSklearnEstimator
import pandas as pd

# Create estimator instance
estimator = UniversalSklearnEstimator()

# Train a classification model
result = estimator.fit_model(
    "classification_random_forest_classifier",
    data,
    target_column="target",
    n_estimators=100,
    max_depth=10
)

# Train a regression model
result = estimator.fit_model(
    "regression_linear_regression",
    data,
    target_column="target"
)

# Perform clustering
result = estimator.fit_model(
    "clustering_kmeans",
    data,
    n_clusters=3
)

# Apply preprocessing
result = estimator.fit_model(
    "preprocessing_pca",
    data,
    n_components=3
)
```

### Backward Compatibility

The refactored version maintains backward compatibility with the original interface:

```python
from universal_sklearn_tool.universal_estimator_refactored import universal_estimator

# This works exactly like the original
result = universal_estimator(
    "random_forest_classifier",
    data,
    target_column="target",
    n_estimators=100
)
```

### Model Discovery

```python
# Get all available models
models = estimator.get_available_models()

# Get models by type
classification_models = estimator.get_models_by_type("classification")
regression_models = estimator.get_models_by_type("regression")

# Search for models
matching_models = estimator.search_models("random forest")

# Get all model names
all_names = estimator.get_all_model_names()
```

### Model Information

```python
# Get detailed model information
info = estimator.get_model_info("classification_random_forest_classifier")

# Get tool description for LangGraph
description = estimator.get_model_tool_description("classification_random_forest_classifier")

# Validate parameters
validation = estimator.validate_model_parameters(
    "classification_random_forest_classifier",
    {"n_estimators": 100, "max_depth": 10}
)

# Create LangGraph tool definition
tool_def = estimator.create_langgraph_tool("classification_random_forest_classifier")
```

## Model Naming Convention

The refactored version uses a consistent naming convention:

- `classification_*` - Classification models
- `regression_*` - Regression models  
- `clustering_*` - Clustering models
- `preprocessing_*` - Preprocessing models

Examples:
- `classification_random_forest_classifier`
- `regression_linear_regression`
- `clustering_kmeans`
- `preprocessing_pca`

## Benefits of the Refactored Architecture

1. **Modularity**: Each algorithm type is in its own module, making the code easier to maintain and extend.

2. **Reusability**: Common functionality is shared through the base class, reducing code duplication.

3. **Extensibility**: New algorithm types can be easily added by creating new modules that inherit from the base class.

4. **Consistency**: Follows the same pattern as the statsmodels tool, providing a consistent architecture across the project.

5. **Backward Compatibility**: The original interface is preserved, so existing code continues to work.

6. **Better Organization**: Related functionality is grouped together, making the codebase easier to navigate and understand.

## Adding New Models

To add new models to a specific category:

1. Add the model configuration to the `_get_model_mapping()` method in the appropriate module
2. Add the model to the `_get_available_models()` method
3. The model will automatically be available through the main interface

To add a new algorithm category:

1. Create a new module in the `algos/` directory
2. Inherit from `BaseSklearnModel`
3. Implement the required abstract methods
4. Add the new module to the main interface in `universal_estimator_refactored.py`

## Testing

The refactored version includes comprehensive example usage in the `example_usage()` function, demonstrating how to use all major algorithm types.

Run the examples:
```python
python universal_estimator_refactored.py
```

This will print all available models and run example training sessions for different algorithm types.
