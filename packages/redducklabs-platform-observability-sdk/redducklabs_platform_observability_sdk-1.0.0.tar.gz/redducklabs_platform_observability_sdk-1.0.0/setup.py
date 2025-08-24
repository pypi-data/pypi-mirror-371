#!/usr/bin/env python
"""Setup script for Platform Observability Python SDK."""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Version
__version__ = "1.0.0"

setup(
    name="platform-observability-sdk",
    version=__version__,
    description="Python SDK for Platform Observability log ingestion and analytics",
    long_description=read_file("README.md") if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="Red Duck Labs",
    author_email="support@redducklabs.com",
    url="https://github.com/redducklabs/platform-observability",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0",
        "python-dateutil>=2.8.0",
        "typing-extensions>=4.0.0;python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
            "asyncio>=3.8.0",
        ],
        "structured": [
            "structlog>=22.0.0",
            "rich>=12.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "obs-cli=platform_observability.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="observability logging monitoring analytics platform",
    project_urls={
        "Bug Reports": "https://github.com/redducklabs/platform-observability/issues",
        "Source": "https://github.com/redducklabs/platform-observability",
        "Documentation": "https://docs.redducklabs.com/platform-observability",
    },
)