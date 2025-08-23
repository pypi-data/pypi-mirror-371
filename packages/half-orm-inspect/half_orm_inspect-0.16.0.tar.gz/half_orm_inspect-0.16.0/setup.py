#!/usr/bin/env python3
"""
Setup configuration for half-orm-inspect extension.
"""

from setuptools import setup, find_packages
import os

# Read long description from README if available
def get_long_description():
    """Get long description from README file."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

VERSION='0.16.0'

setup(
    name="half-orm-inspect",
    version=VERSION,
    description="Database inspection extension for half-orm",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="half-orm Team",
    author_email="contact@half-orm.org",
    url="https://github.com/half-orm/half-orm-inspect",
    
    # Package configuration
    packages=find_packages(),
    python_requires=">=3.7",
    
    # Dependencies
    install_requires=[
        f"half_orm>={VERSION.rsplit('.', 1)[0]}",  # Same major.minor
        "click>=7.0",
    ],
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov',
            'black',
            'flake8',
        ],
        'json': [
            # JSON output is built-in, but could add formatters
        ],
    },
    
    # Entry points for CLI integration
    entry_points={
        'console_scripts': [
            # Optional standalone command
            'half-orm-inspect=half_orm_inspect.cli_extension:inspect',
        ],
    },
    
    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Keywords for PyPI
    keywords="half-orm, PostgreSQL, ORM, database, inspection, introspection",
    
    # Project URLs
    project_urls={
        'Bug Reports': 'https://github.com/half-orm/half-orm-inspect/issues',
        'Source': 'https://github.com/half-orm/half-orm-inspect',
        'Documentation': 'https://half-orm.org/extensions/inspect',
    },
    
    # Package data
    include_package_data=True,
    zip_safe=False,
    
    # Test configuration
    test_suite='tests',
    tests_require=[
        'pytest>=6.0',
        'pytest-cov',
    ],
)
