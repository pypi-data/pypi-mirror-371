# Implementation Blueprint: Universal Statsmodels Tool

## 📋 **Updated Architecture Overview**

This document provides a comprehensive blueprint for implementing universal tools for statsmodels algorithms, based on the successful modular implementation with separate algorithm modules in the `algos/` directory.

## 🏗️ **Current Project Structure**

```
universal_statsmodels_tool/
├── __init__.py                           # Package initialization with imports
├── algos/                                # Algorithm modules directory
│   ├── __init__.py                       # Algos package initialization
│   ├── linear_models.py                  # Linear regression models (7 models)
│   └── glm.py                           # Generalized Linear Models (10 models)
├── tests/                                # Testing directory
│   ├── __init__.py                       # Tests package initialization
│   ├── test_linear_models.py             # Linear models test suite
│   ├── test_glm.py                      # GLM test suite
│   ├── run_tests.py                     # Unified test runner
│   └── README.md                        # Testing documentation
├── requirements.txt                      # Dependencies
├── langgraph_integration_example.py     # LangGraph integration demo
├── LANGGRAPH_USAGE_README.md            # LangGraph usage documentation

└── IMPLEMENTATION_BLUEPRINT.md          # This document
```

## 🎯 **Successfully Implemented**

### **Linear Models Module** (`algos/linear_models.py`)
- ✅ **7 Linear Regression Models**:
  - OLS (Ordinary Least Squares)
  - GLS (Generalized Least Squares)
  - WLS (Weighted Least Squares)
  - Quantile Regression
  - Recursive Least Squares
  - Rolling Regression
  - Mixed Linear Model

### **GLM Module** (`algos/glm.py`)
- ✅ **10 GLM Models**:
  - **GLM Families**: Gaussian, Binomial, Poisson, Gamma, Inverse Gaussian, Negative Binomial, Tweedie
  - **Discrete Choice**: Logit, Probit, Multinomial Logit, Ordered Logit
- ✅ **10 Link Functions**: identity, log, logit, probit, cloglog, loglog, cauchy, inverse_power, inverse_squared, power

## 🔧 **Implementation Pattern for New Algorithms**

### **Step 1: Create Algorithm Module**

Create a new file in the `algos/` directory following this template:

```python
"""
Universal [Algorithm Category] Tool for LangGraph Agent.

This module provides a comprehensive template function that can handle all statsmodels
[algorithm category] through a unified interface, making it suitable for use with LLMs in LangGraph.
"""

import json
import inspect
import importlib
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive mapping of statsmodels [algorithm category] models
[ALGORITHM_CATEGORY]_MAPPING = {
    "model_name": {
        "module": "statsmodels.module.path",
        "class": "ModelClass",
        "type": "algorithm_type",
        "metrics": ["metric1", "metric2", "metric3"],
        "description": "Model description",
        "formula_required": False,  # or True
        "default_params": {}  # Optional: default parameters
    }
}

# Required functions to implement:
def extract_model_info(model_name: str) -> Dict[str, Any]:
    """Extract model description, parameters, and their descriptions from docstring."""
    pass

def get_model_tool_description(model_name: str) -> str:
    """Generate a comprehensive tool description for LangGraph use."""
    pass

def universal_[algorithm_category](
    model_name: str,
    data: pd.DataFrame,
    dependent_var: str,
    independent_vars: List[str] = None,
    formula: str = None,
    **model_params
) -> Dict[str, Any]:
    """Universal function to fit any statsmodels [algorithm category] model."""
    pass

def get_available_models() -> Dict[str, Any]:
    """Get list of all available models grouped by type."""
    pass

def validate_model_parameters(model_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Validate parameters for a specific model."""
    pass

def create_langgraph_tool(model_name: str) -> Dict[str, Any]:
    """Create a LangGraph tool definition for a specific model."""
    pass

def example_usage():
    """Example usage of the universal [algorithm category] function."""
    pass

if __name__ == "__main__":
    # Print available models and run examples
    pass
```

### **Step 2: Update Package Initialization**

Add imports to `__init__.py`:

```python
# Add new imports
from .algos.[algorithm_module] import (
    universal_[algorithm_category],
    extract_model_info as extract_[algorithm_category]_info,
    get_model_tool_description as get_[algorithm_category]_tool_description,
    create_langgraph_tool as create_[algorithm_category]_langgraph_tool,
    get_available_models as get_[algorithm_category]_available_models,
    validate_model_parameters as validate_[algorithm_category]_parameters
)

# Add to __all__ list
__all__ = [
    # ... existing exports ...
    # [Algorithm Category] models
    "universal_[algorithm_category]",
    "extract_[algorithm_category]_info", 
    "get_[algorithm_category]_tool_description",
    "create_[algorithm_category]_langgraph_tool",
    "get_[algorithm_category]_available_models",
    "validate_[algorithm_category]_parameters"
]
```

### **Step 3: Create Test Module**

Create a new test file in the `tests/` directory:

```python
"""
Comprehensive test suite for [Algorithm Category] models.

This module provides unit tests, real dataset tests, and edge case tests
for all [algorithm category] models in the universal statsmodels tool.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algos.[algorithm_module] import (
    universal_[algorithm_category],
    get_available_models,
    extract_model_info,
    validate_model_parameters
)

class Test[AlgorithmCategory]Unit(unittest.TestCase):
    """Unit tests for [algorithm category] models with synthetic data."""
    
    def setUp(self):
        """Set up test data with real datasets from statsmodels."""
        # Try to load real datasets from statsmodels first
        self.real_datasets = {}
        self.synthetic_data = None
        
        try:
            import statsmodels.api as sm
            
            # Load commonly available datasets for different model types
            available_datasets = [
                ('longley', 'TOTEMP', ['GNPDEFL', 'GNP', 'UNEMP']),
                ('engel', 'foodexp', ['income']),
                ('grunfeld', 'invest', ['value', 'capital']),
                ('scotland', 'YES', ['COUTAX', 'UNEMPF', 'MOR', 'ACT', 'GDP', 'AGE', 'COUTAX_FEMALEUNEMPF', 'MOR_FEMALE', 'ACT_FEMALE', 'GDP_FEMALE', 'AGE_FEMALE', 'COUTAX_MALE', 'UNEMPF_MALE', 'MOR_MALE', 'ACT_MALE', 'GDP_MALE', 'AGE_MALE']),
                ('star98', 'NABOVE', ['NABOVE', 'NBELOW', 'SIZE', 'URBAN', 'SCHOOL', 'SEX', 'PRACAD', 'DISCLIM', 'URBAN_NABOVE', 'SCHOOL_NABOVE', 'SEX_NABOVE', 'PRACAD_NABOVE', 'DISCLIM_NABOVE', 'URBAN_NBELOW', 'SCHOOL_NBELOW', 'SEX_NBELOW', 'PRACAD_NBELOW', 'DISCLIM_NBELOW', 'URBAN_SIZE', 'SCHOOL_SIZE', 'SEX_SIZE', 'PRACAD_SIZE', 'DISCLIM_SIZE', 'URBAN_URBAN', 'SCHOOL_URBAN', 'SEX_URBAN', 'PRACAD_URBAN', 'DISCLIM_URBAN', 'SCHOOL_SCHOOL', 'SEX_SCHOOL', 'PRACAD_SCHOOL', 'DISCLIM_SCHOOL', 'SEX_SEX', 'PRACAD_SEX', 'DISCLIM_SEX', 'PRACAD_PRACAD', 'DISCLIM_PRACAD', 'DISCLIM_DISCLIM']),
                ('fair', 'affairs', ['rate_marriage', 'age', 'yrs_married', 'children', 'religious', 'educ', 'occupation', 'occupation_husb']),
                ('copper', 'WORLDCONSUMPTION', ['WORLDPRODUCTION', 'LCOPPERPRICE', 'LCOPPERPRICE_1', 'LCOPPERPRICE_2', 'LCOPPERPRICE_3', 'LCOPPERPRICE_4', 'LCOPPERPRICE_5', 'LCOPPERPRICE_6', 'LCOPPERPRICE_7', 'LCOPPERPRICE_8', 'LCOPPERPRICE_9', 'LCOPPERPRICE_10', 'LCOPPERPRICE_11', 'LCOPPERPRICE_12', 'LCOPPERPRICE_13', 'LCOPPERPRICE_14', 'LCOPPERPRICE_15', 'LCOPPERPRICE_16', 'LCOPPERPRICE_17', 'LCOPPERPRICE_18', 'LCOPPERPRICE_19', 'LCOPPERPRICE_20', 'LCOPPERPRICE_21', 'LCOPPERPRICE_22', 'LCOPPERPRICE_23', 'LCOPPERPRICE_24']),
                ('nile', 'volume', []),  # Time series data
                ('sunspots', 'sunspots', [])  # Time series data
            ]
            
            for dataset_name, dep_var, indep_vars in available_datasets:
                try:
                    dataset = getattr(sm.datasets, dataset_name).load_pandas()
                    self.real_datasets[dataset_name] = {
                        'data': dataset.data,
                        'dependent_var': dep_var,
                        'independent_vars': indep_vars if indep_vars else [col for col in dataset.data.columns if col != dep_var]
                    }
                except (AttributeError, Exception) as e:
                    # Skip datasets that are not available
                    continue
            
            if not self.real_datasets:
                raise ImportError("No real datasets available from statsmodels")
                
        except ImportError as e:
            # Fallback to synthetic data with warning
            import warnings
            warnings.warn(f"statsmodels not available, using synthetic data for testing: {str(e)}")
            
            np.random.seed(42)
            self.n_samples = 1000
            
            # Generate synthetic data as fallback
            self.x1 = np.random.randn(self.n_samples)
            self.x2 = np.random.randn(self.n_samples)
            self.x3 = np.random.randn(self.n_samples)
            
            # Create different types of dependent variables
            self.y_continuous = 2 + 1.5 * self.x1 + 0.8 * self.x2 - 0.3 * self.x3 + np.random.randn(self.n_samples) * 0.5
            self.y_binary = (self.y_continuous > np.mean(self.y_continuous)).astype(int)
            self.y_count = np.random.poisson(np.exp(0.5 + 0.8 * self.x1 + 0.3 * self.x2))
            
            # Create DataFrame
            self.synthetic_data = pd.DataFrame({
                'y_continuous': self.y_continuous,
                'y_binary': self.y_binary,
                'y_count': self.y_count,
                'x1': self.x1,
                'x2': self.x2,
                'x3': self.x3
            })
    
    def test_available_models(self):
        """Test that all models are available."""
        models = get_available_models()
        self.assertIsInstance(models, dict)
        self.assertGreater(len(models), 0)
        
        # Test specific models
        for model_type, type_models in models.items():
            self.assertIsInstance(type_models, dict)
            for model_name, model_info in type_models.items():
                self.assertIn('description', model_info)
                self.assertIn('class', model_info)
                self.assertIn('module', model_info)
    
    def test_model_info_extraction(self):
        """Test model info extraction for all models."""
        models = get_available_models()
        for model_type, type_models in models.items():
            for model_name in type_models.keys():
                info = extract_model_info(model_name)
                self.assertNotIn('error', info)
                self.assertIn('model_name', info)
                self.assertIn('description', info)
    
    # Add specific model tests here
    def test_[specific_model_name](self):
        """Test [specific model] with real datasets from statsmodels."""
        if not self.real_datasets:
            self.skipTest("No real datasets available, skipping test")
        
        # Test with appropriate real dataset
        for dataset_name, dataset_info in self.real_datasets.items():
            # Skip if dataset is not suitable for this model
            if self._should_skip_model("[specific_model_name]", dataset_info['data'], dataset_info['dependent_var']):
                continue
                
            result = universal_[algorithm_category](
                model_name="[specific_model_name]",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars']
            )
            
            self.assertTrue(result['success'], 
                          f"Failed to fit {[specific_model_name]} on {dataset_name}: {result.get('error', 'Unknown error')}")
            self.assertIn('metrics', result)
            self.assertIn('fitted_model', result)
            # Add model-specific assertions
            break  # Test with first suitable dataset

class Test[AlgorithmCategory]RealDatasets(unittest.TestCase):
    """Real dataset tests for [algorithm category] models."""
    
    def test_with_real_datasets(self, real_datasets):
        """Test all models with real datasets from statsmodels."""
        if not real_datasets:
            self.skipTest("No real datasets available from statsmodels")
        
        models = get_available_models()
        
        for dataset_name, dataset_info in real_datasets.items():
            data = dataset_info['data']
            dependent_var = dataset_info['dependent_var']
            independent_vars = dataset_info['independent_vars']
            
            for model_type, type_models in models.items():
                for model_name in type_models.keys():
                    # Skip models that require specific data types
                    if self._should_skip_model(model_name, data, dependent_var):
                        continue
                    
                    try:
                        result = universal_[algorithm_category](
                            model_name=model_name,
                            data=data,
                            dependent_var=dependent_var,
                            independent_vars=independent_vars
                        )
                        
                        self.assertTrue(result['success'], 
                                      f"Failed to fit {model_name} on {dataset_name}: {result.get('error', 'Unknown error')}")
                        
                        # Validate metrics
                        if 'metrics' in result:
                            metrics = result['metrics']
                            # Add metric-specific validations
                            
                    except Exception as e:
                        self.fail(f"Exception fitting {model_name} on {dataset_name}: {str(e)}")
    
    def _should_skip_model(self, model_name, data, dependent_var):
        """Determine if a model should be skipped for a given dataset."""
        # Implement logic to skip incompatible models
        return False

class Test[AlgorithmCategory]EdgeCases(unittest.TestCase):
    """Edge case tests for [algorithm category] models."""
    
    def test_invalid_model_name(self):
        """Test handling of invalid model names."""
        result = universal_[algorithm_category](
            model_name="invalid_model",
            data=pd.DataFrame({'y': [1, 2, 3], 'x': [1, 2, 3]}),
            dependent_var="y",
            independent_vars=["x"]
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_missing_variables(self):
        """Test handling of missing variables."""
        data = pd.DataFrame({'y': [1, 2, 3], 'x1': [1, 2, 3]})
        
        # Test missing dependent variable
        result = universal_[algorithm_category](
            model_name="[first_model_name]",
            data=data,
            dependent_var="missing_y",
            independent_vars=["x1"]
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        
        # Test missing independent variables
        result = universal_[algorithm_category](
            model_name="[first_model_name]",
            data=data,
            dependent_var="y",
            independent_vars=["missing_x"]
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_empty_data(self):
        """Test handling of empty data."""
        empty_data = pd.DataFrame()
        
        result = universal_[algorithm_category](
            model_name="[first_model_name]",
            data=empty_data,
            dependent_var="y",
            independent_vars=["x"]
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()
```

### **Step 4: Update Test Runner**

Add the new test classes to `tests/run_tests.py`:

```python
# Add import for new test module
from test_[algorithm_module] import Test[AlgorithmCategory]Unit, Test[AlgorithmCategory]RealDatasets, Test[AlgorithmCategory]EdgeCases

# Add to test_classes list
test_classes = [
    # ... existing test classes ...
    Test[AlgorithmCategory]Unit,
    Test[AlgorithmCategory]RealDatasets,
    Test[AlgorithmCategory]EdgeCases
]
```

## 📊 **Algorithm Categories to Implement**

### **1. Time Series Models** (`algos/time_series.py`)
```python
TIME_SERIES_MAPPING = {
    "arima": {
        "module": "statsmodels.tsa.arima.model",
        "class": "ARIMA",
        "type": "time_series",
        "metrics": ["aic", "bic", "hqic", "forecast", "residuals"],
        "description": "Autoregressive Integrated Moving Average",
        "formula_required": False,
        "default_params": {"order": (1, 1, 1)}
    },
    "var": {
        "module": "statsmodels.tsa.vector_ar.var_model",
        "class": "VAR",
        "type": "time_series",
        "metrics": ["aic", "bic", "hqic", "forecast", "irf"],
        "description": "Vector Autoregression",
        "formula_required": False,
        "default_params": {"maxlags": 4}
    },
    "varma": {
        "module": "statsmodels.tsa.statespace.varmax",
        "class": "VARMAX",
        "type": "time_series",
        "metrics": ["aic", "bic", "hqic", "forecast"],
        "description": "Vector Autoregression Moving Average",
        "formula_required": False,
        "default_params": {"order": (1, 1)}
    },
    "sarima": {
        "module": "statsmodels.tsa.statespace.sarimax",
        "class": "SARIMAX",
        "type": "time_series",
        "metrics": ["aic", "bic", "hqic", "forecast"],
        "description": "Seasonal ARIMA",
        "formula_required": False,
        "default_params": {"order": (1, 1, 1), "seasonal_order": (1, 1, 1, 12)}
    }
}
```

### **2. Nonparametric Models** (`algos/nonparametric.py`)
```python
NONPARAMETRIC_MAPPING = {
    "kernel_density": {
        "module": "scipy.stats",
        "class": "gaussian_kde",
        "type": "nonparametric",
        "metrics": ["bandwidth", "pdf", "entropy"],
        "description": "Kernel Density Estimation",
        "formula_required": False
    },
    "lowess": {
        "module": "statsmodels.nonparametric.smoothers_lowess",
        "class": "lowess",
        "type": "nonparametric",
        "metrics": ["fitted_values", "residuals", "smoothing"],
        "description": "Locally Weighted Scatterplot Smoothing",
        "formula_required": False,
        "default_params": {"frac": 0.3}
    },
    "kernel_regression": {
        "module": "statsmodels.nonparametric.kernel_regression",
        "class": "KernelReg",
        "type": "nonparametric",
        "metrics": ["fitted_values", "residuals", "r2"],
        "description": "Kernel Regression",
        "formula_required": False
    }
}
```

### **3. Multivariate Models** (`algos/multivariate.py`)
```python
MULTIVARIATE_MAPPING = {
    "pca": {
        "module": "sklearn.decomposition",
        "class": "PCA",
        "type": "multivariate",
        "metrics": ["explained_variance_ratio", "n_components", "singular_values"],
        "description": "Principal Component Analysis",
        "formula_required": False,
        "default_params": {"n_components": 2}
    },
    "factor_analysis": {
        "module": "factor_analyzer",
        "class": "FactorAnalyzer",
        "type": "multivariate",
        "metrics": ["loadings", "communalities", "eigenvalues"],
        "description": "Factor Analysis",
        "formula_required": False,
        "default_params": {"n_factors": 3}
    },
    "canonical_correlation": {
        "module": "statsmodels.multivariate.cancorr",
        "class": "CanCorr",
        "type": "multivariate",
        "metrics": ["canon_corr", "canon_weights", "canon_loadings"],
        "description": "Canonical Correlation Analysis",
        "formula_required": False
    }
}
```

### **4. Survival Analysis** (`algos/survival.py`)
```python
SURVIVAL_MAPPING = {
    "cox_proportional_hazards": {
        "module": "lifelines",
        "class": "CoxPHFitter",
        "type": "survival",
        "metrics": ["concordance_index", "log_likelihood", "aic", "bic"],
        "description": "Cox Proportional Hazards Model",
        "formula_required": False
    },
    "kaplan_meier": {
        "module": "lifelines",
        "class": "KaplanMeierFitter",
        "type": "survival",
        "metrics": ["survival_function", "median_survival", "mean_survival"],
        "description": "Kaplan-Meier Estimator",
        "formula_required": False
    },
    "weibull_aft": {
        "module": "lifelines",
        "class": "WeibullAFTFitter",
        "type": "survival",
        "metrics": ["concordance_index", "log_likelihood", "aic", "bic"],
        "description": "Weibull Accelerated Failure Time Model",
        "formula_required": False
    }
}
```

## 🧪 **Testing Strategy**

### **1. Test Structure**
Each algorithm module should have comprehensive tests covering:

- **Unit Tests**: Real datasets from statsmodels, basic functionality
- **Real Dataset Tests**: Actual datasets from [statsmodels datasets](https://www.statsmodels.org/stable/datasets/index.html#datasets)
- **Edge Case Tests**: Error handling, invalid inputs, edge cases
- **Integration Tests**: LangGraph tool creation and validation
- **Fallback Tests**: Synthetic data with warnings when real datasets unavailable

### **2. Test Data Requirements**
- **Real Datasets (Primary)**: Use statsmodels built-in datasets from [statsmodels datasets](https://www.statsmodels.org/stable/datasets/index.html#datasets) as the primary testing approach
- **Synthetic Data (Fallback Only)**: Generate appropriate data only when real datasets are unavailable, with clear warnings
- **Edge Cases**: Empty data, missing values, invalid parameters

### **3. Test Validation**
- **Model Fitting**: Verify models fit without errors
- **Metric Calculation**: Validate that metrics are calculated correctly
- **Error Handling**: Ensure proper error messages for invalid inputs
- **Performance**: Check that models perform reasonably on real data
- **Real Dataset Priority**: Always prefer statsmodels datasets over synthetic data

### **4. Available Statsmodels Datasets**
The following datasets from [statsmodels datasets](https://www.statsmodels.org/stable/datasets/index.html#datasets) should be used for testing:

#### **Linear Models & GLM Datasets**
- **longley**: Employment data (TOTEMP ~ GNPDEFL + GNP + UNEMP)
- **engel**: Food expenditure data (foodexp ~ income)
- **grunfeld**: Investment data (invest ~ value + capital)
- **scotland**: Scottish voting data (YES ~ various demographic variables)
- **star98**: Educational data (NABOVE ~ various school variables)
- **fair**: Affairs data (affairs ~ rate_marriage + age + yrs_married + children + religious + educ + occupation + occupation_husb)

#### **Time Series Datasets**
- **nile**: Nile River flows at Ashwan 1871-1970
- **sunspots**: Yearly sunspots data 1700-2008
- **copper**: World Copper Market 1951-1975 Dataset

#### **Specialized Datasets**
- **breast_cancer**: Breast Cancer Data
- **credit**: Bill Greene's credit scoring data
- **lung_cancer**: Smoking and lung cancer in eight cities in China
- **mauna_loa**: Mauna Loa Weekly Atmospheric CO2 Data
- **house**: First 100 days of the US House of Representatives 1995
- **capital_punishment**: US Capital Punishment dataset
- **danish_data**: Danish Money Demand Data
- **elnino**: El Nino - Sea Surface Temperatures
- **fertility**: World Bank Fertility Data
- **transplant**: Transplant Survival Data
- **german_data**: (West) German interest and inflation rate 1972-1998
- **macrodata**: United States Macroeconomic data
- **mode_choice**: Travel Mode Choice
- **rand_health**: RAND Health Insurance Experiment Data
- **spector**: Spector and Mazzeo (1980) - Program Effectiveness Data
- **stack_loss**: Stack loss data
- **state_crime**: Statewide Crime Data 2009
- **strike**: U.S. Strike Duration Data

#### **Loading Datasets**
```python
import statsmodels.api as sm

# Load dataset as pandas DataFrame
data = sm.datasets.longley.load_pandas()
df = data.data

# Access dependent and independent variables
y = data.endog  # TOTEMP
X = data.exog   # GNPDEFL, GNP, UNEMP, ARMED, POP, YEAR
```

## 📚 **Documentation Requirements**

### **1. Module Documentation**
Each algorithm module should include:

- **Comprehensive docstring** explaining the module's purpose
- **Model mapping** with detailed descriptions
- **Usage examples** for each model type
- **Parameter documentation** with defaults and constraints

### **2. Test Documentation**
Each test module should include:

- **Test coverage** summary
- **Real dataset descriptions** and sources
- **Performance benchmarks** and expectations
- **Known limitations** and edge cases

### **3. Integration Documentation**
- **LangGraph tool creation** examples
- **Parameter validation** procedures
- **Error handling** strategies
- **Best practices** for each model type

## 🔄 **Implementation Workflow**

### **Phase 1: Research and Planning (1-2 days)**
1. **Study statsmodels documentation** for the target algorithm category
2. **Identify available models** and their requirements
3. **Create model mapping** with metadata and default parameters
4. **Plan testing strategy** with appropriate datasets
5. **Define common interface** and parameter structure

### **Phase 2: Core Implementation (3-5 days)**
1. **Create algorithm module** following the template
2. **Implement universal function** with error handling
3. **Add model mapping** with comprehensive metadata
4. **Support multiple interfaces** (array-based, formula-based)
5. **Extract common metrics** and diagnostics
6. **Integrate real datasets** from statsmodels for testing

### **Phase 3: Testing Implementation (2-3 days)**
1. **Create test module** with unit tests using real datasets from statsmodels
2. **Add comprehensive real dataset tests** with statsmodels built-in datasets
3. **Implement edge case tests** for error handling
4. **Validate model performance** and accuracy on real data
5. **Test integration** with existing modules
6. **Add fallback synthetic data tests** with warnings when real datasets unavailable

### **Phase 4: Integration and Documentation (1-2 days)**
1. **Update package initialization** with new imports
2. **Add to test runner** for unified testing
3. **Create usage examples** and documentation
4. **Validate LangGraph integration** works correctly
5. **Update implementation summary** documentation

## 🎯 **Success Metrics**

### **Functional Requirements**
- ✅ All models in the category work correctly
- ✅ Real dataset validation passes
- ✅ Error handling is robust and informative
- ✅ Integration with existing modules works seamlessly

### **Quality Requirements**
- ✅ All tests pass consistently
- ✅ Performance is acceptable for real-world use
- ✅ Documentation is comprehensive and clear
- ✅ Code follows established patterns and conventions

### **Integration Requirements**
- ✅ LangGraph tool creation works correctly
- ✅ Parameter validation is comprehensive
- ✅ Error messages are helpful and actionable
- ✅ Examples are working and well-documented

## 💡 **Best Practices**

### **1. Model Mapping**
- **Comprehensive metadata**: Include all necessary information for each model
- **Default parameters**: Provide sensible defaults for common use cases
- **Metric descriptions**: Clearly document what metrics are available
- **Formula support**: Indicate whether formula interface is supported

### **2. Error Handling**
- **Validation first**: Check inputs before attempting model fitting
- **Informative messages**: Provide clear error messages with suggestions
- **Graceful degradation**: Handle edge cases without crashing
- **Logging**: Use appropriate logging levels for debugging

### **3. Testing Strategy**
- **Real datasets (Primary)**: Use statsmodels built-in datasets from [statsmodels datasets](https://www.statsmodels.org/stable/datasets/index.html#datasets) as the primary testing approach
- **Synthetic data (Fallback)**: Generate appropriate data only when real datasets are unavailable, with clear warnings
- **Edge cases**: Test error conditions and boundary cases
- **Integration**: Test with existing modules and LangGraph

### **4. Documentation**
- **Clear examples**: Provide working examples for each model
- **Parameter documentation**: Explain all parameters and their effects
- **Usage patterns**: Show common usage patterns and best practices
- **Troubleshooting**: Include common issues and solutions

## 🚀 **Next Steps**

### **Immediate Priorities**
1. **Time Series Models**: ARIMA, VAR, VARMAX, SARIMAX
2. **Nonparametric Models**: Kernel Density, LOWESS, Kernel Regression
3. **Multivariate Models**: PCA, Factor Analysis, Canonical Correlation
4. **Survival Analysis**: Cox PH, Kaplan-Meier, Weibull AFT

### **Advanced Models**
1. **Bayesian Models**: PyMC integration for Bayesian inference
2. **Machine Learning**: scikit-learn integration for ML models
3. **Deep Learning**: TensorFlow/PyTorch integration for neural networks
4. **Specialized Models**: Spatial models, panel data, hierarchical models

## 🎉 **Conclusion**

This updated blueprint provides a proven, modular framework for implementing universal tools for any statsmodels algorithm category. The key to success is:

1. **Follow the established pattern** from linear_models.py and glm.py
2. **Use the modular structure** with separate algorithm modules
3. **Implement comprehensive testing** with real datasets
4. **Maintain consistent interfaces** across all modules
5. **Document everything thoroughly** with clear examples

This approach ensures production-ready, thoroughly tested statistical analysis tools that can be easily integrated into LangGraph-powered agents! 🚀
