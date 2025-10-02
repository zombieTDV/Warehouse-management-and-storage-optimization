# Warehouse-management-and-storage-optimization

![Python](https://img.shields.io/badge/python-3.12-blue)
![Node.js](https://img.shields.io/badge/node-22-alpine-green)
![Build](https://img.shields.io/github/actions/workflow/status/zombieTDV/Warehouse-management-and-storage-optimization/ci.yml?branch=main)
![License](https://img.shields.io/github/license/zombieTDV/Warehouse-management-and-storage-optimization)


# Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Option 1: Local Development Setup (Python & Node)](#option-1-local-development-setup-python--node)
  - [Step 1: Clone the Repository](#step-1-clone-the-repository)
  - [Step 2: Create Virtual Environment](#step-2-create-virtual-environment)
    - [Activate the virtual environment (Windows / macOS / Linux)](#activate-the-virtual-environment)
  - [Step 3: Install Project Dependencies](#step-3-install-project-dependencies)
  - [Step 4: Run the Application](#step-4-run-the-application)
  - [Step 5: Set Up Pre-commit Hooks](#step-5-set-up-pre-commit-hooks)
  - [Additional: Generate Changelog](#additional-generate-changelog)
- [Option 2: Development with Docker / Dev Container (recommended)](#option-2-development-with-docker--dev-container-recommended)
  - [A. VS Code Dev Container (automatic setup)](#a-vs-code-dev-container-automatic-setup)
    - [Prerequisites](#prerequisites-1)
    - [Reopen in Container / postCreateCommand actions](#reopen-in-container--postcreatecommand-actions)
    - [Python interpreter inside container](#python-interpreter-inside-container)
    - [Common in-container commands (tests, lint, run)](#common-in-container-commands-tests-lint-run)
    - [Generate changelog](#generate-changelog)
  - [B. Manual: build & run with Docker (no VS Code)](#b-manual-build--run-with-docker-no-vs-code)
    - [Build (Dockerfile location options)](#build-dockerfile-location-options)
    - [Run an interactive container (macOS / Windows)](#run-an-interactive-container-macos--windows)
    - [Inside the container: create venv & install deps (PEP-668 safe)](#inside-the-container-create-venv--install-deps-pep-668-safe)
    - [Run tests / lint / app](#run-tests--lint--app)
  - [Example minimal `.devcontainer/Dockerfile`](#example-minimal-devcontainerdockerfile)
- [Troubleshooting & tips](#troubleshooting--tips)
  - [PEP 668 / externally-managed-environment errors](#pep-668--externally-managed-environment-errors)
  - [Native libs required by some packages](#native-libs-required-by-some-packages)
  - [Quick rebuild after Dockerfile changes](#quick-rebuild-after-dockerfile-changes)
  - [Ports](#ports)

## Overview

This project provides a warehouse management and storage optimization system.  
It supports development in **Python** and uses **Node.js** for automated changelog generation.

## Features

- 📦 Warehouse inventory tracking  
- 📊 Storage space optimization algorithms  
- 🛠 Pre-commit hooks for linting & formatting (black, flake8, isort)  
- 📝 Automated changelog generation (via `conventional-changelog-cli`)  
- 🐳 Reproducible setup with Docker / Dev Container  
- ⚡ Compatible with **Python 3.9+** and **Node.js 22-alpine**  

## Prerequisites

- Python **3.9 or higher** (3.12 recommended)  
- Git installed  
- **Optional (recommended)**: VS Code + Docker + Remote - Containers extension for Dev Container workflow

## **Contribute and Usage:**

## Option 1: Local Development Setup (Python & Node)

### Step 1: Clone the Repository

```bash
git clone https://github.com/zombieTDV/Warehouse-management-and-storage-optimization.git
cd Warehouse-management-and-storage-optimization
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv
```

#### Activate the virtual environment

- On Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

- On macOS/Linux

```bash
source .venv/bin/activate
```

### Step 3: Install Project Dependencies

- Development mode (recommended):

```bash
pip install -e .[dev]
```

- Runtime only (minimal install):

```bash
pip install -e .
```

### Step 4: Run the Application

```bash
Step 4: Run the Application
```

### Step 5: Set Up Pre-commit Hooks

- The set up:

```bash
pip install pre-commit
pre-commit install
```

- Run manualy if you need to:

```bash
pre-commit run --all-files
```

> Pre-commit enforces style and quality checks (black, flake8, etc.) automatically.
Configuration applies to src/, tests/, and root-level Python files.

### Additionaly: Generate Changelog

```bash
npm install -g conventional-changelog-cli
conventional-changelog -p angular -i CHANGELOG.md -s
```

## Option 2: Development with Docker / Dev Container (recommended for reproducible builds)

This option shows two ways to use Docker for development:

- **A.** Use VS Code *Dev Containers* (one-click "Reopen in Container").
- **B.** Build and run the development image manually (useful without VS Code).


> Important: The container uses a Python **virtual environment** inside the project (`.venv`) so we avoid modifying the system Python (PEP 668). Do **not** run `pip install` against the system Python in the Dockerfile.

### A. VS Code Dev Container (automatic setup)

Prerequisites:

- Docker Desktop
- VS Code + *Remote - Containers* (or *Dev Containers*) extension

1. Ensure the repo contains `.devcontainer/Dockerfile` and `.devcontainer/devcontainer.json`.
2. In VS Code: **Command Palette → Dev Containers: Reopen in Container**.
3. The devcontainer will build the image and run the `postCreateCommand`:
   - creates a venv at `/app/.venv`
   - upgrades pip **inside** the venv
   - installs your package in editable mode: `pip install -e .[dev]` (falls back to `pip install -e .`)
   - installs `pre-commit` and runs `pre-commit install`
   - installs `conventional-changelog-cli` (if included in `postCreateCommand`)

When the container is ready, open a terminal inside VS Code (it will be in the container). If the Python extension does not auto-select the venv, choose the interpreter at:

```bash
/app/.venv/bin/python
```

Run common commands from the in-container terminal:

```bash
# run tests
. .venv/bin/activate
pytest

# run linters / pre-commit
pre-commit run --all-files

# run the app (if your app listens on a port)
. .venv/bin/activate
python -m your_package.main
```

#### Generate changelog

```bash
conventional-changelog -p angular -i CHANGELOG.md -s
```

### B. Manual: build & run with Docker (no VS Code)

From the repository root:

- **If your Dockerfile is at:** `.devcontainer/Dockerfile:`

    - Run: `docker build -t warehouse-dev -f .devcontainer/Dockerfile .`

- **If your Dockerfile is at repo root:** `(./Dockerfile):`

    - Run: `docker build -t warehouse-dev -f Dockerfile .`

Run an interactive container (mounts your repo into /app so source edits are visible immediately):

- **macOS / Linux (bash/zsh):**

    - Run: `docker run --rm -it -v "$(pwd)":/app -w /app -p 8000:8000 warehouse-dev bash`

- **Windows PowerShell:**

    - Run: `docker run --rm -it -v ${PWD}:/app -w /app -p 8000:8000 warehouse-dev bash`

- **Windows CMD:**

    - Run: `docker run --rm -it -v "%cd%":/app -w /app -p 8000:8000 warehouse-dev bash`

Inside the container do the following (safe, PEP-668-compliant steps):

```bash
# create a venv in the project (only needed once)
python3 -m venv .venv

# activate it
. .venv/bin/activate

# upgrade pip *inside* the venv and install editable deps
pip install --upgrade pip
pip install -e .[dev] || pip install -e .

# install pre-commit and hooks (optional)
pip install pre-commit
pre-commit install
```

Now run tests / lint / app as needed:

```bash
. .venv/bin/activate
pytest
pre-commit run --all-files
python -m your_package.main
```

### Troubleshooting & tips

- **PEP 668 errors** (e.g. externally-managed-environment): **do not try to upgrade system pip in the Dockerfile**. Create a **venv** and run pip install inside it (*see steps above*).

- If packages need native libs **(e.g. psycopg2, lxml, cryptography)**, add the required apk add packages to the Dockerfile (e.g. postgresql-dev, libxml2-dev, libxslt-dev, rust if needed), then **rebuild** the image.

- **Quick rebuild** after changing the Dockerfile:

    - Run: `docker build -t warehouse-dev -f .devcontainer/Dockerfile .`

- **Ports**: forward the port your app listens on with `-p hostPort:containerPort` (examples above use `8000:8000`).


## License

> This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.