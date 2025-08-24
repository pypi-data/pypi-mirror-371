#!/usr/bin/env python3
"""
Setup script for LRDBench
A comprehensive framework for long-range dependence estimation
Developed in the Department of Biomedical Engineering at the University of Reading
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get version from pyproject.toml or use default
def get_version():
    return "1.0.1"

setup(
    name="lrdbench",
    version=get_version(),
    author="Davian R. Chin",
    author_email="d.r.chin@pgr.reading.ac.uk",
    description="A comprehensive framework for long-range dependence estimation with synthetic data generation and analysis. Developed in the Department of Biomedical Engineering at the University of Reading.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/dave2k77/long-range-dependence-project-3",
    project_urls={
        "Bug Reports": "https://github.com/dave2k77/long-range-dependence-project-3/issues",
        "Source": "https://github.com/dave2k77/long-range-dependence-project-3",
        "Documentation": "https://github.com/dave2k77/long-range-dependence-project-3#readme",
    },
    packages=find_packages(include=["models*", "analysis*"], exclude=["web-dashboard*", "setup*", "research*", "tests*", "demos*", "documentation*", "assets*", "confound_results*", "scripts*", "config*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
        "full": [
            "jax>=0.3.0",
            "jaxlib>=0.3.0",
            "torch>=1.9.0",
            "numba>=0.56.0",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.txt", "*.md"],
    },
    entry_points={
        "console_scripts": [
            "lrdbench=scripts.comprehensive_estimator_benchmark:main",
            "benchmark-estimators=scripts.comprehensive_estimator_benchmark:main",
            "confound-analysis=scripts.confounded_data_benchmark:main",
        ],
    },
    keywords=[
        "long-range-dependence",
        "hurst-exponent",
        "fractional-calculus",
        "time-series-analysis",
        "synthetic-data",
        "benchmarking",
        "estimators",
        "neural-networks",
        "physics-informed",
        "scientific-computing",
    ],
    zip_safe=False,
)
