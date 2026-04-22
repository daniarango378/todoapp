from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"


def test_index_html_exists():
    assert (SRC_DIR / "index.html").exists()


def test_styles_css_exists():
    assert (SRC_DIR / "css" / "styles.css").exists()


def test_api_js_exists():
    assert (SRC_DIR / "js" / "api.js").exists()


def test_app_js_exists():
    assert (SRC_DIR / "js" / "app.js").exists()


def test_build_script_exists():
    assert (ROOT_DIR / "build_frontend.py").exists()


def test_serve_script_exists():
    assert (ROOT_DIR / "serve_frontend.py").exists()
