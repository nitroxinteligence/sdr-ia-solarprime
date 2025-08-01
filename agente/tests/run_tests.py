#!/usr/bin/env python3
"""
Test runner script for SDR Agent.

This script provides convenient commands to run different test suites
with appropriate configurations and reporting.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd: list[str], cwd: str = None) -> int:
    """Run a command and return exit code."""
    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)
    
    result = subprocess.run(cmd, cwd=cwd or project_root)
    return result.returncode


def run_unit_tests(category: str = None, verbose: bool = False):
    """Run unit tests."""
    cmd = ["pytest", "agente/tests/unit"]
    
    if category:
        cmd.append(f"agente/tests/unit/{category}")
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend([
        "--cov=agente",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-x"  # Stop on first failure
    ])
    
    return run_command(cmd)


def run_integration_tests(verbose: bool = False):
    """Run integration tests."""
    cmd = [
        "pytest",
        "agente/tests/integration",
        "-m", "integration"
    ]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd)


def run_stress_tests(verbose: bool = False):
    """Run stress tests."""
    cmd = [
        "pytest",
        "agente/tests/stress",
        "-m", "stress",
        "--tb=short"  # Shorter traceback for stress tests
    ]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd)


def run_validation_tests(verbose: bool = False):
    """Run validation tests."""
    cmd = [
        "pytest",
        "agente/tests/validation",
        "-m", "validation"
    ]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd)


def run_performance_benchmarks(verbose: bool = False):
    """Run performance benchmarks."""
    cmd = [
        "pytest",
        "agente/tests/performance",
        "-m", "benchmark",
        "-s"  # Show print statements for benchmark results
    ]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd)


def run_all_tests(verbose: bool = False, continue_on_failure: bool = False):
    """Run all test suites."""
    print("🧪 Running all test suites...")
    print("=" * 80)
    
    suites = [
        ("Unit Tests", lambda: run_unit_tests(verbose=verbose)),
        ("Integration Tests", lambda: run_integration_tests(verbose=verbose)),
        ("Validation Tests", lambda: run_validation_tests(verbose=verbose)),
        ("Stress Tests", lambda: run_stress_tests(verbose=verbose)),
        ("Performance Benchmarks", lambda: run_performance_benchmarks(verbose=verbose))
    ]
    
    results = {}
    
    for suite_name, suite_func in suites:
        print(f"\n📋 {suite_name}")
        print("-" * 80)
        
        exit_code = suite_func()
        results[suite_name] = "✅ PASSED" if exit_code == 0 else "❌ FAILED"
        
        if exit_code != 0 and not continue_on_failure:
            break
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 Test Summary:")
    print("-" * 80)
    
    for suite_name, result in results.items():
        print(f"{result} {suite_name}")
    
    # Overall result
    all_passed = all("✅" in result for result in results.values())
    return 0 if all_passed else 1


def run_specific_test(test_path: str, verbose: bool = False):
    """Run a specific test file or test case."""
    cmd = ["pytest", test_path]
    
    if verbose:
        cmd.extend(["-v", "-s"])
    
    return run_command(cmd)


def run_coverage_report():
    """Generate and open coverage report."""
    print("📊 Generating coverage report...")
    
    cmd = [
        "pytest",
        "agente/tests/unit",
        "--cov=agente",
        "--cov-report=html",
        "--cov-report=term"
    ]
    
    exit_code = run_command(cmd)
    
    if exit_code == 0:
        print("\n✅ Coverage report generated at: htmlcov/index.html")
        
        # Try to open in browser
        import webbrowser
        report_path = project_root / "htmlcov" / "index.html"
        webbrowser.open(f"file://{report_path}")
    
    return exit_code


def main():
    parser = argparse.ArgumentParser(
        description="Test runner for SDR Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all unit tests
  python run_tests.py unit
  
  # Run specific category of unit tests
  python run_tests.py unit --category whatsapp
  
  # Run integration tests
  python run_tests.py integration
  
  # Run all tests
  python run_tests.py all
  
  # Run specific test file
  python run_tests.py specific agente/tests/unit/whatsapp/test_send_text.py
  
  # Generate coverage report
  python run_tests.py coverage
        """
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Test suite to run")
    
    # Unit tests
    unit_parser = subparsers.add_parser("unit", help="Run unit tests")
    unit_parser.add_argument(
        "--category",
        choices=["whatsapp", "kommo", "calendar", "database", "media", "utility"],
        help="Specific category to test"
    )
    
    # Integration tests
    subparsers.add_parser("integration", help="Run integration tests")
    
    # Stress tests
    subparsers.add_parser("stress", help="Run stress tests")
    
    # Validation tests
    subparsers.add_parser("validation", help="Run validation tests")
    
    # Performance benchmarks
    subparsers.add_parser("performance", help="Run performance benchmarks")
    
    # All tests
    all_parser = subparsers.add_parser("all", help="Run all test suites")
    all_parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Continue running tests even if a suite fails"
    )
    
    # Specific test
    specific_parser = subparsers.add_parser("specific", help="Run specific test")
    specific_parser.add_argument("test_path", help="Path to test file or test case")
    
    # Coverage report
    subparsers.add_parser("coverage", help="Generate coverage report")
    
    # Global arguments
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate function
    if args.command == "unit":
        return run_unit_tests(category=args.category, verbose=args.verbose)
    elif args.command == "integration":
        return run_integration_tests(verbose=args.verbose)
    elif args.command == "stress":
        return run_stress_tests(verbose=args.verbose)
    elif args.command == "validation":
        return run_validation_tests(verbose=args.verbose)
    elif args.command == "performance":
        return run_performance_benchmarks(verbose=args.verbose)
    elif args.command == "all":
        return run_all_tests(verbose=args.verbose, continue_on_failure=args.continue_on_failure)
    elif args.command == "specific":
        return run_specific_test(args.test_path, verbose=args.verbose)
    elif args.command == "coverage":
        return run_coverage_report()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())