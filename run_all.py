
from pathlib import Path
import subprocess, sys, os

BASE = Path(__file__).resolve().parent
PY = sys.executable

print("Seeding SQLite with synthetic data...")
subprocess.check_call([PY, str(BASE / "src" / "setup_db.py")])

print("Running ETL pipeline...")
subprocess.check_call([PY, str(BASE / "src" / "etl.py")])

print("Done.")
