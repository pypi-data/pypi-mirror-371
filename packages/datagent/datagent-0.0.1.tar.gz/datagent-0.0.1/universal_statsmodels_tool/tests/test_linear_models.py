#!/usr/bin/env python3
"""
Comprehensive pytest suite for Linear Models in Universal Statsmodels Tool.

This module consolidates all linear model testing including:
- Unit tests for basic functionality
- Real dataset validation
- Error handling and edge cases
- Model comparison and diagnostics
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
import warnings
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules
from algos.linear_models import (
    universal_linear_models,
    get_available_models,
    extract_model_info,
    create_langgraph_tool,
    validate_model_parameters,
    LinearModels
)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


@pytest.fixture
def linear_models():
    """Create an instance of LinearModels for testing."""
    return LinearModels()


class TestLinearModelsUnit:
    """Unit tests for the linear models module."""
    
    def test_basic_functionality(self, linear_models):
        """Test basic functionality with real datasets."""
        # Test get_available_models
        models = linear_models.get_available_models()
        assert 'regression' in models
        expected_models = ['ols', 'gls', 'wls', 'quantile_regression', 
                          'recursive_least_squares', 'rolling_regression', 'mixed_linear_model']
        
        for model_name in expected_models:
            assert model_name in models['regression']
        
        # Test extract_model_info
        info = linear_models.extract_model_info('ols')
        assert 'error' not in info
        assert info['model_name'] == 'ols'
        assert info['class_name'] == 'OLS'
        
        # Test with real dataset (Engel dataset)
        try:
            import statsmodels.api as sm
            engel_data = sm.datasets.engel.load_pandas().data
            data = engel_data
            dependent_var = 'foodexp'
            independent_vars = ['income']
        except ImportError:
            # Fallback to synthetic data only if statsmodels is completely unavailable
            np.random.seed(42)
            n_samples = 100
            x1 = np.random.randn(n_samples)
            x2 = np.random.randn(n_samples)
            y = 2 + 1.5 * x1 + 0.8 * x2 + np.random.randn(n_samples) * 0.5
            
            data = pd.DataFrame({
                'y': y,
                'x1': x1,
                'x2': x2
            })
            dependent_var = 'y'
            independent_vars = ['x1', 'x2']
        
        # Test OLS
        result = universal_linear_models(
            model_name='ols',
            data=data,
            dependent_var=dependent_var,
            independent_vars=independent_vars,
            add_constant=True
        )
        
        assert result['success'] is True
        assert 'metrics' in result
        assert 'r2' in result['metrics']
        assert result['metrics']['r2'] > 0
        
        # Test error handling
        result = universal_linear_models(
            model_name='invalid_model',
            data=data,
            dependent_var=dependent_var,
            independent_vars=independent_vars
        )
        
        assert result['success'] is False
        assert 'error' in result
    

    
    def test_get_available_models(self, linear_models):
        """Test getting available models."""
        models = linear_models.get_available_models()
        
        # Check that models are grouped by type
        assert 'regression' in models
        
        # Check that all expected models are present
        expected_models = ['ols', 'gls', 'wls', 'quantile_regression', 
                          'recursive_least_squares', 'rolling_regression', 'mixed_linear_model']
        
        for model_name in expected_models:
            assert model_name in models['regression']
    
    def test_extract_model_info(self, linear_models):
        """Test extracting model information."""
        # Test valid model
        info = linear_models.extract_model_info('ols')
        assert 'error' not in info
        assert info['model_name'] == 'ols'
        assert info['class_name'] == 'OLS'
        assert info['type'] == 'regression'
        
        # Test invalid model
        info = linear_models.extract_model_info('invalid_model')
        assert 'error' in info
    
    def test_create_langgraph_tool(self, linear_models):
        """Test creating LangGraph tool definitions."""
        tool = linear_models.create_langgraph_tool('ols')
        assert 'error' not in tool
        assert tool['name'] == 'fit_ols'
        assert 'parameters' in tool
        assert 'description' in tool
        
        # Test invalid model
        tool = linear_models.create_langgraph_tool('invalid_model')
        assert 'error' in tool
    
    def test_validate_model_parameters(self, linear_models):
        """Test parameter validation."""
        # Test valid parameters
        validation = linear_models.validate_model_parameters('ols', {'endog': [1, 2, 3], 'exog': [[1, 1], [1, 2], [1, 3]], 'kwargs': {}})
        assert validation['valid'] is True
        
        # Test invalid model
        validation = linear_models.validate_model_parameters('invalid_model', {})
        assert validation['valid'] is False
        assert 'error' in validation
    
    def test_universal_linear_models_invalid_model(self, real_datasets):
        """Test universal_linear_models with invalid model name."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        result = universal_linear_models(
            model_name='invalid_model',
            data=dataset_info['data'],
            dependent_var=dataset_info['dependent_var'],
            independent_vars=dataset_info['independent_vars'][:2]
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_universal_linear_models_missing_dependent_var(self, real_datasets):
        """Test universal_linear_models with missing dependent variable."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        result = universal_linear_models(
            model_name='ols',
            data=dataset_info['data'],
            dependent_var='nonexistent_var',
            independent_vars=dataset_info['independent_vars'][:2]
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_universal_linear_models_missing_independent_vars(self, real_datasets):
        """Test universal_linear_models with missing independent variables."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        result = universal_linear_models(
            model_name='ols',
            data=dataset_info['data'],
            dependent_var=dataset_info['dependent_var'],
            independent_vars=['nonexistent_var']
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_universal_linear_models_no_independent_vars_or_formula(self, real_datasets):
        """Test universal_linear_models without independent vars or formula."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        result = universal_linear_models(
            model_name='ols',
            data=dataset_info['data'],
            dependent_var=dataset_info['dependent_var']
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    @patch('algos.linear_models.importlib.import_module')
    def test_universal_linear_models_ols_success(self, mock_import, real_datasets):
        """Test successful OLS fitting."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        # Mock the OLS class and its fit method
        mock_ols_class = MagicMock()
        mock_fitted_model = MagicMock()
        
        # Set up mock attributes
        mock_fitted_model.rsquared = 0.85
        mock_fitted_model.rsquared_adj = 0.84
        mock_fitted_model.aic = 150.0
        mock_fitted_model.bic = 160.0
        mock_fitted_model.fvalue = 25.0
        mock_fitted_model.f_pvalue = 0.001
        mock_fitted_model.params = pd.Series({'const': 2.0, 'x1': 1.5, 'x2': 0.8})
        mock_fitted_model.resid = pd.Series(np.random.randn(100))
        mock_fitted_model.fittedvalues = pd.Series(np.random.randn(100))
        mock_fitted_model.summary.return_value = "Model Summary"
        
        mock_ols_class.return_value.fit.return_value = mock_fitted_model
        
        # Mock the module import
        mock_module = MagicMock()
        mock_module.OLS = mock_ols_class
        mock_import.return_value = mock_module
        
        # Mock statsmodels.api.add_constant
        with patch('statsmodels.api') as mock_sm:
            independent_vars = dataset_info['independent_vars'][:2]
            mock_sm.add_constant.return_value = dataset_info['data'][independent_vars]
            
            result = universal_linear_models(
                model_name='ols',
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=independent_vars,
                add_constant=True
            )
            
            assert result['success'] is True
            assert result['model_name'] == 'ols'
            assert result['model_type'] == 'regression'
            assert 'metrics' in result
            assert 'diagnostics' in result
            
            # Check metrics
            metrics = result['metrics']
            assert metrics['r2'] == 0.85
            assert metrics['adj_r2'] == 0.84
            assert metrics['aic'] == 150.0
            assert metrics['bic'] == 160.0
            assert metrics['f_statistic'] == 25.0
            assert metrics['p_value'] == 0.001
    
    def test_linear_models_mapping_structure(self, linear_models):
        """Test that the mapping has the correct structure."""
        for model_name, info in linear_models.model_mapping.items():
            # Check required keys
            required_keys = ['module', 'class', 'type', 'metrics', 'description', 'formula_required']
            for key in required_keys:
                assert key in info, f"Missing key '{key}' in model '{model_name}'"
            
            # Check data types
            assert isinstance(info['module'], str)
            assert isinstance(info['class'], str)
            assert isinstance(info['type'], str)
            assert isinstance(info['metrics'], list)
            assert isinstance(info['description'], str)
            assert isinstance(info['formula_required'], bool)
    
    def test_model_types(self, linear_models):
        """Test that all models have valid types."""
        valid_types = ['regression']
        for model_name, info in linear_models.model_mapping.items():
            assert info['type'] in valid_types, f"Invalid type '{info['type']}' for model '{model_name}'"
    
    def test_metrics_not_empty(self, linear_models):
        """Test that all models have at least one metric."""
        for model_name, info in linear_models.model_mapping.items():
            assert len(info['metrics']) > 0, f"No metrics defined for model '{model_name}'"


class TestLinearModelsRealDatasets:
    """Tests using real datasets from statsmodels."""
    
    def test_ols_with_real_datasets(self, real_datasets):
        """Test OLS regression with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            result = universal_linear_models(
                model_name="ols",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars'][:2],
                add_constant=True
            )
            
            assert result['success'] is True
            assert result['model_name'] == 'ols'
            assert result['model_type'] == 'regression'
            assert 'metrics' in result
            assert 'diagnostics' in result
            
            # Check that R² is between 0 and 1
            assert 0 <= result['metrics']['r2'] <= 1
            assert result['n_observations'] > 0
    
    def test_formula_interface_with_real_datasets(self, real_datasets):
        """Test formula interface with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            # Create formula string
            formula = f"{dataset_info['dependent_var']} ~ {' + '.join(dataset_info['independent_vars'][:2])}"
            
            result = universal_linear_models(
                model_name="ols",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                formula=formula
            )
            
            assert result['success'] is True
            assert result['model_name'] == 'ols'
            assert 'metrics' in result
    
    def test_wls_with_real_datasets(self, real_datasets):
        """Test Weighted Least Squares with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            # Create weights
            data_with_weights = dataset_info['data'].copy()
            if len(dataset_info['independent_vars']) > 0:
                weight_var = dataset_info['independent_vars'][0]
                if weight_var in data_with_weights.columns:
                    weights = 1 / (np.abs(data_with_weights[weight_var]) + 1)
                    data_with_weights['weights'] = weights
                    
                    result = universal_linear_models(
                        model_name="wls",
                        data=data_with_weights,
                        dependent_var=dataset_info['dependent_var'],
                        independent_vars=dataset_info['independent_vars'][:2],
                        weights=data_with_weights['weights']
                    )
                    
                    assert result['success'] is True
                    assert result['model_name'] == 'wls'
                    assert 'metrics' in result
    
    def test_gls_with_real_datasets(self, real_datasets):
        """Test Generalized Least Squares with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            result = universal_linear_models(
                model_name="gls",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars'][:2]
            )
            
            assert result['success'] is True
            assert result['model_name'] == 'gls'
            assert 'metrics' in result
    
    def test_quantile_regression_with_real_datasets(self, real_datasets):
        """Test Quantile Regression with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            result = universal_linear_models(
                model_name="quantile_regression",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars'][:2],
                q=0.5  # Median regression
            )
            
            assert result['success'] is True
            assert result['model_name'] == 'quantile_regression'
            assert 'metrics' in result
    
    def test_model_comparison(self, real_datasets):
        """Compare different models on the same dataset."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        models_to_test = ['ols', 'gls']
        results = {}
        
        for model_name in models_to_test:
            result = universal_linear_models(
                model_name=model_name,
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars'][:2]
            )
            
            assert result['success'] is True
            results[model_name] = result['metrics']['r2']
        
        # All models should produce valid R² values
        for r2 in results.values():
            assert 0 <= r2 <= 1
    
    def test_diagnostic_analysis(self, real_datasets):
        """Test comprehensive diagnostic analysis on real datasets."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        result = universal_linear_models(
            model_name="ols",
            data=dataset_info['data'],
            dependent_var=dataset_info['dependent_var'],
            independent_vars=dataset_info['independent_vars'],
            add_constant=True
        )
        
        assert result['success'] is True
        assert 'diagnostics' in result
        
        diagnostics = result['diagnostics']
        
        # Check that diagnostic tests are present
        if 'residual_normality_p_value' in diagnostics:
            assert 0 <= diagnostics['residual_normality_p_value'] <= 1
        
        if 'durbin_watson_statistic' in diagnostics:
            assert diagnostics['durbin_watson_statistic'] > 0
        
        if 'breusch_pagan_p_value' in diagnostics:
            assert 0 <= diagnostics['breusch_pagan_p_value'] <= 1
    
    def test_weighted_least_squares_with_real_datasets(self, real_datasets):
        """Test Weighted Least Squares with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            if len(dataset_info['independent_vars']) > 1:
                # Create weights based on first independent variable
                weight_var = dataset_info['independent_vars'][0]
                if weight_var in dataset_info['data'].columns:
                    weights = 1 / (np.abs(dataset_info['data'][weight_var]) + 1)
                    
                    result = universal_linear_models(
                        model_name="wls",
                        data=dataset_info['data'],
                        dependent_var=dataset_info['dependent_var'],
                        independent_vars=dataset_info['independent_vars'][:2],
                        weights=weights
                    )
                    
                    assert result['success'] is True
                    assert result['model_name'] == 'wls'
                    assert 'metrics' in result
                    assert 0 <= result['metrics']['r2'] <= 1
    
    def test_comprehensive_linear_models_demonstration(self, real_datasets):
        """Comprehensive demonstration of linear models with real datasets."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        for dataset_name, dataset_info in real_datasets.items():
            # Test OLS with multiple variables
            result_ols = universal_linear_models(
                model_name='ols',
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars'][:3],
                add_constant=True
            )
            
            assert result_ols['success'] is True
            assert result_ols['model_name'] == 'ols'
            assert 'metrics' in result_ols
            assert 'r2' in result_ols['metrics']
            assert 0 <= result_ols['metrics']['r2'] <= 1
            
            # Test GLS
            result_gls = universal_linear_models(
                model_name='gls',
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars'][:2]
            )
            
            assert result_gls['success'] is True
            assert result_gls['model_name'] == 'gls'
            assert 'metrics' in result_gls
            
            # Test formula interface
            formula = f"{dataset_info['dependent_var']} ~ {' + '.join(dataset_info['independent_vars'][:2])}"
            result_formula = universal_linear_models(
                model_name='ols',
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                formula=formula
            )
            
            assert result_formula['success'] is True
            assert 'metrics' in result_formula


class TestLinearModelsEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        result = universal_linear_models(
            model_name='ols',
            data=empty_df,
            dependent_var='y',
            independent_vars=['x1']
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_single_observation(self):
        """Test with single observation."""
        single_obs = pd.DataFrame({'y': [1.0], 'x1': [2.0]})
        
        result = universal_linear_models(
            model_name='ols',
            data=single_obs,
            dependent_var='y',
            independent_vars=['x1']
        )
        
        # Should fail due to insufficient observations
        assert result['success'] is False
        assert 'error' in result
    
    def test_constant_variables(self):
        """Test with constant variables."""
        constant_data = pd.DataFrame({
            'y': [1, 2, 3, 4, 5],
            'x1': [1, 1, 1, 1, 1],  # Constant
            'x2': [2, 2, 2, 2, 2]   # Constant
        })
        
        result = universal_linear_models(
            model_name='ols',
            data=constant_data,
            dependent_var='y',
            independent_vars=['x1', 'x2']
        )
        
        # Model should succeed but with warnings about constant variables
        assert result['success'] is True
        assert 'metrics' in result
        # Check that the model was fitted (even if constant variables don't contribute)
        assert result['n_observations'] == 5
    
    def test_missing_values(self):
        """Test handling of missing values."""
        data_with_missing = pd.DataFrame({
            'y': [1, 2, np.nan, 4, 5],
            'x1': [1, 2, 3, np.nan, 5],
            'x2': [1, 2, 3, 4, 5]
        })
        
        result = universal_linear_models(
            model_name='ols',
            data=data_with_missing,
            dependent_var='y',
            independent_vars=['x1', 'x2']
        )
        
        # Should handle missing values gracefully
        if result['success']:
            assert result['n_observations'] < 5  # Some rows should be dropped
        else:
            assert 'error' in result
    
    def test_large_dataset(self):
        """Test with large dataset using real data."""
        try:
            import statsmodels.api as sm
            # Use macrodata which has many observations
            macro_data = sm.datasets.macrodata.load_pandas().data
            
            # Select a subset of variables for testing
            test_data = macro_data[['realgdp', 'realcons', 'realinv', 'realgovt']].copy()
            
            result = universal_linear_models(
                model_name='ols',
                data=test_data,
                dependent_var='realgdp',
                independent_vars=['realcons', 'realinv']
            )
            
            assert result['success'] is True
            assert result['n_observations'] > 0
        except ImportError:
            # Fallback to synthetic data only if statsmodels is completely unavailable
            np.random.seed(42)
            n_samples = 10000
            
            large_data = pd.DataFrame({
                'y': np.random.randn(n_samples),
                'x1': np.random.randn(n_samples),
                'x2': np.random.randn(n_samples)
            })
            
            result = universal_linear_models(
                model_name='ols',
                data=large_data,
                dependent_var='y',
                independent_vars=['x1', 'x2']
            )
            
            assert result['success'] is True
            assert result['n_observations'] == n_samples


if __name__ == "__main__":
    # Run all tests in this file
    pytest.main([__file__, "-v", "--tb=short"])
