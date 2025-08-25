"""
Comprehensive test suite for ANOVA models using pytest.

This module provides unit tests, real dataset tests, and edge case tests
for all ANOVA models in the universal statsmodels tool.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algos.anova import (
    universal_anova,
    get_available_models,
    extract_model_info,
    validate_model_parameters
)


class TestANOVAUnit:
    """Unit tests for ANOVA models with real datasets from statsmodels."""
    
    @pytest.fixture(autouse=True)
    def setup_data(self):
        """Set up test data with real datasets from statsmodels."""
        # Try to load real datasets from statsmodels first
        self.real_datasets = {}
        self.synthetic_data = None
        
        try:
            import statsmodels.api as sm
            
            # Load commonly available datasets for ANOVA testing
            available_datasets = [
                ('longley', 'TOTEMP', ['GNPDEFL', 'GNP', 'UNEMP']),
                ('engel', 'foodexp', ['income']),
                ('grunfeld', 'invest', ['value', 'capital']),
                ('scotland', 'YES', ['COUTAX', 'UNEMPF', 'MOR', 'ACT', 'GDP', 'AGE']),
                ('star98', 'NABOVE', ['NBELOW', 'SIZE', 'URBAN', 'SCHOOL', 'SEX']),
                ('fair', 'affairs', ['rate_marriage', 'age', 'yrs_married', 'children', 'religious', 'educ']),
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
        """Test that all ANOVA models are available."""
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
    
    def test_model_info_extraction(self):
        """Test model info extraction for all ANOVA models."""
        models = get_available_models()
        for model_type, type_models in models.items():
            for model_name in type_models.keys():
                info = extract_model_info(model_name)
                assert 'error' not in info
                assert 'model_name' in info
                assert 'description' in info
    
    def test_anova_lm(self):
        """Test anova_lm with real datasets from statsmodels."""
        if not self.real_datasets:
            pytest.skip("No real datasets available, skipping test")
        
        # Test with appropriate real dataset
        for dataset_name, dataset_info in self.real_datasets.items():
            # Skip if dataset is not suitable for ANOVA
            if self._should_skip_model("anova_lm", dataset_info['data'], dataset_info['dependent_var']):
                continue
                
            # Test with formula interface
            formula = f"{dataset_info['dependent_var']} ~ {' + '.join(dataset_info['independent_vars'][:2])}"
            
            result = universal_anova(
                model_name="anova_lm",
                data=dataset_info['data'],
                formula=formula,
                typ=2
            )
            
            assert result['success'], f"Failed to fit anova_lm on {dataset_name}: {result.get('error', 'Unknown error')}"
            assert 'metrics' in result
            assert 'fitted_model' in result
            assert 'anova_table' in result
            
            # Validate ANOVA results
            metrics = result['metrics']
            assert 'sum_squares' in metrics
            assert 'degrees_of_freedom' in metrics
            assert 'f_statistics' in metrics
            assert 'p_values' in metrics
            break  # Test with first suitable dataset
    
    def test_anova_rm(self):
        """Test anova_rm with synthetic repeated measures data."""
        # Create repeated measures data - properly structured
        np.random.seed(42)
        n_subjects = 15
        n_conditions = 3
        
        data_rm = []
        for subject in range(1, n_subjects + 1):
            for condition in ['A', 'B', 'C']:
                data_rm.append({
                    'subject': subject,
                    'condition': condition,
                    'value': np.random.randn()
                })
        data_rm = pd.DataFrame(data_rm)
        
        result = universal_anova(
            model_name="anova_rm",
            data=data_rm,
            dependent_var="value",
            subject_var="subject",
            within_factors=["condition"]
        )
        
        assert result['success'], f"Failed to fit anova_rm: {result.get('error', 'Unknown error')}"
        assert 'metrics' in result
        assert 'fitted_model' in result
        assert 'anova_table' in result
        
        # Validate ANOVA results
        metrics = result['metrics']
        assert 'sum_squares' in metrics
        assert 'degrees_of_freedom' in metrics
        assert 'f_statistics' in metrics
        assert 'p_values' in metrics
    
    def _should_skip_model(self, model_name, data, dependent_var):
        """Determine if a model should be skipped for a given dataset."""
        # Skip time series data for ANOVA
        if dependent_var in ['volume', 'sunspots']:
            return True
        return False


class TestANOVARealDatasets:
    """Real dataset tests for ANOVA models."""
    
    def test_with_real_datasets(self, real_datasets):
        """Test ANOVA models with real datasets from statsmodels."""
        if not real_datasets:
            pytest.skip("No real datasets available")
        
        models = get_available_models()
        
        for dataset_name, dataset_info in real_datasets.items():
            data = dataset_info['data']
            dependent_var = dataset_info['dependent_var']
            independent_vars = dataset_info['independent_vars']
            
            # Test anova_lm
            try:
                # Check if variables exist in the dataset
                available_vars = [var for var in independent_vars[:2] if var in data.columns]
                if not available_vars:
                    continue  # Skip if no variables are available
                
                formula = f"{dependent_var} ~ {' + '.join(available_vars)}"
                
                result = universal_anova(
                    model_name="anova_lm",
                    data=data,
                    formula=formula,
                    typ=2
                )
                
                assert result['success'], f"Failed to fit anova_lm on {dataset_name}: {result.get('error', 'Unknown error')}"
                
                # Validate metrics
                if 'metrics' in result:
                    metrics = result['metrics']
                    assert isinstance(metrics['sum_squares'], dict)
                    assert isinstance(metrics['degrees_of_freedom'], dict)
                    assert isinstance(metrics['f_statistics'], dict)
                    assert isinstance(metrics['p_values'], dict)
                    
            except Exception as e:
                pytest.fail(f"Exception fitting anova_lm on {dataset_name}: {str(e)}")


class TestANOVAEdgeCases:
    """Edge case tests for ANOVA models."""
    
    def test_invalid_model_name(self):
        """Test handling of invalid model names."""
        result = universal_anova(
            model_name="invalid_model",
            data=pd.DataFrame({'y': [1, 2, 3], 'x': [1, 2, 3]}),
            formula="y ~ x"
        )
        
        assert not result['success']
        assert 'error' in result
    
    def test_missing_variables(self):
        """Test handling of missing variables."""
        data = pd.DataFrame({'y': [1, 2, 3], 'x1': [1, 2, 3]})
        
        # Test missing dependent variable in formula
        result = universal_anova(
            model_name="anova_lm",
            data=data,
            formula="missing_y ~ x1"
        )
        
        assert not result['success']
        assert 'error' in result
        
        # Test missing independent variables in formula
        result = universal_anova(
            model_name="anova_lm",
            data=data,
            formula="y ~ missing_x"
        )
        
        assert not result['success']
        assert 'error' in result
    
    def test_empty_data(self):
        """Test handling of empty data."""
        empty_data = pd.DataFrame()
        
        result = universal_anova(
            model_name="anova_lm",
            data=empty_data,
            formula="y ~ x"
        )
        
        assert not result['success']
        assert 'error' in result
    
    def test_anova_rm_missing_subject(self):
        """Test anova_rm with missing subject variable."""
        data = pd.DataFrame({
            'value': [1, 2, 3, 4, 5, 6],
            'condition': ['A', 'B', 'A', 'B', 'A', 'B']
        })
        
        result = universal_anova(
            model_name="anova_rm",
            data=data,
            dependent_var="value",
            subject_var="missing_subject",
            within_factors=["condition"]
        )
        
        assert not result['success']
        assert 'error' in result
    
    def test_anova_rm_missing_dependent(self):
        """Test anova_rm with missing dependent variable."""
        data = pd.DataFrame({
            'subject': [1, 1, 2, 2, 3, 3],
            'condition': ['A', 'B', 'A', 'B', 'A', 'B']
        })
        
        result = universal_anova(
            model_name="anova_rm",
            data=data,
            dependent_var="missing_value",
            subject_var="subject",
            within_factors=["condition"]
        )
        
        assert not result['success']
        assert 'error' in result
    
    def test_parameter_validation(self):
        """Test parameter validation for ANOVA models."""
        # Test anova_lm parameter validation
        validation = validate_model_parameters("anova_lm", {"typ": 5})
        assert validation["valid"]
        assert len(validation["warnings"]) > 0
        
        validation = validate_model_parameters("anova_lm", {"test": "invalid"})
        assert validation["valid"]
        assert len(validation["warnings"]) > 0
        
        # Test anova_rm parameter validation
        validation = validate_model_parameters("anova_rm", {"aggregate_func": "invalid"})
        assert validation["valid"]
        assert len(validation["warnings"]) > 0
        
        # Test unknown model
        validation = validate_model_parameters("unknown_model", {})
        assert not validation["valid"]
        assert "error" in validation


class TestANOVASyntheticData:
    """Synthetic data tests for ANOVA models when real datasets are unavailable."""
    
    @pytest.fixture(autouse=True)
    def setup_synthetic_data(self):
        """Set up synthetic data for testing."""
        np.random.seed(42)
        
        # Create synthetic data for anova_lm
        n_samples = 100
        self.data_lm = pd.DataFrame({
            'y': np.random.randn(n_samples),
            'group': np.random.choice(['A', 'B', 'C'], n_samples),
            'x1': np.random.randn(n_samples),
            'x2': np.random.randn(n_samples)
        })
        
        # Create synthetic data for anova_rm - properly structured
        n_subjects = 20
        n_conditions = 3
        
        data_rm = []
        for subject in range(1, n_subjects + 1):
            for condition in ['A', 'B', 'C']:
                data_rm.append({
                    'subject': subject,
                    'condition': condition,
                    'value': np.random.randn()
                })
        self.data_rm = pd.DataFrame(data_rm)
    
    def test_anova_lm_synthetic(self):
        """Test anova_lm with synthetic data."""
        result = universal_anova(
            model_name="anova_lm",
            data=self.data_lm,
            formula="y ~ group + x1 + x2",
            typ=2
        )
        
        assert result['success']
        assert 'metrics' in result
        assert 'fitted_model' in result
        
        # Validate results structure
        metrics = result['metrics']
        assert 'sum_squares' in metrics
        assert 'degrees_of_freedom' in metrics
        assert 'f_statistics' in metrics
        assert 'p_values' in metrics
    
    def test_anova_rm_synthetic(self):
        """Test anova_rm with synthetic data."""
        result = universal_anova(
            model_name="anova_rm",
            data=self.data_rm,
            dependent_var="value",
            subject_var="subject",
            within_factors=["condition"]
        )
        
        assert result['success']
        assert 'metrics' in result
        assert 'fitted_model' in result
        
        # Validate results structure
        metrics = result['metrics']
        assert 'sum_squares' in metrics
        assert 'degrees_of_freedom' in metrics
        assert 'f_statistics' in metrics
        assert 'p_values' in metrics
    
    def test_different_anova_types(self):
        """Test different ANOVA types with synthetic data."""
        for typ in [1, 2, 3]:
            result = universal_anova(
                model_name="anova_lm",
                data=self.data_lm,
                formula="y ~ group + x1 + x2",
                typ=typ
            )
            
            assert result['success'], f"Failed with typ={typ}"
            assert 'metrics' in result
    
    def test_different_test_statistics(self):
        """Test different test statistics with synthetic data."""
        for test in ["F"]:  # Only test F statistic as Chisq may not be supported
            result = universal_anova(
                model_name="anova_lm",
                data=self.data_lm,
                formula="y ~ group + x1 + x2",
                test=test
            )
            
            assert result['success'], f"Failed with test={test}"
            assert 'metrics' in result


if __name__ == '__main__':
    pytest.main([__file__, "-v", "--tb=short"])
