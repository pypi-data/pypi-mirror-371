# Testing the Universal Estimator Module

This document describes how to run tests for the universal estimator module using pytest.

## Test Structure

The tests are organized into several test classes:

### 1. `TestUniversalEstimator`
Tests the main `universal_estimator` function:
- **Basic functionality**: Random Forest, Linear Regression, K-Means, PCA
- **Error handling**: Invalid estimator names, missing target columns
- **Data validation**: Required parameters for supervised learning

### 2. `TestUtilityFunctions`
Tests utility functions:
- `get_available_estimators()`
- `extract_estimator_info()`
- `get_estimator_tool_description()`
- `validate_estimator_parameters()`
- `create_langgraph_tool()`

### 3. `TestEstimatorTypes`
Tests different types of estimators using parameterization:
- **Classifiers**: Logistic Regression, SVM, KNN, Naive Bayes
- **Regressors**: Ridge, Lasso, SVR, KNN Regressor
- **Clustering**: DBSCAN, Agglomerative Clustering
- **Preprocessors**: Truncated SVD, Factor Analysis

### 4. `TestDataHandling`
Tests data preprocessing capabilities:
- Categorical variable handling
- Missing value handling

## Running Tests

### Prerequisites

Install the required testing dependencies:

```bash
pip install -r test_requirements.txt
```

### Basic Test Execution

#### Using pytest directly:
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test class
python -m pytest test_universal_estimator.py::TestUniversalEstimator -v

# Run specific test method
python -m pytest test_universal_estimator.py::TestUniversalEstimator::test_random_forest_classifier -v
```

#### Using the test runner script:
```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py -v

# Run with coverage
python run_tests.py -c

# Run with coverage and HTML report
python run_tests.py -c --html
```

### Test Coverage

To check test coverage:

```bash
# Basic coverage report
python -m pytest --cov=universal_estimator --cov-report=term-missing

# HTML coverage report
python -m pytest --cov=universal_estimator --cov-report=html

# Using the test runner
python run_tests.py -c --html
```

The HTML report will be generated in the `htmlcov/` directory.

## Test Configuration

The tests use a `pytest.ini` configuration file that includes:

- **Test discovery**: Automatically finds test files and classes
- **Output options**: Verbose output, short tracebacks, colored output
- **Markers**: Custom markers for slow, integration, and unit tests
- **Warning filters**: Suppresses common warnings

## Test Fixtures

### `sample_data` fixture
Creates sample datasets for testing:
- **Classification data**: 100 samples, 5 features, 3 classes
- **Regression data**: 100 samples, 5 features, continuous target
- **Clustering data**: 100 samples, 5 features (no target)

## Test Categories

### Unit Tests
- Individual function testing
- Parameter validation
- Error handling
- Utility functions

### Integration Tests
- End-to-end estimator training
- Data preprocessing pipeline
- Metric calculation
- Feature importance extraction

### Data Handling Tests
- Categorical variable encoding
- Missing value imputation
- Data type handling
- Train/test splitting

## Expected Test Results

### All Tests Should Pass
- ✅ 31 tests total
- ✅ All estimator types working
- ✅ Error handling functioning
- ✅ Utility functions working
- ✅ Data preprocessing working

### Coverage Target
- **Current**: ~69% code coverage
- **Target**: >80% code coverage
- **Critical paths**: 100% coverage

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the correct directory
   cd universal_sklearn_tool
   
   # Install dependencies
   pip install -r test_requirements.txt
   ```

2. **Missing Dependencies**
   ```bash
   # Install scikit-learn and other dependencies
   pip install scikit-learn pandas numpy pytest
   ```

3. **Test Failures**
   - Check that all required packages are installed
   - Ensure you have the latest version of scikit-learn
   - Verify that the universal_estimator.py file is in the same directory

### Debugging Tests

To debug a failing test:

```bash
# Run with maximum verbosity
python -m pytest -vvv test_universal_estimator.py::TestUniversalEstimator::test_random_forest_classifier

# Run with print statements visible
python -m pytest -s test_universal_estimator.py::TestUniversalEstimator::test_random_forest_classifier

# Run with debugger
python -m pytest --pdb test_universal_estimator.py::TestUniversalEstimator::test_random_forest_classifier
```

## Adding New Tests

### Test Naming Convention
- Test classes: `TestClassName`
- Test methods: `test_method_name`
- Test files: `test_*.py`

### Example Test Structure
```python
class TestNewFeature:
    """Test class for new feature."""
    
    def test_basic_functionality(self, sample_data):
        """Test basic functionality."""
        result = universal_estimator(
            estimator_name="new_estimator",
            data=sample_data['classification'],
            target_column="target"
        )
        
        assert result['success'] is True
        assert result['estimator_type'] == "classifier"
```

### Running New Tests
```bash
# Run only new tests
python -m pytest test_universal_estimator.py::TestNewFeature -v

# Run with coverage
python -m pytest test_universal_estimator.py::TestNewFeature --cov=universal_estimator
```

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Install dependencies
pip install -r test_requirements.txt

# Run tests with coverage
python -m pytest --cov=universal_estimator --cov-report=xml --cov-report=term-missing

# Run tests in parallel (if needed)
python -m pytest -n auto
```

## Performance Testing

For performance testing, add the `@pytest.mark.slow` marker:

```python
@pytest.mark.slow
def test_large_dataset_performance(self):
    """Test performance with large datasets."""
    # Test with larger datasets
    pass
```

Run without slow tests:
```bash
python -m pytest -m "not slow"
```

## Test Reports

### HTML Reports
```bash
# Generate HTML test report
python -m pytest --html=report.html --self-contained-html

# Generate coverage HTML report
python -m pytest --cov=universal_estimator --cov-report=html
```

### JUnit XML Reports
```bash
# Generate JUnit XML report for CI
python -m pytest --junitxml=test-results.xml
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Assertions**: Use descriptive assertion messages
3. **Fixture Usage**: Reuse fixtures for common test data
4. **Parameterization**: Use `@pytest.mark.parametrize` for similar tests
5. **Error Testing**: Always test error conditions
6. **Coverage**: Aim for high test coverage, especially for critical paths

## Support

If you encounter issues with the tests:

1. Check the pytest documentation: https://docs.pytest.org/
2. Verify all dependencies are installed correctly
3. Ensure you're using compatible versions of scikit-learn and pytest
4. Check the test logs for detailed error messages
