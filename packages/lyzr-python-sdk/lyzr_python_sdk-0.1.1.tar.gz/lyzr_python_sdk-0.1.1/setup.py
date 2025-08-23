#!/usr/bin/env python3
"""Setup script for lyzr-agent-api package."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "lyzr-python", "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt file."""
    requirements_path = os.path.join(this_directory, "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return ["requests>=2.25.0"]

setup(
    name="lyzr-python-sdk",
    version="0.1.1",
    author="Lyzr",
    author_email="support@lyzr.ai",
    description="A Python client library for interacting with the Lyzr Agent API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LyzrCore/lyzr-python",
    packages=["lyzr_python_sdk", "lyzr_python_sdk.clients"],
    package_dir={"lyzr_python_sdk": "lyzr-python"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords="lyzr agent api client llm artificial intelligence",
    project_urls={
        "Bug Reports": "https://github.com/LyzrCore/lyzr-python/issues",
        "Source": "https://github.com/LyzrCore/lyzr-python",
        "Documentation": "https://docs.lyzr.ai",
    },
    include_package_data=True,
    zip_safe=False,
)
