from pathlib import Path
import runpy


PROJECT_ROOT = Path(__file__).resolve().parents[2]


if __name__ == "__main__":
    runpy.run_path(str(PROJECT_ROOT / "scripts" / "pricing" / "02_price_from_arima.py"), run_name="__main__")
