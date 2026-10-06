"""Project path helpers that do not depend on the current working directory."""

from pathlib import Path


def get_project_root() -> Path:
    """Find the project root from this module's location."""
    current = Path(__file__).resolve().parent

    while True:
        if (current / "data").is_dir() and (current / "pyproject.toml").is_file():
            return current

        if current.parent == current:
            raise FileNotFoundError("프로젝트 루트를 찾을 수 없습니다.")

        current = current.parent


def get_data_dir() -> Path:
    """Return the project's data directory."""
    return get_project_root() / "data"
