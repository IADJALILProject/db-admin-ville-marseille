# scripts/python/simulate_data.py

from pathlib import Path

from data_sources_generator import main as generate_sources  # type: ignore
from data_generated_generator import main as generate_generated  # type: ignore


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
SOURCES_DIR = DATA_DIR / "sources"
GENERATED_DIR = DATA_DIR / "generated"


def run() -> None:
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    generate_sources()
    generate_generated()


if __name__ == "__main__":
    run()
