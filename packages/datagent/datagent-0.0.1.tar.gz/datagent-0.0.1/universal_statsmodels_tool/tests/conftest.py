import pytest
import numpy as np
import pandas as pd


@pytest.fixture(scope="session")
def real_datasets():
    """Load real datasets for testing."""
    datasets = {}
    
    try:
        import statsmodels.api as sm
        
        # Load available datasets with correct column names
        available_datasets = [
            ('longley', 'TOTEMP', ['GNPDEFL', 'GNP', 'UNEMP', 'ARMED', 'POP', 'YEAR']),
            ('star98', 'NABOVE', ['LOWINC', 'PERASIAN', 'PERBLACK', 'PERHISP', 'PERMINTE']),
            ('engel', 'foodexp', ['income']),
            ('grunfeld', 'invest', ['value', 'capital']),
            ('statecrime', 'murder', ['poverty', 'white', 'hs_grad', 'single', 'urban']),
            ('copper', 'COPPERPRICE', ['WORLDCONSUMPTION', 'INCOMEINDEX', 'ALUMPRICE', 'INVENTORYINDEX', 'TIME']),
            ('stackloss', 'stackloss', ['air_flow', 'water_temp', 'acid_conc']),
            ('spector', 'grade', ['gpa', 'tuce', 'psi']),
            ('fair', 'affairs', ['rate_marriage', 'age', 'yrs_married', 'children', 'religious', 'educ', 'occupation', 'occupation_husb']),
            ('ccard', 'AVGEXP', ['AGE', 'INCOME', 'INCOMESQ', 'OWNRENT']),
            ('cancer', 'time', ['age', 'sex', 'ph_ecog', 'ph_karno', 'pat_karno', 'meal_cal', 'wt_loss']),
            ('heart', 'survival', ['age', 'sex', 'chol', 'sbp', 'tobacco', 'ldl', 'adiposity', 'famhist', 'typea', 'obesity', 'alcohol', 'ecg']),
            ('nile', 'volume', ['year']),
            ('sunspots', 'sunspots', ['year']),
            ('macrodata', 'realgdp', ['realcons', 'realinv', 'realgovt', 'realdpi', 'cpi_u', 'm1', 'tbilrate', 'unemp', 'pop', 'infl', 'realint'])
        ]
        
        for dataset_name, dep_var, indep_vars in available_datasets:
            try:
                dataset = getattr(sm.datasets, dataset_name).load_pandas()
                # Check if the dependent variable exists in the dataset
                if dep_var in dataset.data.columns:
                    datasets[dataset_name] = {
                        'data': dataset.data,
                        'dependent_var': dep_var,
                        'independent_vars': [var for var in indep_vars if var in dataset.data.columns]
                    }
            except (AttributeError, KeyError):
                # Skip if dataset not available or columns don't exist
                continue
        
    except ImportError:
        # If statsmodels not available, create synthetic data
        np.random.seed(42)
        n_samples = 100
        
        for i in range(4):
            dataset_name = f'synthetic_{i}'
            x1 = np.random.randn(n_samples)
            x2 = np.random.randn(n_samples)
            y = 2 + 1.5 * x1 + 0.8 * x2 + np.random.randn(n_samples) * 0.5
            
            datasets[dataset_name] = {
                'data': pd.DataFrame({'y': y, 'x1': x1, 'x2': x2}),
                'dependent_var': 'y',
                'independent_vars': ['x1', 'x2']
            }
    
    return datasets
