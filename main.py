from pathlib import Path

from slrresearch.td08_runtime import load_td08_artifacts

ROOT = Path(__file__).parent


def main():
    _evidence, _required_rqs, _draft, _repaired = load_td08_artifacts(ROOT)
    print("TD08 : complétez les TODO 1 à 9, puis lancez streamlit_app.py.")


if __name__ == "__main__":
    main()

