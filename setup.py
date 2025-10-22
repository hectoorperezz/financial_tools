"""
Setup script for SEC Filing Extractor.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="sec-filing-extractor",
    version="2.0.0",
    description="Download and extract data from SEC EDGAR filings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SEC Filing Extractor Contributors",
    author_email="contact@example.com",
    url="https://github.com/yourusername/sec-filing-extractor",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "sec-filing-extractor=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="sec edgar filings financial data extraction xbrl",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/sec-filing-extractor/issues",
        "Source": "https://github.com/yourusername/sec-filing-extractor",
    },
)
