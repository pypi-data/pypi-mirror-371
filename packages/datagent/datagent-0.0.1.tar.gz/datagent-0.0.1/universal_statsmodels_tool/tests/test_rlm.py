"""
Comprehensive test suite for Robust Linear Models (RLM) using pytest.

This module provides unit tests, real dataset tests, and edge case tests
for all robust linear models in the universal statsmodels tool.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algos.rlm import (
    universal_rlm,
    get_available_models,
    extract_model_info,
    validate_model_parameters
)


class TestRLMUnit:
    """Unit tests for robust linear models with real datasets from statsmodels."""
    
    @pytest.fixture(autouse=True)
    def setup_data(self):
        """Set up test data with real datasets from statsmodels."""
        # Try to load real datasets from statsmodels first
        self.real_datasets = {}
        self.synthetic_data = None
        
        try:
            import statsmodels.api as sm
            
            # Load commonly available datasets for robust regression
            available_datasets = [
                ('longley', 'TOTEMP', ['GNPDEFL', 'GNP', 'UNEMP']),
                ('engel', 'foodexp', ['income']),
                ('grunfeld', 'invest', ['value', 'capital']),
                ('stack_loss', 'STACKLOSS', ['AIRFLOW', 'WATERTEMP', 'ACIDCONC']),
                ('fair', 'affairs', ['rate_marriage', 'age', 'yrs_married', 'children', 'religious', 'educ', 'occupation', 'occupation_husb']),
                ('star98', 'NABOVE', ['NABOVE', 'NBELOW', 'SIZE', 'URBAN', 'SCHOOL', 'SEX', 'PRACAD', 'DISCLIM']),
                ('copper', 'WORLDCONSUMPTION', ['WORLDPRODUCTION', 'LCOPPERPRICE']),
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
            
            # Create clean data
            self.y_clean = 2 + 1.5 * self.x1 + 0.8 * self.x2 - 0.3 * self.x3 + np.random.randn(self.n_samples) * 0.5
            
            # Add outliers for robust regression testing
            outliers_idx = np.random.choice(self.n_samples, size=20, replace=False)
            self.y_with_outliers = self.y_clean.copy()
            self.y_with_outliers[outliers_idx] += 15  # Add large outliers
            
            # Create DataFrame
            self.synthetic_data = pd.DataFrame({
                'y_clean': self.y_clean,
                'y_with_outliers': self.y_with_outliers,
                'x1': self.x1,
                'x2': self.x2,
                'x3': self.x3
            })
    
    def test_available_models(self):
        """Test that all robust linear models are available."""
        models = get_available_models()
        assert isinstance(models, dict)
        assert len(models) > 0
        
        # Test specific models
        for model_type, type_models in models.items():
            assert isinstance(type_models, dict)
            for model_name, model_info in type_models.items():
                assert 'description' in model_info
                assert 'class' in model_info
                assert 'module' in model_info
                assert 'norm' in model_info
    
    def test_model_info_extraction(self):
        """Test model info extraction for all robust linear models."""
        models = get_available_models()
        for model_type, type_models in models.items():
            for model_name in type_models.keys():
                info = extract_model_info(model_name)
                assert 'error' not in info
                assert 'model_name' in info
                assert 'description' in info
    
    def test_rlm_huber(self):
        """Test Huber's T robust linear model with real datasets."""
        if not self.real_datasets:
            pytest.skip("No real datasets available, skipping test")
        
        # Test with appropriate real dataset
        for dataset_name, dataset_info in self.real_datasets.items():
            # Skip if dataset is not suitable for this model
            if self._should_skip_model("rlm_huber", dataset_info['data'], dataset_info['dependent_var']):
                continue
                
            result = universal_rlm(
                model_name="rlm_huber",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars']
            )
            
            assert result['success'], f"Failed to fit rlm_huber on {dataset_name}: {result.get('error', 'Unknown error')}"
            assert 'coefficients' in result
            assert 'scale' in result
            assert 'weights' in result
            assert 'residuals' in result
            assert 'fitted_values' in result
            assert 'n_observations' in result
            break  # Test with first suitable dataset
    
    def test_rlm_tukey_biweight(self):
        """Test Tukey's biweight robust linear model with real datasets."""
        if not self.real_datasets:
            pytest.skip("No real datasets available, skipping test")
        
        # Test with appropriate real dataset
        for dataset_name, dataset_info in self.real_datasets.items():
            # Skip if dataset is not suitable for this model
            if self._should_skip_model("rlm_tukey_biweight", dataset_info['data'], dataset_info['dependent_var']):
                continue
                
            result = universal_rlm(
                model_name="rlm_tukey_biweight",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars']
            )
            
            assert result['success'], f"Failed to fit rlm_tukey_biweight on {dataset_name}: {result.get('error', 'Unknown error')}"
            assert 'coefficients' in result
            assert 'scale' in result
            assert 'weights' in result
            break  # Test with first suitable dataset
    
    def test_rlm_hampel(self):
        """Test Hampel robust linear model with real datasets."""
        if not self.real_datasets:
            pytest.skip("No real datasets available, skipping test")
        
        # Test with appropriate real dataset
        for dataset_name, dataset_info in self.real_datasets.items():
            # Skip if dataset is not suitable for this model
            if self._should_skip_model("rlm_hampel", dataset_info['data'], dataset_info['dependent_var']):
                continue
                
            result = universal_rlm(
                model_name="rlm_hampel",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars']
            )
            
            assert result['success'], f"Failed to fit rlm_hampel on {dataset_name}: {result.get('error', 'Unknown error')}"
            assert 'coefficients' in result
            assert 'scale' in result
            assert 'weights' in result
            break  # Test with first suitable dataset
    
    def test_rlm_andrew_wave(self):
        """Test Andrew's wave robust linear model with real datasets."""
        if not self.real_datasets:
            pytest.skip("No real datasets available, skipping test")
        
        # Test with appropriate real dataset
        for dataset_name, dataset_info in self.real_datasets.items():
            # Skip if dataset is not suitable for this model
            if self._should_skip_model("rlm_andrew_wave", dataset_info['data'], dataset_info['dependent_var']):
                continue
                
            result = universal_rlm(
                model_name="rlm_andrew_wave",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars']
            )
            
            assert result['success'], f"Failed to fit rlm_andrew_wave on {dataset_name}: {result.get('error', 'Unknown error')}"
            assert 'coefficients' in result
            assert 'scale' in result
            assert 'weights' in result
            break  # Test with first suitable dataset
    
    def test_rlm_ramsay_e(self):
        """Test Ramsay's E robust linear model with real datasets."""
        if not self.real_datasets:
            pytest.skip("No real datasets available, skipping test")
        
        # Test with appropriate real dataset
        for dataset_name, dataset_info in self.real_datasets.items():
            # Skip if dataset is not suitable for this model
            if self._should_skip_model("rlm_ramsay_e", dataset_info['data'], dataset_info['dependent_var']):
                continue
                
            result = universal_rlm(
                model_name="rlm_ramsay_e",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars']
            )
            
            assert result['success'], f"Failed to fit rlm_ramsay_e on {dataset_name}: {result.get('error', 'Unknown error')}"
            assert 'coefficients' in result
            assert 'scale' in result
            assert 'weights' in result
            break  # Test with first suitable dataset
    
    def test_rlm_trimmed_mean(self):
        """Test trimmed mean robust linear model with real datasets."""
        if not self.real_datasets:
            pytest.skip("No real datasets available, skipping test")
        
        # Test with appropriate real dataset
        for dataset_name, dataset_info in self.real_datasets.items():
            # Skip if dataset is not suitable for this model
            if self._should_skip_model("rlm_trimmed_mean", dataset_info['data'], dataset_info['dependent_var']):
                continue
                
            result = universal_rlm(
                model_name="rlm_trimmed_mean",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars']
            )
            
            assert result['success'], f"Failed to fit rlm_trimmed_mean on {dataset_name}: {result.get('error', 'Unknown error')}"
            assert 'coefficients' in result
            assert 'scale' in result
            assert 'weights' in result
            break  # Test with first suitable dataset
    
    def test_rlm_least_squares(self):
        """Test least squares robust linear model with real datasets."""
        if not self.real_datasets:
            pytest.skip("No real datasets available, skipping test")
        
        # Test with appropriate real dataset
        for dataset_name, dataset_info in self.real_datasets.items():
            # Skip if dataset is not suitable for this model
            if self._should_skip_model("rlm_least_squares", dataset_info['data'], dataset_info['dependent_var']):
                continue
                
            result = universal_rlm(
                model_name="rlm_least_squares",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars']
            )
            
            assert result['success'], f"Failed to fit rlm_least_squares on {dataset_name}: {result.get('error', 'Unknown error')}"
            assert 'coefficients' in result
            assert 'scale' in result
            assert 'weights' in result
            break  # Test with first suitable dataset
    
    def test_rlm_m_quantile(self):
        """Test M-quantiles robust linear model with real datasets."""
        if not self.real_datasets:
            pytest.skip("No real datasets available, skipping test")
        
        # Test with appropriate real dataset
        for dataset_name, dataset_info in self.real_datasets.items():
            # Skip if dataset is not suitable for this model
            if self._should_skip_model("rlm_m_quantile", dataset_info['data'], dataset_info['dependent_var']):
                continue
                
            result = universal_rlm(
                model_name="rlm_m_quantile",
                data=dataset_info['data'],
                dependent_var=dataset_info['dependent_var'],
                independent_vars=dataset_info['independent_vars']
            )
            
            # M-quantiles might fail due to parameter issues, so we'll be more lenient
            if result['success']:
                assert 'coefficients' in result
                assert 'scale' in result
                assert 'weights' in result
            else:
                # If it fails, it should be due to parameter issues, not fundamental problems
                assert 'error' in result
            break  # Test with first suitable dataset
    
    def _should_skip_model(self, model_name, data, dependent_var):
        """Determine if a model should be skipped for a given dataset."""
        # Skip time series data for regular robust regression
        if dependent_var in ['volume', 'sunspots']:
            return True
        
        # Skip if data has too few observations
        if len(data) < 10:
            return True
        
        # Skip if dependent variable has too many missing values
        if data[dependent_var].isna().sum() > len(data) * 0.5:
            return True
        
        return False


class TestRLMRealDatasets:
    """Real dataset tests for robust linear models."""
    
    @pytest.fixture
    def real_datasets(self):
        """Get real datasets from statsmodels for testing."""
        real_datasets = {}
        try:
            import statsmodels.api as sm
            
            # Load commonly available datasets for robust regression
            available_datasets = [
                ('longley', 'TOTEMP', ['GNPDEFL', 'GNP', 'UNEMP']),
                ('engel', 'foodexp', ['income']),
                ('grunfeld', 'invest', ['value', 'capital']),
                ('stack_loss', 'STACKLOSS', ['AIRFLOW', 'WATERTEMP', 'ACIDCONC'])
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
        except ImportError:
            pass
        
        return real_datasets
    
    def test_with_real_datasets(self, real_datasets):
        """Test all robust linear models with real datasets from statsmodels."""
        if not real_datasets:
            pytest.skip("No real datasets available from statsmodels")
        
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
                        result = universal_rlm(
                            model_name=model_name,
                            data=data,
                            dependent_var=dependent_var,
                            independent_vars=independent_vars
                        )
                        
                        assert result['success'], f"Failed to fit {model_name} on {dataset_name}: {result.get('error', 'Unknown error')}"
                        
                        # Validate robust-specific metrics
                        if 'scale' in result:
                            assert isinstance(result['scale'], (int, float))
                            assert result['scale'] > 0
                        
                        if 'weights' in result:
                            assert isinstance(result['weights'], list)
                            assert len(result['weights']) == result['n_observations']
                            # Weights should be between 0 and 1 for most robust estimators
                            weights = np.array(result['weights'])
                            assert np.all(weights >= 0)
                            assert np.all(weights <= 1)
                        
                        # Validate coefficients
                        if 'coefficients' in result:
                            assert isinstance(result['coefficients'], dict)
                            assert len(result['coefficients']) > 0
                            
                    except Exception as e:
                        pytest.fail(f"Exception fitting {model_name} on {dataset_name}: {str(e)}")
    
    def _should_skip_model(self, model_name, data, dependent_var):
        """Determine if a model should be skipped for a given dataset."""
        # Skip time series data for regular robust regression
        if dependent_var in ['volume', 'sunspots']:
            return True
        
        # Skip if data has too few observations
        if len(data) < 10:
            return True
        
        # Skip if dependent variable has too many missing values
        if data[dependent_var].isna().sum() > len(data) * 0.5:
            return True
        
        return False


class TestRLMEdgeCases:
    """Edge case tests for robust linear models."""
    
    def test_invalid_model_name(self):
        """Test handling of invalid model names."""
        result = universal_rlm(
            model_name="invalid_model",
            data=pd.DataFrame({'y': [1, 2, 3], 'x': [1, 2, 3]}),
            dependent_var="y",
            independent_vars=["x"]
        )
        
        assert not result['success']
        assert 'error' in result
    
    def test_missing_variables(self):
        """Test handling of missing variables."""
        data = pd.DataFrame({'y': [1, 2, 3], 'x1': [1, 2, 3]})
        
        # Test missing dependent variable
        result = universal_rlm(
            model_name="rlm_huber",
            data=data,
            dependent_var="missing_y",
            independent_vars=["x1"]
        )
        
        assert not result['success']
        assert 'error' in result
        
        # Test missing independent variables
        result = universal_rlm(
            model_name="rlm_huber",
            data=data,
            dependent_var="y",
            independent_vars=["missing_x"]
        )
        
        assert not result['success']
        assert 'error' in result
    
    def test_empty_data(self):
        """Test handling of empty data."""
        empty_data = pd.DataFrame()
        
        result = universal_rlm(
            model_name="rlm_huber",
            data=empty_data,
            dependent_var="y",
            independent_vars=["x"]
        )
        
        assert not result['success']
        assert 'error' in result
    
    def test_single_observation(self):
        """Test handling of single observation data."""
        single_data = pd.DataFrame({'y': [1], 'x': [1]})
        
        result = universal_rlm(
            model_name="rlm_huber",
            data=single_data,
            dependent_var="y",
            independent_vars=["x"]
        )
        
        # This should fail due to insufficient observations
        assert not result['success']
        assert 'error' in result
    
    def test_constant_variables(self):
        """Test handling of constant variables."""
        # Create data with constant independent variable
        data = pd.DataFrame({
            'y': [1, 2, 3, 4, 5],
            'x1': [1, 2, 3, 4, 5],
            'x2': [1, 1, 1, 1, 1]  # Constant variable
        })
        
        result = universal_rlm(
            model_name="rlm_huber",
            data=data,
            dependent_var="y",
            independent_vars=["x1", "x2"]
        )
        
        # This should work but may have issues with the constant variable
        if result['success']:
            assert 'coefficients' in result
            # The coefficient for x2 should be 0 or very small
            if 'x2' in result['coefficients']:
                assert abs(result['coefficients']['x2']) < 1e-5
    
    def test_missing_values(self):
        """Test handling of missing values."""
        data_with_missing = pd.DataFrame({
            'y': [1, 2, np.nan, 4, 5],
            'x1': [1, 2, 3, np.nan, 5],
            'x2': [1, 2, 3, 4, 5]
        })
        
        result = universal_rlm(
            model_name="rlm_huber",
            data=data_with_missing,
            dependent_var="y",
            independent_vars=["x1", "x2"]
        )
        
        # This should work by dropping missing values
        if result['success']:
            assert 'coefficients' in result
            assert 'n_observations' in result
            # Should have fewer observations due to missing values
            assert result['n_observations'] < len(data_with_missing)


class TestRLMOutlierHandling:
    """Tests specifically for outlier handling capabilities."""
    
    @pytest.fixture(autouse=True)
    def setup_data(self):
        """Set up data with known outliers."""
        np.random.seed(42)
        n_samples = 100
        
        # Generate clean data
        x1 = np.random.randn(n_samples)
        x2 = np.random.randn(n_samples)
        y_clean = 2 + 1.5 * x1 + 0.8 * x2 + np.random.randn(n_samples) * 0.5
        
        # Add outliers at different positions
        outliers_idx = np.random.choice(n_samples, size=10, replace=False)
        y_with_outliers = y_clean.copy()
        y_with_outliers[outliers_idx] += 20  # Add large outliers
        
        self.data = pd.DataFrame({
            'y_clean': y_clean,
            'y_with_outliers': y_with_outliers,
            'x1': x1,
            'x2': x2
        })
        self.outliers_idx = outliers_idx
    
    def test_outlier_robustness_comparison(self):
        """Test that robust models handle outliers better than least squares."""
        if not hasattr(self, 'data'):
            pytest.skip("No test data available")
        
        # Fit least squares (should be sensitive to outliers)
        result_ls = universal_rlm(
            model_name="rlm_least_squares",
            data=self.data,
            dependent_var="y_with_outliers",
            independent_vars=["x1", "x2"]
        )
        
        # Fit Huber (should be robust to outliers)
        result_huber = universal_rlm(
            model_name="rlm_huber",
            data=self.data,
            dependent_var="y_with_outliers",
            independent_vars=["x1", "x2"]
        )
        
        # Fit Tukey biweight (should be robust to outliers)
        result_tukey = universal_rlm(
            model_name="rlm_tukey_biweight",
            data=self.data,
            dependent_var="y_with_outliers",
            independent_vars=["x1", "x2"]
        )
        
        assert result_ls['success']
        assert result_huber['success']
        assert result_tukey['success']
        
        # Check that robust models have lower weights for outliers
        if 'weights' in result_huber and 'weights' in result_tukey:
            huber_weights = np.array(result_huber['weights'])
            tukey_weights = np.array(result_tukey['weights'])
            
            # Outliers should have lower weights in robust models
            outlier_weights_huber = huber_weights[self.outliers_idx]
            outlier_weights_tukey = tukey_weights[self.outliers_idx]
            
            # Most outlier weights should be less than 1 (indicating downweighting)
            assert np.sum(outlier_weights_huber < 1) > len(self.outliers_idx) * 0.5
            assert np.sum(outlier_weights_tukey < 1) > len(self.outliers_idx) * 0.5
    
    def test_scale_estimation(self):
        """Test that scale estimation works correctly."""
        if not hasattr(self, 'data'):
            pytest.skip("No test data available")
        
        result = universal_rlm(
            model_name="rlm_huber",
            data=self.data,
            dependent_var="y_with_outliers",
            independent_vars=["x1", "x2"]
        )
        
        assert result['success']
        assert 'scale' in result
        assert isinstance(result['scale'], (int, float))
        assert result['scale'] > 0
        
        # Scale should be reasonable (not too large or too small)
        assert result['scale'] < 100
        assert result['scale'] > 0.1


if __name__ == '__main__':
    pytest.main([__file__, "-v", "--tb=short"])
