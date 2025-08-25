#!/usr/bin/env python3
"""
Setup script for PoI Python SDK package.
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

setup(
    name="poi-sdk",
    version="0.1.0",
    author="Giovanny Pietro",
    author_email="giovanny.pietro@example.com",
    description="A Python SDK for creating trustworthy AI agent transactions with Proof-of-Intent",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/giovannypietro/poi-examples",
    project_urls={
        "Bug Tracker": "https://github.com/giovannypietro/poi-examples/issues",
        "Documentation": "https://github.com/giovannypietro/poi-examples/blob/main/README.md",
        "Source Code": "https://github.com/giovannypietro/poi-examples",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=3.4.8",
        "pyyaml>=6.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "tox>=4.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "poi-cli=poi_sdk.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "poi_sdk": ["py.typed"],
    },
    zip_safe=False,
    keywords="proof-of-intent, ai, security, cryptography, agents, trust, audit",
)
