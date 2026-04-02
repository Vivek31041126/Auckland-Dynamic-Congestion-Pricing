from pathlib import Path
import runpy


PROJECT_ROOT = Path(__file__).resolve().parents[2]


if __name__ == "__main__":
    runpy.run_path(str(PROJECT_ROOT / "scripts" / "final" / "02_save_final_figures.py"), run_name="__main__")
