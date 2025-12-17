"""Setup configuration for Enhanced ML Pipeline package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Development requirements
dev_requirements = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "black>=23.0.0",
    "flake8>=6.1.0",
    "mypy>=1.7.0",
    "isort>=5.13.0",
    "pre-commit>=3.6.0",
]

setup(
    name="ml-pipeline",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Enhanced ML Pipeline with LangGraph, AWS Bedrock, and MLflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ml-pipeline",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "notebooks"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "xgboost": ["xgboost>=2.0.0"],
        "lightgbm": ["lightgbm>=4.1.0"],
        "catboost": ["catboost>=1.2.0"],
        "all": [
            "xgboost>=2.0.0",
            "lightgbm>=4.1.0",
            "catboost>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ml-pipeline=scripts.run_pipeline:main",
            "ml-pipeline-evaluate=scripts.evaluate_model:main",
            "ml-pipeline-deploy=scripts.deploy_model:main",
        ],
    },
    include_package_data=True,
    package_data={
        "agents": ["prompts/*.txt"],
        "config": ["*.yaml"],
    },
    zip_safe=False,
    keywords="machine-learning mlops langgraph aws-bedrock mlflow pipeline automation",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ml-pipeline/issues",
        "Source": "https://github.com/yourusername/ml-pipeline",
        "Documentation": "https://github.com/yourusername/ml-pipeline/docs",
    },
)
