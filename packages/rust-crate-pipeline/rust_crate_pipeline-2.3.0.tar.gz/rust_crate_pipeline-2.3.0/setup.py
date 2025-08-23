#!/usr/bin/env python3
"""
Setup script for rust-crate-pipeline

This package provides comprehensive Rust crate analysis with AI-powered insights,
web scraping, and enhanced tooling for dependency analysis and security assessment.
"""

import sys
from pathlib import Path
from setuptools import setup

# Read the README file for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from the package
try:
    sys.path.insert(0, str(this_directory))
    from rust_crate_pipeline.version import __version__
except ImportError:
    __version__ = "2.2.3"  # fallback version

setup(
    name="rust-crate-pipeline",
    version=__version__,
    description=(
        "Comprehensive Rust crate analysis with AI-powered insights and enhanced "
        "tooling"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SigilDERG Team",
    author_email="sigil@example.com",
    url="https://github.com/Superuser666-Sigil/SigilDERG-Data_Production",
    packages=[
        "rust_crate_pipeline",
        "rust_crate_pipeline.audits",
        "rust_crate_pipeline.core",
        "rust_crate_pipeline.scraping",
        "rust_crate_pipeline.utils",
    ],
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=[
        "aiohttp>=3.8.0",
        "httpx[http2]>=0.24.0",
        "playwright>=1.40.0",
        "crawl4ai>=0.1.0",
        "pydantic>=2.0.0",
        "requests>=2.28.0",
        "asyncio-mqtt>=0.13.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "llm": [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
            "llama-cpp-python>=0.2.0",
            "litellm>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rust-crate-pipeline=rust_crate_pipeline.main:main",
            "sigil-pipeline=rust_crate_pipeline.unified_pipeline:main",
            "rust-crate-setup=rust_crate_pipeline.setup_manager:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Systems Administration",
    ],
    keywords="rust, crates, analysis, ai, llm, security, dependencies",
    project_urls={
        "Bug Reports": (
            "https://github.com/Superuser666-Sigil/SigilDERG-Data_Production/issues"
        ),
        "Source": (
            "https://github.com/Superuser666-Sigil/SigilDERG-Data_Production"
        ),
        "Documentation": (
            "https://github.com/Superuser666-Sigil/SigilDERG-Data_Production/wiki"
        ),
    },
)
