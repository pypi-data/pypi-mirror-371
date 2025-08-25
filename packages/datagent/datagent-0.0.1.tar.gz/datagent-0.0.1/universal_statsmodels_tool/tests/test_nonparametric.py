"""
Comprehensive test suite for Nonparametric models using pytest.

This module provides unit tests, real dataset tests, and edge case tests
for all nonparametric models in the universal statsmodels tool.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algos.nonparametric import (
    universal_nonparametric,
    get_available_models,
    extract_model_info,
    validate_model_parameters,
    NonparametricModels
)


@pytest.fixture
def real_datasets():
    """Get real datasets from statsmodels for testing."""
    real_datasets = {}
    try:
        import statsmodels.api as sm
        
        # Load commonly available datasets for different model types
        available_datasets = [
            ('longley', 'TOTEMP', ['GNPDEFL', 'GNP', 'UNEMP']),
            ('engel', 'foodexp', ['income']),
            ('grunfeld', 'invest', ['value', 'capital']),
            ('nile', 'volume', []),  # Time series data - use for univariate KDE
            ('sunspots', 'sunspots', [])  # Time series data - use for univariate KDE
        ]
        
        for dataset_name, dep_var, indep_vars in available_datasets:
            try:
                dataset = getattr(sm.datasets, dataset_name).load_pandas()
                real_datasets[dataset_name] = {
                    'data': dataset.data,
                    'dependent_var': dep_var,
                    'independent_vars': indep_vars if indep_vars else [col for col in dataset.data.columns if col != dep_var]
                }
            except (AttributeError, Exception) as e:
                # Skip datasets that are not available
                continue
        
        if not real_datasets:
            pytest.skip("No real datasets available from statsmodels")
            
    except ImportError as e:
        pytest.skip(f"statsmodels not available: {str(e)}")
    
    return real_datasets


@pytest.fixture
def synthetic_data():
    """Create synthetic data for testing when real datasets are unavailable."""
    np.random.seed(42)
    n_samples = 1000
    
    # Generate synthetic data
    x = np.random.randn(n_samples)
    y = 2 + 1.5 * x + 0.8 * x**2 + np.random.randn(n_samples) * 0.5
    positive_data = np.abs(x) + np.random.exponential(1, n_samples)
    multivariate_data = np.random.multivariate_normal(
        mean=[0, 0], 
        cov=[[1, 0.5], [0.5, 1]], 
        size=n_samples
    )
    
    # Create DataFrame
    synthetic_data = pd.DataFrame({
        'x': x,
        'y': y,
        'positive_data': positive_data,
        'z1': multivariate_data[:, 0],
        'z2': multivariate_data[:, 1]
    })
    
    return synthetic_data


@pytest.fixture
def nonparametric_models():
    """Create an instance of NonparametricModels for testing."""
    return NonparametricModels()


class TestNonparametricUnit:
    """Unit tests for nonparametric models."""
    
    def test_available_models(self, nonparametric_models):
        """Test that all models are available."""
        models = nonparametric_models.get_available_models()
        assert isinstance(models, dict)
        assert len(models) > 0
        
        # Test specific model types
        expected_types = ['density_estimation', 'regression', 'smoothing', 'asymmetric_kernel']
        for model_type in expected_types:
            assert model_type in models
            assert isinstance(models[model_type], dict)
            assert len(models[model_type]) > 0
        
        # Test model structure
        for model_type, type_models in models.items():
            for model_name, model_info in type_models.items():
                assert 'description' in model_info
                assert 'class' in model_info
                assert 'module' in model_info
                assert 'metrics' in model_info
    
    def test_model_info_extraction(self, nonparametric_models):
        """Test model info extraction for all models."""
        models = nonparametric_models.get_available_models()
        for model_type, type_models in models.items():
            for model_name in type_models.keys():
                info = nonparametric_models.extract_model_info(model_name)
                assert 'error' not in info
                assert 'model_name' in info
                assert 'description' in info
                assert 'type' in info
    
    def test_univariate_kde_real_data(self, nonparametric_models, real_datasets):
        """Test univariate kernel density estimation with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            data = dataset_info['data']
            # Use first numeric column for univariate KDE
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                test_col = numeric_cols[0]
                result = nonparametric_models.fit_model(
                    model_name="univariate_kde",
                    data=data,
                    variables=[test_col]
                )
                
                assert result['success'], f"Failed to fit univariate_kde on {dataset_name}: {result.get('error', 'Unknown error')}"
                assert 'metrics' in result
                assert 'fitted_model' in result
                assert 'bandwidth' in result['metrics']
                assert isinstance(result['metrics']['bandwidth'], (int, float))
                break  # Test with first suitable dataset
    
    def test_univariate_kde_synthetic_data(self, nonparametric_models, synthetic_data):
        """Test univariate kernel density estimation with synthetic data."""
        result = nonparametric_models.fit_model(
            model_name="univariate_kde",
            data=synthetic_data,
            variables=["x"]
        )
        
        assert result['success']
        assert 'metrics' in result
        assert 'fitted_model' in result
        assert 'bandwidth' in result['metrics']
        assert isinstance(result['metrics']['bandwidth'], (int, float))
    
    def test_multivariate_kde_real_data(self, nonparametric_models, real_datasets):
        """Test multivariate kernel density estimation with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            data = dataset_info['data']
            # Use first two numeric columns for multivariate KDE
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                test_cols = numeric_cols[:2].tolist()
                result = nonparametric_models.fit_model(
                    model_name="multivariate_kde",
                    data=data,
                    variables=test_cols
                )
                
                assert result['success'], f"Failed to fit multivariate_kde on {dataset_name}: {result.get('error', 'Unknown error')}"
                assert 'metrics' in result
                assert 'fitted_model' in result
                assert result['metrics']['dimensions'] == 2
                break  # Test with first suitable dataset
    
    def test_multivariate_kde_synthetic_data(self, nonparametric_models, synthetic_data):
        """Test multivariate kernel density estimation with synthetic data."""
        result = nonparametric_models.fit_model(
            model_name="multivariate_kde",
            data=synthetic_data,
            variables=["z1", "z2"]
        )
        
        assert result['success']
        assert 'metrics' in result
        assert 'fitted_model' in result
        assert result['metrics']['dimensions'] == 2
    
    def test_kernel_regression_real_data(self, nonparametric_models, real_datasets):
        """Test kernel regression with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            data = dataset_info['data']
            dependent_var = dataset_info['dependent_var']
            independent_vars = dataset_info['independent_vars']
            
            # Skip if no independent variables available
            if not independent_vars:
                continue
            
            result = nonparametric_models.fit_model(
                model_name="kernel_regression",
                data=data,
                dependent_var=dependent_var,
                independent_vars=independent_vars[:1]  # Use first independent variable
            )
            
            assert result['success'], f"Failed to fit kernel_regression on {dataset_name}: {result.get('error', 'Unknown error')}"
            assert 'metrics' in result
            assert 'fitted_model' in result
            assert 'r2' in result['metrics']
            assert isinstance(result['metrics']['r2'], (int, float))
            break  # Test with first suitable dataset
    
    def test_kernel_regression_synthetic_data(self, nonparametric_models, synthetic_data):
        """Test kernel regression with synthetic data."""
        result = nonparametric_models.fit_model(
            model_name="kernel_regression",
            data=synthetic_data,
            dependent_var="y",
            independent_vars=["x"]
        )
        
        assert result['success']
        assert 'metrics' in result
        assert 'fitted_model' in result
        assert 'r2' in result['metrics']
        assert isinstance(result['metrics']['r2'], (int, float))
    
    def test_lowess_smoothing_real_data(self, nonparametric_models, real_datasets):
        """Test LOWESS smoothing with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            data = dataset_info['data']
            dependent_var = dataset_info['dependent_var']
            independent_vars = dataset_info['independent_vars']
            
            # Skip if no independent variables available
            if not independent_vars:
                continue
            
            result = nonparametric_models.fit_model(
                model_name="lowess",
                data=data,
                x_col=independent_vars[0],  # Use first independent variable
                y_col=dependent_var,
                frac=0.3
            )
            
            assert result['success'], f"Failed to fit lowess on {dataset_name}: {result.get('error', 'Unknown error')}"
            assert 'metrics' in result
            assert 'fitted_model' in result
            assert 'residuals_std' in result['metrics']
            assert isinstance(result['metrics']['residuals_std'], (int, float))
            break  # Test with first suitable dataset
    
    def test_lowess_smoothing_synthetic_data(self, nonparametric_models, synthetic_data):
        """Test LOWESS smoothing with synthetic data."""
        result = nonparametric_models.fit_model(
            model_name="lowess",
            data=synthetic_data,
            x_col="x",
            y_col="y",
            frac=0.3
        )
        
        assert result['success']
        assert 'metrics' in result
        assert 'fitted_model' in result
        assert 'residuals_std' in result['metrics']
        assert isinstance(result['metrics']['residuals_std'], (int, float))
    
    def test_beta_kernel_pdf_synthetic_data(self, nonparametric_models, synthetic_data):
        """Test beta kernel density estimation with synthetic data."""
        result = nonparametric_models.fit_model(
            model_name="beta_kernel_pdf",
            data=synthetic_data,
            variables=["positive_data"]
        )
        
        assert result['success']
        assert 'metrics' in result
        assert 'fitted_model' in result
        assert 'bandwidth' in result['metrics']
        assert isinstance(result['metrics']['bandwidth'], (int, float))
    
    def test_parameter_validation(self, nonparametric_models):
        """Test parameter validation."""
        # Test valid parameters with required parameters
        validation = nonparametric_models.validate_model_parameters("lowess", {
            "endog": [1, 2, 3], 
            "exog": [1, 2, 3], 
            "frac": 0.3, 
            "it": 3
        })
        assert validation["valid"]
        
        # Test invalid parameters
        validation = nonparametric_models.validate_model_parameters("lowess", {"frac": 1.5, "it": -1})
        assert not validation["valid"]
        assert len(validation["errors"]) > 0
        
        # Test unknown model
        validation = nonparametric_models.validate_model_parameters("unknown_model", {})
        assert not validation["valid"]
        assert "error" in validation
    
    def test_backward_compatibility_functions(self, synthetic_data):
        """Test backward compatibility functions still work."""
        # Test universal_nonparametric function
        result = universal_nonparametric(
            model_name="univariate_kde",
            data=synthetic_data,
            variables=["x"]
        )
        assert result['success']
        assert 'metrics' in result
        
        # Test get_available_models function
        models = get_available_models()
        assert isinstance(models, dict)
        assert len(models) > 0
        
        # Test extract_model_info function
        info = extract_model_info("univariate_kde")
        assert 'error' not in info
        assert 'model_name' in info
        
        # Test validate_model_parameters function
        validation = validate_model_parameters("lowess", {
            "endog": [1, 2, 3], 
            "exog": [1, 2, 3], 
            "frac": 0.3
        })
        assert validation["valid"]


class TestNonparametricEdgeCases:
    """Edge case tests for nonparametric models."""
    
    def test_invalid_model_name(self, nonparametric_models):
        """Test handling of invalid model names."""
        result = nonparametric_models.fit_model(
            model_name="invalid_model",
            data=pd.DataFrame({'y': [1, 2, 3], 'x': [1, 2, 3]}),
            dependent_var="y",
            independent_vars=["x"]
        )
        
        assert not result['success']
        assert 'error' in result
    
    def test_missing_variables(self, nonparametric_models):
        """Test handling of missing variables."""
        data = pd.DataFrame({'y': [1, 2, 3], 'x1': [1, 2, 3]})
        
        # Test missing dependent variable
        result = nonparametric_models.fit_model(
            model_name="kernel_regression",
            data=data,
            dependent_var="missing_y",
            independent_vars=["x1"]
        )
        
        assert not result['success']
        assert 'error' in result
        
        # Test missing independent variables
        result = nonparametric_models.fit_model(
            model_name="kernel_regression",
            data=data,
            dependent_var="y",
            independent_vars=["missing_x"]
        )
        
        assert not result['success']
        assert 'error' in result
    
    def test_empty_data(self, nonparametric_models):
        """Test handling of empty data."""
        empty_data = pd.DataFrame()
        
        result = nonparametric_models.fit_model(
            model_name="univariate_kde",
            data=empty_data,
            variables=["x"]
        )
        
        assert not result['success']
        assert 'error' in result
    
    def test_single_value_data(self, nonparametric_models):
        """Test handling of data with single unique value."""
        single_value_data = pd.DataFrame({'x': [1, 1, 1, 1, 1]})
        
        result = nonparametric_models.fit_model(
            model_name="univariate_kde",
            data=single_value_data,
            variables=["x"]
        )
        
        # This should fail or handle gracefully
        if not result['success']:
            assert 'error' in result
    
    def test_missing_values(self, nonparametric_models):
        """Test handling of missing values."""
        data_with_nans = pd.DataFrame({
            'x': [1, 2, np.nan, 4, 5],
            'y': [1, np.nan, 3, 4, 5]
        })
        
        result = nonparametric_models.fit_model(
            model_name="univariate_kde",
            data=data_with_nans,
            variables=["x"]
        )
        
        # Should handle missing values gracefully
        if result['success']:
            assert 'metrics' in result
        else:
            assert 'error' in result
    
    def test_large_dataset(self, nonparametric_models):
        """Test handling of large datasets."""
        large_data = pd.DataFrame({
            'x': np.random.randn(10000),
            'y': np.random.randn(10000)
        })
        
        result = nonparametric_models.fit_model(
            model_name="univariate_kde",
            data=large_data,
            variables=["x"]
        )
        
        assert result['success']
        assert 'metrics' in result
        # Check data shape instead of sample_size metric
        assert result['data_shape'][0] == 10000


class TestNonparametricPerformance:
    """Performance tests for nonparametric models."""
    
    def test_performance_comparison(self, nonparametric_models):
        """Compare performance of different density estimation methods."""
        np.random.seed(42)
        data = pd.DataFrame({
            'normal': np.random.normal(0, 1, 1000),
            'exponential': np.random.exponential(1, 1000)
        })
        
        models_to_test = [
            "univariate_kde",
            "beta_kernel_pdf",
            "gamma_kernel_pdf"
        ]
        
        results = {}
        for model_name in models_to_test:
            import time
            start_time = time.time()
            
            result = nonparametric_models.fit_model(
                model_name=model_name,
                data=data,
                variables=["normal"]
            )
            
            end_time = time.time()
            results[model_name] = {
                'success': result['success'],
                'time': end_time - start_time,
                'bandwidth': result['metrics']['bandwidth'] if result['success'] else None
            }
        
        # All models should succeed
        for model_name, result in results.items():
            assert result['success'], f"{model_name} failed"
            assert result['time'] < 10.0, f"{model_name} took too long: {result['time']:.2f}s"
    
    def test_bandwidth_selection(self, nonparametric_models):
        """Test different bandwidth selection methods."""
        np.random.seed(42)
        data = pd.DataFrame({'x': np.random.normal(0, 1, 500)})
        
        bandwidth_methods = ['silverman', 'scott']
        
        for bw_method in bandwidth_methods:
            result = nonparametric_models.fit_model(
                model_name="univariate_kde",
                data=data,
                variables=["x"],
                bw=bw_method
            )
            
            assert result['success']
            assert 'bandwidth' in result['metrics']
            assert isinstance(result['metrics']['bandwidth'], (int, float))
            assert result['metrics']['bandwidth'] > 0


class TestNonparametricInheritance:
    """Tests for the inheritance structure and base class functionality."""
    
    def test_inheritance_structure(self, nonparametric_models):
        """Test that NonparametricModels properly inherits from BaseStatsModel."""
        from algos.base_model import BaseStatsModel
        
        # Check inheritance
        assert isinstance(nonparametric_models, BaseStatsModel)
        
        # Check that required methods exist
        assert hasattr(nonparametric_models, 'model_mapping')
        assert hasattr(nonparametric_models, 'available_models')
        assert hasattr(nonparametric_models, 'fit_model')
        assert hasattr(nonparametric_models, 'extract_model_info')
        assert hasattr(nonparametric_models, 'validate_model_parameters')
    
    def test_model_mapping_structure(self, nonparametric_models):
        """Test that model mapping has the correct structure."""
        mapping = nonparametric_models.model_mapping
        
        assert isinstance(mapping, dict)
        assert len(mapping) > 0
        
        # Check structure of each model entry
        for model_name, model_info in mapping.items():
            assert 'module' in model_info
            assert 'class' in model_info
            assert 'type' in model_info
            assert 'metrics' in model_info
            assert 'description' in model_info
            assert 'formula_required' in model_info
            assert 'default_params' in model_info
    
    def test_available_models_structure(self, nonparametric_models):
        """Test that available models have the correct structure."""
        models = nonparametric_models.available_models
        
        assert isinstance(models, dict)
        assert len(models) > 0
        
        # Check structure of each model type
        for model_type, type_models in models.items():
            assert isinstance(type_models, dict)
            assert len(type_models) > 0
            
            for model_name, model_info in type_models.items():
                assert 'description' in model_info
                assert 'class' in model_info
                assert 'module' in model_info
                assert 'metrics' in model_info
                assert 'default_params' in model_info


if __name__ == '__main__':
    pytest.main([__file__, "-v", "--tb=short"])
