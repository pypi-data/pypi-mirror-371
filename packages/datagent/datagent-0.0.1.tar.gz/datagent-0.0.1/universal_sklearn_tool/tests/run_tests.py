#!/usr/bin/env python3
"""
Test runner script for the universal estimator module.
"""

import sys
import subprocess
import argparse


def run_tests(verbose=False, coverage=False, html_report=False):
    """Run the pytest tests."""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=universal_estimator", "--cov-report=term-missing"])
        
        if html_report:
            cmd.append("--cov-report=html")
    
    cmd.append("test_universal_estimator.py")
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        if html_report:
            print("📊 HTML coverage report generated in htmlcov/")
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed!")
        sys.exit(1)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run tests for universal estimator")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    
    args = parser.parse_args()
    
    run_tests(
        verbose=args.verbose,
        coverage=args.coverage,
        html_report=args.html
    )


if __name__ == "__main__":
    main()
