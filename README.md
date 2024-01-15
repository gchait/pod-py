## Pod-Py

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

**A simple CLI to create or manage a Kubernetes Pod.**


#### Prerequisites
- Python 3.12+
- Poetry
- Just
- A running Kubernetes cluster
- A kubeconfig file that gives you Pod management permissions


#### Assumptions
- The Pod has only one container
- The Pod has `bash` and `tar`
- For `deploy`, your YAML file contains only a Pod
