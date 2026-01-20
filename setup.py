#!/usr/bin/env python3
"""Setup script for PII Anonymizer."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip() 
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith("#") and not line.startswith("-")
    ]

setup(
    name="piicloak",
    version="1.0.1",
    author="Dmitry Marinov",
    author_email="marinovdk@gmail.com",
    description="Enterprise-grade PII detection and anonymization API. Helps achieve GDPR/CCPA compliance. Supports 31 entity types.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dimanjet/piicloak",
    project_urls={
        "Bug Tracker": "https://github.com/dimanjet/piicloak/issues",
        "Documentation": "https://github.com/dimanjet/piicloak#readme",
        "Source": "https://github.com/dimanjet/piicloak",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Text Processing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business",
        "Environment :: Web Environment",
        "Framework :: Flask",
    ],
    keywords="pii pii-detection anonymization gdpr ccpa hipaa privacy data-protection "
             "presidio spacy nlp ner salesforce legal-tech fintech healthcare "
             "text-processing redaction compliance",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "flask>=3.0.0",
        "presidio-analyzer>=2.2.0",
        "presidio-anonymizer>=2.2.0",
        "spacy>=3.7.0",
        "python-docx>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "production": [
            "gunicorn>=21.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "piicloak=piicloak.app:main",
        ],
    },
)
