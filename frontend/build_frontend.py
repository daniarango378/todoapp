from __future__ import annotations

import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
DIST_DIR = ROOT_DIR / "dist"


def build_frontend() -> list[Path]:
    if not SRC_DIR.exists():
        raise FileNotFoundError(f"Source directory not found: {SRC_DIR}")

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    shutil.copytree(SRC_DIR, DIST_DIR)

    expected_files = [
        DIST_DIR / "index.html",
        DIST_DIR / "css" / "styles.css",
        DIST_DIR / "js" / "api.js",
        DIST_DIR / "js" / "app.js",
    ]

    missing_files = [path for path in expected_files if not path.exists()]
    if missing_files:
        missing_list = ", ".join(str(path) for path in missing_files)
        raise FileNotFoundError(f"Build output is incomplete: {missing_list}")

    return expected_files


if __name__ == "__main__":
    files = build_frontend()
    print("Frontend build completed successfully.")
    for file_path in files:
        print(f"- {file_path.relative_to(ROOT_DIR)}")
