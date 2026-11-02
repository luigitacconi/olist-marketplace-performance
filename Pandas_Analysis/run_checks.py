# Runs the five check files in order

import runpy
from pathlib import Path


FOLDER = Path(__file__).parent

FILES = [
    "checks_structure_keys.py",
    "checks_dates_amounts.py",
    "checks_missing_values.py",
    "checks_anomalies.py",
    "checks_temporal_coverage.py",
]

for name in FILES:
    print()
    print("=" * 20, name, "=" * 20)
    runpy.run_path(FOLDER / name)
