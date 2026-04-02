from pathlib import Path
import runpy


PROJECT_ROOT = Path(__file__).resolve().parents[2]


if __name__ == "__main__":
    runpy.run_path(str(PROJECT_ROOT / "scripts" / "02_aggregate_to_10min.py"), run_name="__main__")
