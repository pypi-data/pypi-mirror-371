# Azure WAF Deployer 🛡️

[![PyPI version](https://badge.fury.io/py/azure-waf-deployer.svg)](https://badge.fury.io/py/azure-waf-deployer)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python package for deploying Web Application Firewall (WAF) enabled infrastructure on Azure. Simplify your Azure security deployments with pre-built templates and easy-to-use Python APIs.

## 🚀 Features

- **One-command WAF deployment** - Deploy Application Gateway or Front Door with WAF in minutes
- **Pre-configured security templates** - OWASP Core Rule Set, Bot Manager, and custom rules
- **Python API and CLI** - Use programmatically or from command line
- **Flexible configuration** - YAML-based configuration with full customization
- **Built-in validation** - Template validation before deployment
- **Comprehensive logging** - Rich console output and detailed logging

## 📦 Installation

```bash
pip install azure-waf-deployer
```

## 🎯 Quick Start

### 1. Initialize Configuration
```bash
azure-waf-deploy init --name "my-waf" --location "eastus" --output config.yaml
```

### 2. Deploy WAF Infrastructure
```bash
azure-waf-deploy deploy \
  --subscription-id "your-subscription-id" \
  --resource-group "my-rg" \
  --config config.yaml
```

### 3. Python API Usage
```python
from azure_waf_deployer import WAFDeployer, WAFConfig

config = WAFConfig.from_yaml('config.yaml')
deployer = WAFDeployer('your-subscription-id')
result = deployer.deploy_application_gateway_waf('my-rg', config)
```

## 📚 Documentation

- [Complete Usage Guide](https://github.com/yourusername/azure-waf-deployer/blob/main/docs/USAGE.md)
- [Configuration Reference](https://github.com/yourusername/azure-waf-deployer/blob/main/docs/CONFIG.md)
- [API Documentation](https://github.com/yourusername/azure-waf-deployer/blob/main/docs/API.md)

## 🛠️ Supported Templates

- **Application Gateway WAF v2** - Regional load balancer with advanced WAF
- **Azure Front Door WAF** - Global CDN with WAF protection
- **API Management WAF** - API gateway with WAF (coming soon)

## 🔧 Requirements

- Python 3.8+
- Azure CLI or Service Principal credentials
- Azure subscription with appropriate permissions

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

# LICENSE
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

# MANIFEST.in
include README.md
include LICENSE
include CHANGELOG.md
recursive-include azure_waf_deployer/templates *.json *.bicep
recursive-include azure_waf_deployer/configs *.yaml *.yml
recursive-include docs *.md
global-exclude *.pyc
global-exclude __pycache__
global-exclude .git*
global-exclude .DS_Store

---

# pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "azure-waf-deployer"
version = "1.0.0"
description = "Azure Web Application Firewall deployment templates and utilities"
readme = "README.md"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}
keywords = ["azure", "waf", "security", "cloud", "deployment", "arm", "bicep"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: System :: Systems Administration",
    "Topic :: Security",
    "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
]
requires-python = ">=3.8"
dependencies = [
    "azure-identity>=1.12.0",
    "azure-mgmt-resource>=22.0.0",
    "azure-mgmt-network>=25.0.0",
    "azure-mgmt-web>=7.0.0",
    "azure-cli-core>=2.45.0",
    "jinja2>=3.1.2",
    "pyyaml>=6.0",
    "click>=8.0.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
]
docs = [
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.2.0",
    "myst-parser>=1.0.0",
]

[project.scripts]
azure-waf-deploy = "azure_waf_deployer.cli:main"

[project.urls]
Homepage = "https://github.com/yourusername/azure-waf-deployer"
Documentation = "https://azure-waf-deployer.readthedocs.io/"
Repository = "https://github.com/yourusername/azure-waf-deployer"
Issues = "https://github.com/yourusername/azure-waf-deployer/issues"
Changelog = "https://github.com/yourusername/azure-waf-deployer/blob/main/CHANGELOG.md"

[tool.setuptools.packages.find]
where = ["."]
include = ["azure_waf_deployer*"]

[tool.setuptools.package-data]
azure_waf_deployer = ["templates/*.json", "templates/*.bicep", "configs/*.yaml"]

[tool.black]
line-length = 100
target-version = ['py38']
include = '\.pyi?$'

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

---

# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Lint with flake8
      run: |
        flake8 azure_waf_deployer tests --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 azure_waf_deployer tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Type check with mypy
      run: mypy azure_waf_deployer
    
    - name: Test with pytest
      run: |
        pytest tests/ --cov=azure_waf_deployer --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

---

# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy