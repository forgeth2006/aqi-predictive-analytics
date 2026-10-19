"""Re-run the whole pipeline: the six notebooks in order, then the contract check and the tests.

Usage (from the repository root, with requirements-notebooks.txt installed):
    python scripts/run_all.py
"""
import subprocess
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ["01_wrangling", "02_eda", "03_regression", "04_classification", "05_timeseries", "06_control_charts"]

for name in NOTEBOOKS:
    path = ROOT / "notebooks" / f"{name}.ipynb"
    print(f"running {path.name} ...", flush=True)
    nb = nbformat.read(path, as_version=4)
    NotebookClient(nb, timeout=1800, kernel_name="python3",
                   resources={"metadata": {"path": str(path.parent)}}).execute()
    nbformat.write(nb, path)

print("contract check ...", flush=True)
subprocess.run([sys.executable, str(ROOT / "src" / "check_contract.py")], check=True)
print("tests ...", flush=True)
subprocess.run([sys.executable, "-m", "pytest", "-q", str(ROOT / "tests")], check=True)
print("all done")
