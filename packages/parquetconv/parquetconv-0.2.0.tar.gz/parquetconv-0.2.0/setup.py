#!/usr/bin/env python3
"""
Setup script for ParquetConv
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="parquetconv",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A command-line tool for converting between Parquet and CSV file formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/parquetconv",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Data Scientists",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.3.2",
        "pyarrow>=21.0.0",
    ],
    entry_points={
        "console_scripts": [
            "parquetconv=parquetconv.cli:main",
        ],
    },
    keywords="parquet csv conversion pandas data",
)
