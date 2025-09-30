# Case-y

## Installation Guide

### Prerequisites
- Python **3.9 or higher** (3.12 recommended)
- Git installed

---

### Step 1: Clone the Repository
git clone [https://github.com/zombieTDV/Case-unknown.git](https://github.com/zombieTDV/Warehouse-management-and-storage-optimization.git)
cd Warehouse-management-and-storage-optimization
---

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
```

Activate the virtual environment:

- On Windows (PowerShell):
```bash
  .venv\Scripts\Activate.ps1
```
- On macOS/Linux:
```bash
  source .venv/bin/activate
```
---

### Step 3: Install the Project

Development mode (recommended):
```bash
pip install -e .[dev]
```
Runtime only (minimal install):
```bash
pip install -e .
```
---

### Step 4: Run the Application
- Run the shim launcher at project root:
```bash
  python main.py
```
---

## Contributing

We use pre-commit hooks to enforce style and quality checks (black, flake8, etc.).

### Setup pre-commit
```bash
pip install pre-commit
```
```bash
pre-commit install
```

Now, checks will run automatically before each commit.
To run them manually on all files:
```bash
pre-commit run --all-files
```
Our configuration lints all .py files in src/, tests/, and the project root (e.g. main.py).

---

## Development Notes
- Project follows the src/ layout (src/casey/ contains all source code).
- Root-level main.py is a thin shim for quick running in VS Code.
- For production/packaging, use `python -m casey.cli.menu` or the `casey` CLI entry point.
