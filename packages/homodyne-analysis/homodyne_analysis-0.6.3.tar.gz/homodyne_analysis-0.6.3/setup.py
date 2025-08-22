#!/usr/bin/env python3
"""
Setup script for the Homodyne Scattering Analysis Package.

A comprehensive Python package for analyzing homodyne scattering in X-ray Photon
Correlation Spectroscopy (XPCS) under nonequilibrium conditions.
"""

from setuptools import setup, find_packages
import os
import re


def read_version():
    """Read version from homodyne/__init__.py."""
    version_file = os.path.join(os.path.dirname(__file__), "homodyne", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
        version_match = re.search(r'^__version__ = ["\']([^"\']*)["\']', content, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


def read_long_description():
    """Read long description from README.md."""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def read_requirements(filename):
    """Read requirements from a file."""
    requirements_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return []


# Core requirements (always needed)
CORE_REQUIREMENTS = [
    "numpy>=1.24.0,<2.3.0",  # Compatible with Numba 0.61.2
    "scipy>=1.7.0",
    "matplotlib>=3.3.0",
]

# Data handling and manipulation
DATA_REQUIREMENTS = [
    "xpcs-viewer>=1.0.4",  # XPCS data handling (pyXpcsViewer): https://github.com/AdvancedPhotonSource/pyXpcsViewer
]

# Performance requirements (recommended)
PERFORMANCE_REQUIREMENTS = [
    "numba>=0.61.0,<0.62.0",  # Ensure NumPy 2.2 compatibility
    "psutil>=5.8.0",  # For memory profiling and system monitoring
]

# MCMC requirements (optional advanced feature)
MCMC_REQUIREMENTS = [
    "pymc>=5.0.0",
    "arviz>=0.12.0",
    "pytensor>=2.8.0",
    "corner>=2.2.0",  # For enhanced MCMC corner plots
]

# Test requirements
TEST_REQUIREMENTS = [
    "pytest>=6.2.0",
    "pytest-cov>=2.12.0",
    "pytest-xdist>=2.3.0",
    "pytest-benchmark>=4.0.0",
    "pytest-mock>=3.6.0",  # For mocking utilities in tests
    "hypothesis>=6.0.0",  # For property-based testing
]

# Documentation requirements
DOC_REQUIREMENTS = [
    "sphinx>=4.0.0",
    "sphinx-rtd-theme>=1.0.0",
    "myst-parser>=0.17.0",
    "sphinx-autodoc-typehints>=1.12.0",
    "numpydoc>=1.2.0",
    "linkify-it-py>=2.0.0",
]

# Development requirements
DEV_REQUIREMENTS = [
    "pytest>=6.2.0",
    "pytest-cov>=2.12.0",
    "pytest-xdist>=2.3.0",
    "pytest-benchmark>=4.0.0",
    "pytest-mock>=3.6.0",
    "hypothesis>=6.0.0",
    "black>=21.0.0",
    "flake8>=3.9.0",
    "mypy>=0.910",
    "types-psutil>=5.9.0",
    "types-Pillow>=10.0.0",
    "types-six>=1.16.0",
] + DOC_REQUIREMENTS

# All optional requirements combined
ALL_REQUIREMENTS = (
    DATA_REQUIREMENTS + PERFORMANCE_REQUIREMENTS + MCMC_REQUIREMENTS + DOC_REQUIREMENTS + TEST_REQUIREMENTS + DEV_REQUIREMENTS
)

setup(
    name="homodyne-analysis",
    version=read_version(),
    author="Wei Chen, Hongrui He",
    author_email="wchen@anl.gov",
    description="Comprehensive Python package for analyzing homodyne scattering in X-ray Photon Correlation Spectroscopy (XPCS) under nonequilibrium conditions",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/imewei/homodyne",
    project_urls={
        "Documentation": "https://homodyne.readthedocs.io/",
        "Source": "https://github.com/imewei/homodyne",
        "Tracker": "https://github.com/imewei/homodyne/issues",
    },
    packages=find_packages(exclude=["tests*", "docs*", "examples*", "homodyne.tests*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=CORE_REQUIREMENTS,
    extras_require={
        "data": DATA_REQUIREMENTS,
        "performance": PERFORMANCE_REQUIREMENTS,
        "mcmc": MCMC_REQUIREMENTS,
        "docs": DOC_REQUIREMENTS,
        "test": TEST_REQUIREMENTS,
        "dev": DEV_REQUIREMENTS,
        "all": ALL_REQUIREMENTS,
    },
    include_package_data=True,
    package_data={
        "homodyne": [
            "config_*.json",
            "templates/*.json",
        ],
    },
    entry_points={
        "console_scripts": [
            "homodyne=homodyne.run_homodyne:main",
            "homodyne-config=homodyne.create_config:main",
        ],
    },
    keywords=[
        "xpcs",
        "homodyne",
        "scattering",
        "correlation spectroscopy",
        "soft matter",
        "nonequilibrium dynamics",
        "transport coefficients",
        "Bayesian analysis",
        "MCMC",
    ],
    zip_safe=False,
)
