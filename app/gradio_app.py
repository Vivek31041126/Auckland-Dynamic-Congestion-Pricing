from pathlib import Path
import runpy


LEGACY_APP = Path(__file__).resolve().parents[1] / "Gradio" / "app.py"
globals().update(
    {
        key: value
        for key, value in runpy.run_path(str(LEGACY_APP)).items()
        if not key.startswith("__")
    }
)


if __name__ == "__main__":
    build_app().launch()
