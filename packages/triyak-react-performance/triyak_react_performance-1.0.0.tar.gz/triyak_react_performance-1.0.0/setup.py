#!/usr/bin/env python3
"""
Setup script for Triyak React Performance Suite - Python Bindings
The world's most advanced React performance optimization toolkit
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
    name="triyak-react-performance",
    version="1.0.0",
    author="Bhavendra Singh",
    author_email="info@triyak.in",
    description="The world's most advanced React performance optimization toolkit - Built on 500+ enterprise website optimizations",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://www.triyak.in/docs/react-performance",
    project_urls={
        "Bug Reports": "https://github.com/bhaven13/triyak-react-performance/issues",
        "Source": "https://github.com/bhaven13/triyak-react-performance",
        "Documentation": "https://www.triyak.in/docs/react-performance",
        "Website": "https://www.triyak.in",
        "LinkedIn": "https://www.linkedin.com/in/bhavendra-singh",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Flask",
        "Framework :: FastAPI",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "psutil>=5.8.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "pytest-mock>=3.6",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
            "myst-parser>=0.15",
        ],
    },
    keywords=[
        "react",
        "performance",
        "optimization",
        "core-web-vitals",
        "lcp",
        "fid",
        "cls",
        "bundle-optimization",
        "memory-optimization",
        "ai-optimization",
        "enterprise",
        "triyak",
        "digital-marketing",
        "seo-optimization",
        "web-performance",
        "python",
        "monitoring",
        "analytics",
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "triyak-performance=triyak_react_performance.cli:main",
        ],
    },
)
