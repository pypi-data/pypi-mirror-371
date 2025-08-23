"""
Setup script for PayPal SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = [
        "requests>=2.31.0",
        "python-dotenv>=1.0.0", 
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0"
    ]

setup(
    name="paypal-payments-sdk",
    version="1.1.0",
    author="ljohri",
    author_email="ljohri@example.com",
    description="A comprehensive Python SDK for PayPal Payments REST API v2 and Transaction Search API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ljohri/paypal_sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="paypal payments api sdk",
    project_urls={
        "Bug Reports": "https://github.com/ljohri/paypal_sdk/issues",
        "Source": "https://github.com/ljohri/paypal_sdk",
        "Documentation": "https://github.com/ljohri/paypal_sdk#readme",
    },
)
