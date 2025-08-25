#!/usr/bin/env python3
"""
Comprehensive pytest suite for GLM Models in Universal Statsmodels Tool.

This module consolidates all GLM model testing including:
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
from algos.glm import (
    universal_glm,
    get_available_models,
    extract_model_info,
    create_langgraph_tool,
    validate_model_parameters,
    GLMModels
)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


@pytest.fixture
def glm_models():
    """Create an instance of GLMModels for testing."""
    return GLMModels()


class TestGLMUnit:
    """Unit tests for the GLM module."""
    
    def test_basic_functionality(self, glm_models):
        """Test basic functionality with real datasets."""
        # Test get_available_models
        models = glm_models.get_available_models()
        assert 'glm' in models
        expected_models = ['gaussian_glm', 'binomial_glm', 'poisson_glm', 'gamma_glm']
        
        for model_name in expected_models:
            assert model_name in models['glm']
        
        # Test extract_model_info
        info = glm_models.extract_model_info('gaussian_glm')
        assert 'error' not in info
        assert info['model_name'] == 'gaussian_glm'
        assert info['class_name'] == 'GLM'
        
        # Test with real dataset (Longley dataset)
        try:
            import statsmodels.api as sm
            longley_data = sm.datasets.longley.load_pandas().data
            data = longley_data
            dependent_var = 'TOTEMP'
            independent_vars = ['GNPDEFL', 'GNP', 'UNEMP']
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
        
        # Test Gaussian GLM
        result = universal_glm(
            model_name='gaussian_glm',
            data=data,
            dependent_var=dependent_var,
            independent_vars=independent_vars,
            link_name='identity'
        )
        
        assert result['success'] is True
        assert 'metrics' in result
        assert 'aic' in result['metrics']
        assert result['metrics']['aic'] > 0
        
        # Test error handling
        result = universal_glm(
            model_name='invalid_model',
            data=data,
            dependent_var=dependent_var,
            independent_vars=independent_vars
        )
        
        assert result['success'] is False
        assert 'error' in result
    

    
    def test_get_available_models(self, glm_models):
        """Test getting available models."""
        models = glm_models.get_available_models()
        
        # Check that models are grouped by type
        assert 'glm' in models
        
        # Check that all expected models are present
        expected_models = ['gaussian_glm', 'binomial_glm', 'poisson_glm', 'gamma_glm']
        
        for model_name in expected_models:
            assert model_name in models['glm']
    
    def test_extract_model_info(self, glm_models):
        """Test extracting model information."""
        # Test valid model
        info = glm_models.extract_model_info('gaussian_glm')
        assert 'error' not in info
        assert info['model_name'] == 'gaussian_glm'
        assert info['class_name'] == 'GLM'
        assert info['type'] == 'glm'
        
        # Test invalid model
        info = glm_models.extract_model_info('invalid_model')
        assert 'error' in info
    
    def test_create_langgraph_tool(self, glm_models):
        """Test creating LangGraph tool definitions."""
        tool = glm_models.create_langgraph_tool('gaussian_glm')
        assert 'error' not in tool
        assert tool['name'] == 'fit_gaussian_glm'
        assert 'parameters' in tool
        assert 'description' in tool
        
        # Test invalid model
        tool = glm_models.create_langgraph_tool('invalid_model')
        assert 'error' in tool
    
    def test_validate_model_parameters(self, glm_models):
        """Test parameter validation."""
        # Test valid parameters
        validation = glm_models.validate_model_parameters('gaussian_glm', {'endog': [1, 2, 3], 'exog': [[1, 1], [1, 2], [1, 3]], 'kwargs': {}})
        assert validation['valid'] is True
        
        # Test invalid model
        validation = glm_models.validate_model_parameters('invalid_model', {})
        assert validation['valid'] is False
        assert 'error' in validation
    
    def test_universal_glm_invalid_model(self, real_datasets):
        """Test universal_glm with invalid model name."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        result = universal_glm(
            model_name='invalid_model',
            data=dataset_info['data'],
            dependent_var=dataset_info['dependent_var'],
            independent_vars=dataset_info['independent_vars'][:2]
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_universal_glm_missing_dependent_var(self, real_datasets):
        """Test universal_glm with missing dependent variable."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        result = universal_glm(
            model_name='gaussian_glm',
            data=dataset_info['data'],
            dependent_var='nonexistent_var',
            independent_vars=dataset_info['independent_vars'][:2]
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_universal_glm_missing_independent_vars(self, real_datasets):
        """Test universal_glm with missing independent variables."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        result = universal_glm(
            model_name='gaussian_glm',
            data=dataset_info['data'],
            dependent_var=dataset_info['dependent_var'],
            independent_vars=['nonexistent_var']
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_universal_glm_no_independent_vars_or_formula(self, real_datasets):
        """Test universal_glm without independent vars or formula."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        result = universal_glm(
            model_name='gaussian_glm',
            data=dataset_info['data'],
            dependent_var=dataset_info['dependent_var']
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    @patch('algos.glm.importlib.import_module')
    def test_universal_glm_gaussian_success(self, mock_import, real_datasets):
        """Test successful Gaussian GLM fitting."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        # Mock the GLM class and its fit method
        mock_glm_class = MagicMock()
        mock_fitted_model = MagicMock()
        
        # Set up mock attributes
        mock_fitted_model.aic = 150.0
        mock_fitted_model.bic = 160.0
        mock_fitted_model.deviance = 45.0
        mock_fitted_model.params = pd.Series({'const': 2.0, 'x1': 1.5, 'x2': 0.8})
        mock_fitted_model.resid = pd.Series(np.random.randn(100))
        mock_fitted_model.fittedvalues = pd.Series(np.random.randn(100))
        mock_fitted_model.summary.return_value = "Model Summary"
        
        mock_glm_class.return_value.fit.return_value = mock_fitted_model
        
        # Mock the module import
        mock_module = MagicMock()
        mock_module.GLM = mock_glm_class
        mock_import.return_value = mock_module
        
        # Mock statsmodels.api.add_constant
        with patch('statsmodels.api') as mock_sm:
            independent_vars = dataset_info['independent_vars'][:2]
            mock_sm.add_constant.return_value = dataset_info['data'][independent_vars]
            
            result = universal_glm(
                model_name='gaussian_glm',
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=independent_vars,
                link_name='identity'
            )
            
            assert result['success'] is True
            assert result['model_name'] == 'gaussian_glm'
            assert result['model_type'] == 'glm'
            assert 'metrics' in result
            assert 'diagnostics' in result
            
            # Check metrics
            metrics = result['metrics']
            assert metrics['aic'] == 150.0
            assert metrics['bic'] == 160.0
            assert metrics['deviance'] == 45.0
    
    def test_glm_mapping_structure(self, glm_models):
        """Test that the mapping has the correct structure."""
        for model_name, info in glm_models.model_mapping.items():
            # Check required keys
            required_keys = ['module', 'class', 'type', 'metrics', 'description', 'family', 'default_link', 'links']
            for key in required_keys:
                assert key in info, f"Missing key '{key}' in model '{model_name}'"
            
            # Check data types
            assert isinstance(info['module'], str)
            assert isinstance(info['class'], str)
            assert isinstance(info['type'], str)
            assert isinstance(info['metrics'], list)
            assert isinstance(info['description'], str)
            assert isinstance(info['family'], str)
            assert isinstance(info['default_link'], str)
            assert isinstance(info['links'], list)
    
    def test_model_types(self, glm_models):
        """Test that all models have valid types."""
        valid_types = ['glm']
        for model_name, info in glm_models.model_mapping.items():
            assert info['type'] in valid_types, f"Invalid type '{info['type']}' for model '{model_name}'"
    
    def test_metrics_not_empty(self, glm_models):
        """Test that all models have at least one metric."""
        for model_name, info in glm_models.model_mapping.items():
            assert len(info['metrics']) > 0, f"No metrics defined for model '{model_name}'"
    
    def test_links_not_empty(self, glm_models):
        """Test that all models have at least one link function."""
        for model_name, info in glm_models.model_mapping.items():
            assert len(info['links']) > 0, f"No links defined for model '{model_name}'"


class TestGLMRealDatasets:
    """Tests using real datasets from statsmodels."""
    
    def test_gaussian_glm_with_real_datasets(self, real_datasets):
        """Test Gaussian GLM with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            result = universal_glm(
                model_name="gaussian_glm",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars'][:2],
                link_name='identity'
            )
            
            assert result['success'] is True
            assert result['model_name'] == 'gaussian_glm'
            assert result['model_type'] == 'glm'
            assert 'metrics' in result
            assert 'diagnostics' in result
            
            # Check that AIC and BIC are finite (can be negative for well-fitting models)
            assert np.isfinite(result['metrics']['aic'])
            assert np.isfinite(result['metrics']['bic'])
            assert result['n_observations'] > 0
    
    def test_binomial_glm_with_real_datasets(self, real_datasets):
        """Test Binomial GLM with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            # Create binary outcome for binomial GLM
            data_binary = dataset_info['data'].copy()
            if len(dataset_info['independent_vars']) > 0:
                # Create binary outcome based on median of dependent variable
                median_val = data_binary[dataset_info['dependent_var']].median()
                data_binary['binary_y'] = (data_binary[dataset_info['dependent_var']] > median_val).astype(int)
                
                result = universal_glm(
                    model_name="binomial_glm",
                    data=data_binary,
                    dependent_var='binary_y',
                    independent_vars=dataset_info['independent_vars'][:2],
                    link_name='logit'
                )
                
                assert result['success'] is True
                assert result['model_name'] == 'binomial_glm'
                assert 'metrics' in result
    
    def test_poisson_glm_with_real_datasets(self, real_datasets):
        """Test Poisson GLM with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            # Create count outcome for Poisson GLM
            data_count = dataset_info['data'].copy()
            if len(dataset_info['independent_vars']) > 0:
                # Create count outcome based on absolute values
                data_count['count_y'] = np.abs(data_count[dataset_info['dependent_var']]).astype(int)
                
                result = universal_glm(
                    model_name="poisson_glm",
                    data=data_count,
                    dependent_var='count_y',
                    independent_vars=dataset_info['independent_vars'][:2],
                    link_name='log'
                )
                
                assert result['success'] is True
                assert result['model_name'] == 'poisson_glm'
                assert 'metrics' in result
    
    def test_gamma_glm_with_real_datasets(self, real_datasets):
        """Test Gamma GLM with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            # Create positive outcome for Gamma GLM
            data_positive = dataset_info['data'].copy()
            if len(dataset_info['independent_vars']) > 0:
                # Create positive outcome
                data_positive['positive_y'] = np.abs(data_positive[dataset_info['dependent_var']]) + 0.1
                
                result = universal_glm(
                    model_name="gamma_glm",
                    data=data_positive,
                    dependent_var='positive_y',
                    independent_vars=dataset_info['independent_vars'][:2],
                    link_name='log'
                )
                
                assert result['success'] is True
                assert result['model_name'] == 'gamma_glm'
                assert 'metrics' in result
    
    def test_formula_interface_with_real_datasets(self, real_datasets):
        """Test formula interface with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            # Create formula string
            formula = f"{dataset_info['dependent_var']} ~ {' + '.join(dataset_info['independent_vars'][:2])}"
            
            result = universal_glm(
                model_name="gaussian_glm",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                formula=formula,
                link_name='identity'
            )
            
            assert result['success'] is True
            assert result['model_name'] == 'gaussian_glm'
            assert 'metrics' in result
    
    def test_model_comparison(self, real_datasets):
        """Compare different GLM models on the same dataset."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        models_to_test = ['gaussian_glm']
        results = {}
        
        for model_name in models_to_test:
            result = universal_glm(
                model_name=model_name,
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars'][:2],
                link_name='identity'
            )
            
            assert result['success'] is True
            results[model_name] = result['metrics']['aic']
        
        # All models should produce valid AIC values
        for aic in results.values():
            assert aic > 0
    
    def test_diagnostic_analysis(self, real_datasets):
        """Test comprehensive diagnostic analysis on real datasets."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        # Use first available dataset
        dataset_name = list(real_datasets.keys())[0]
        dataset_info = real_datasets[dataset_name]
        
        result = universal_glm(
            model_name="gaussian_glm",
            data=dataset_info['data'],
            dependent_var=dataset_info['dependent_var'],
            independent_vars=dataset_info['independent_vars'],
            link_name='identity'
        )
        
        assert result['success'] is True
        assert 'diagnostics' in result
        
        diagnostics = result['diagnostics']
        
        # Check that diagnostic tests are present
        if 'residual_normality_p_value' in diagnostics:
            assert 0 <= diagnostics['residual_normality_p_value'] <= 1
        
        if 'deviance_residuals' in diagnostics:
            assert len(diagnostics['deviance_residuals']) > 0
    
    def test_binary_outcome_glm_with_real_datasets(self, real_datasets):
        """Test GLM models with binary outcomes created from real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            # Create binary outcome based on median
            data_binary = dataset_info['data'].copy()
            median_val = data_binary[dataset_info['dependent_var']].median()
            data_binary['binary_outcome'] = (data_binary[dataset_info['dependent_var']] > median_val).astype(int)
            
            result = universal_glm(
                model_name='binomial_glm',
                data=data_binary,
                dependent_var='binary_outcome',
                independent_vars=dataset_info['independent_vars'][:2],
                link_name='logit'
            )
            
            assert result['success'] is True
            assert result['model_name'] == 'binomial_glm'
            assert 'metrics' in result
            assert 'aic' in result['metrics']
    
    def test_comprehensive_glm_demonstration(self, real_datasets):
        """Comprehensive demonstration of GLM models with real datasets."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        for dataset_name, dataset_info in real_datasets.items():
            # Test Gaussian GLM (equivalent to OLS)
            result_gaussian = universal_glm(
                model_name='gaussian_glm',
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars'][:3],
                link_name='identity'
            )
            
            assert result_gaussian['success'] is True
            assert result_gaussian['model_name'] == 'gaussian_glm'
            assert 'metrics' in result_gaussian
            assert 'aic' in result_gaussian['metrics']
            assert 'deviance' in result_gaussian['metrics']
            
            # Test formula interface
            formula = f"{dataset_info['dependent_var']} ~ {' + '.join(dataset_info['independent_vars'][:2])}"
            result_formula = universal_glm(
                model_name='gaussian_glm',
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                formula=formula,
                link_name='identity'
            )
            
            assert result_formula['success'] is True
            assert 'metrics' in result_formula


class TestGLMEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        result = universal_glm(
            model_name='gaussian_glm',
            data=empty_df,
            dependent_var='y',
            independent_vars=['x1']
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_single_observation(self):
        """Test with single observation."""
        single_obs = pd.DataFrame({'y': [1.0], 'x1': [2.0]})
        
        result = universal_glm(
            model_name='gaussian_glm',
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
        
        result = universal_glm(
            model_name='gaussian_glm',
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
        
        result = universal_glm(
            model_name='gaussian_glm',
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
            
            result = universal_glm(
                model_name='gaussian_glm',
                data=test_data,
                dependent_var='realgdp',
                independent_vars=['realcons', 'realinv'],
                link_name='identity'
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
            
            result = universal_glm(
                model_name='gaussian_glm',
                data=large_data,
                dependent_var='y',
                independent_vars=['x1', 'x2'],
                link_name='identity'
            )
            
            assert result['success'] is True
            assert result['n_observations'] == n_samples


class TestGLMRealDatasetsExtended:
    """Test GLM models with real datasets for different families."""
    
    def test_gaussian_glm_with_real_datasets_extended(self, real_datasets):
        """Test Gaussian GLM with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            result = universal_glm(
                model_name="gaussian_glm",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars'][:3],
                link_name='identity'
            )
            
            assert result['success'] is True
            assert result['model_name'] == 'gaussian_glm'
            assert result['model_type'] == 'glm'
            assert 'metrics' in result
            assert 'diagnostics' in result
            
            # Check that AIC and BIC are finite (can be negative for well-fitting models)
            assert np.isfinite(result['metrics']['aic'])
            assert 'bic' in result['metrics']
            assert result['n_observations'] > 0
    
    def test_binomial_glm_with_real_datasets_extended(self, real_datasets):
        """Test Binomial GLM with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            # Create binary outcome for binomial GLM
            data_binary = dataset_info['data'].copy()
            if len(dataset_info['independent_vars']) > 0:
                # Create binary outcome based on median of dependent variable
                median_val = data_binary[dataset_info['dependent_var']].median()
                data_binary['binary_y'] = (data_binary[dataset_info['dependent_var']] > median_val).astype(int)
                
                result = universal_glm(
                    model_name="binomial_glm",
                    data=data_binary,
                    dependent_var='binary_y',
                    independent_vars=dataset_info['independent_vars'][:3],
                    link_name='logit'
                )
                
                assert result['success'] is True
                assert result['model_name'] == 'binomial_glm'
                assert 'metrics' in result
                # AIC can be NaN for perfect separation cases, but should be finite if not NaN
                if not np.isnan(result['metrics']['aic']):
                    assert result['metrics']['aic'] > 0
                assert 'bic' in result['metrics']
    
    def test_poisson_glm_with_real_datasets_extended(self, real_datasets):
        """Test Poisson GLM with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            # Create count outcome for Poisson GLM
            data_count = dataset_info['data'].copy()
            if len(dataset_info['independent_vars']) > 0:
                # Create count outcome based on absolute values
                data_count['count_y'] = np.abs(data_count[dataset_info['dependent_var']]).astype(int)
                
                result = universal_glm(
                    model_name="poisson_glm",
                    data=data_count,
                    dependent_var='count_y',
                    independent_vars=dataset_info['independent_vars'][:3],
                    link_name='log'
                )
                
                assert result['success'] is True
                assert result['model_name'] == 'poisson_glm'
                assert 'metrics' in result
                # AIC can be NaN for some edge cases, but should be finite if not NaN
                if not np.isnan(result['metrics']['aic']):
                    assert result['metrics']['aic'] > 0
                assert result['metrics']['deviance'] > 0
    
    def test_gamma_glm_with_real_datasets_extended(self, real_datasets):
        """Test Gamma GLM with real datasets."""
        for dataset_name, dataset_info in real_datasets.items():
            # Create positive outcome for Gamma GLM
            data_positive = dataset_info['data'].copy()
            if len(dataset_info['independent_vars']) > 0:
                # Create positive outcome
                data_positive['positive_y'] = np.abs(data_positive[dataset_info['dependent_var']]) + 0.1
                
                result = universal_glm(
                    model_name="gamma_glm",
                    data=data_positive,
                    dependent_var='positive_y',
                    independent_vars=dataset_info['independent_vars'][:3],
                    link_name='log'
                )
                
                assert result['success'] is True
                assert result['model_name'] == 'gamma_glm'
                assert 'metrics' in result
                # AIC can be NaN for some edge cases, but should be finite if not NaN
                if not np.isnan(result['metrics']['aic']):
                    assert result['metrics']['aic'] > 0
                assert result['metrics']['deviance'] > 0


if __name__ == "__main__":
    # Run all tests in this file
    pytest.main([__file__, "-v", "--tb=short"])
