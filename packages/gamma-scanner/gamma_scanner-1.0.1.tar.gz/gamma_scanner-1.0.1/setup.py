#!/usr/bin/env python3
"""
Setup script for Gamma Scanner
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return "Gamma Scanner - Advanced String Manipulation and Pattern Matching Engine"

setup(
    name="gamma-scanner",
    version="1.0.1",
    author="Harish Santhanalakshmi Ganesan",
    author_email="harishsg99@gmail.com",
    description="Advanced string manipulation and pattern matching engine with unique DSL syntax",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/gammascanner/gamma-scanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "gamma-scanner=gamma_scanner.cli:main",
            "gamma=gamma_scanner.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "gamma_scanner": ["examples/*.gamma"],
    },
    keywords="security pattern-matching dsl text-analysis malware-detection",
    project_urls={
        "Bug Reports": "https://github.com/gammascanner/gamma-scanner/issues",
        "Source": "https://github.com/gammascanner/gamma-scanner",
        "Documentation": "https://gamma-scanner.readthedocs.io/",
    },
)