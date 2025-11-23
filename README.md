# Warehouse-management-and-storage-optimization

## Installation Guide

### Prerequisites
- Python **3.9 or higher** (3.12 recommended)
- Git installed

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/zombieTDV/Warehouse-management-and-storage-optimization.git
```
```bash
cd Warehouse-management-and-storage-optimization
```

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

### Step 4: Run the Application
- Run the shim launcher at project root:
```bash
  python src/main.py --input src/input_dataset1.txt --output src/output_dataset1.txt
```
---

### Step 5: Run the test-cases

```bash
pytest -q
```
