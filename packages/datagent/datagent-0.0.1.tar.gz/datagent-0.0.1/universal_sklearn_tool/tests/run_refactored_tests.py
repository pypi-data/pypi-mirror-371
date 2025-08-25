#!/usr/bin/env python3
"""
Test runner for the refactored Universal Scikit-learn Tools.

This script provides a comprehensive test runner for all the refactored modules
with various options for different testing scenarios.
"""

import argparse
import sys
import os
import subprocess
import time
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    if description:
        print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"Exit code: {result.returncode}")
    print(f"Duration: {end_time - start_time:.2f} seconds")
    
    if result.stdout:
        print("\nSTDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    return result.returncode == 0


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Test runner for refactored Universal Scikit-learn Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_refactored_tests.py

  # Run only unit tests
  python run_refactored_tests.py --unit

  # Run only integration tests
  python run_refactored_tests.py --integration

  # Run tests for specific module
  python run_refactored_tests.py --module classification

  # Run with coverage
  python run_refactored_tests.py --coverage

  # Run with verbose output
  python run_refactored_tests.py --verbose

  # Run slow tests
  python run_refactored_tests.py --slow

  # Run tests in parallel
  python run_refactored_tests.py --parallel

  # Generate HTML coverage report
  python run_refactored_tests.py --coverage --html
        """
    )
    
    # Test type options
    parser.add_argument(
        "--unit", action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration", action="store_true",
        help="Run only integration tests"
    )
    parser.add_argument(
        "--classification", action="store_true",
        help="Run only classification tests"
    )
    parser.add_argument(
        "--regression", action="store_true",
        help="Run only regression tests"
    )
    parser.add_argument(
        "--clustering", action="store_true",
        help="Run only clustering tests"
    )
    parser.add_argument(
        "--preprocessing", action="store_true",
        help="Run only preprocessing tests"
    )
    
    # Module-specific options
    parser.add_argument(
        "--module", choices=["base", "classification", "regression", "clustering", "preprocessing", "universal"],
        help="Run tests for specific module"
    )
    
    # Test execution options
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Quiet output (minimal)"
    )
    parser.add_argument(
        "--slow", action="store_true",
        help="Include slow tests"
    )
    parser.add_argument(
        "--parallel", "-n", type=int, metavar="N",
        help="Run tests in parallel with N workers"
    )
    parser.add_argument(
        "--failed", action="store_true",
        help="Run only failed tests from last run"
    )
    
    # Coverage options
    parser.add_argument(
        "--coverage", action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--html", action="store_true",
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--xml", action="store_true",
        help="Generate XML coverage report"
    )
    
    # Output options
    parser.add_argument(
        "--junit", action="store_true",
        help="Generate JUnit XML report"
    )
    parser.add_argument(
        "--html-report", action="store_true",
        help="Generate HTML test report"
    )
    
    # Other options
    parser.add_argument(
        "--install-deps", action="store_true",
        help="Install test dependencies"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Clean up test artifacts"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available tests"
    )
    
    args = parser.parse_args()
    
    # Change to the tests directory
    tests_dir = Path(__file__).parent
    os.chdir(tests_dir)
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"])
    
    # Clean up if requested
    if args.clean:
        print("Cleaning up test artifacts...")
        for pattern in ["htmlcov", "coverage.xml", "test-results.xml", "report.html", ".pytest_cache", "__pycache__"]:
            subprocess.run(["find", ".", "-name", pattern, "-type", "d", "-exec", "rm", "-rf", "{}", "+"], 
                         capture_output=True)
        for pattern in ["*.pyc", "*.pyo", "*.pyd"]:
            subprocess.run(["find", ".", "-name", pattern, "-delete"], capture_output=True)
    
    # List tests if requested
    if args.list:
        print("Available tests:")
        cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q"]
        subprocess.run(cmd)
        return
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    elif args.quiet:
        cmd.append("-q")
    else:
        cmd.append("-v")
    
    # Build marker string
    markers = []
    
    # Add markers based on test type
    if args.unit:
        markers.append("unit")
    elif args.integration:
        markers.append("integration")
    elif args.classification:
        markers.append("classification")
    elif args.regression:
        markers.append("regression")
    elif args.clustering:
        markers.append("clustering")
    elif args.preprocessing:
        markers.append("preprocessing")
    
    # Add slow test handling
    if args.slow:
        # Include slow tests
        pass
    else:
        # Exclude slow tests by default
        markers.append("not slow")
    
    # Add marker to command if any markers specified
    if markers:
        cmd.extend(["-m", " and ".join(markers)])
    
    # Add module-specific tests
    if args.module:
        if args.module == "base":
            cmd.append("test_base_model.py")
        elif args.module == "classification":
            cmd.append("test_classification.py")
        elif args.module == "regression":
            cmd.append("test_regression.py")
        elif args.module == "clustering":
            cmd.append("test_clustering.py")
        elif args.module == "preprocessing":
            cmd.append("test_preprocessing.py")
        elif args.module == "universal":
            cmd.append("test_universal_estimator_refactored.py")
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add failed tests
    if args.failed:
        cmd.append("--lf")
    
    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=..", "--cov-report=term-missing"])
        
        if args.html:
            cmd.append("--cov-report=html")
        if args.xml:
            cmd.append("--cov-report=xml")
    
    # Add JUnit XML report
    if args.junit:
        cmd.extend(["--junitxml=test-results.xml"])
    
    # Add HTML test report
    if args.html_report:
        cmd.extend(["--html=report.html", "--self-contained-html"])
    
    # Add color and other options
    cmd.extend(["--color=yes", "--tb=short"])
    
    # Run the tests
    success = run_command(cmd, "Running tests")
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print(f"{'='*60}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
