#!/usr/bin/env python3
import pytest
import sys
import subprocess
import os


def install_dependencies():
    """Install test dependencies"""
    print("Installing dependencies...")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "pytest-asyncio",
            "httpx",
        ]
    )


def run_tests():
    """Run pytest"""
    print("Running tests...")
    args = [
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:coverage_report",
        "test/",
    ]
    ret = pytest.main(args)
    return ret


if __name__ == "__main__":
    # Check if we need to install deps (simple check)
    try:
        import pytest_cov
        import pytest_mock
    except ImportError:
        install_dependencies()

    sys.exit(run_tests())
