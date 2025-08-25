# azure-waf-deployer/setup.py
from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="azure-waf-deployer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Azure Web Application Firewall deployment templates and utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/azure-waf-deployer",
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
    ],
    python_requires=">=3.8",
    install_requires=[
        "azure-identity>=1.12.0",
        "azure-mgmt-resource>=22.0.0",
        "azure-mgmt-network>=25.0.0",
        "azure-mgmt-web>=7.0.0",
        "azure-cli-core>=2.45.0",
        "jinja2>=3.1.2",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "azure_waf_deployer": [
            "templates/*.json",
            "templates/*.bicep",
            "templates/*.yml",
            "configs/*.yaml",
        ],
    },
    entry_points={
        "console_scripts": [
            "azure-waf-deploy=azure_waf_deployer.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/azure-waf-deployer/issues",
        "Source": "https://github.com/yourusername/azure-waf-deployer",
        "Documentation": "https://azure-waf-deployer.readthedocs.io/",
    },
)