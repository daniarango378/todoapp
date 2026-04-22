from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
DIST_DIR = ROOT_DIR / "dist"


def test_index_html_contains_expected_structure():
    content = (SRC_DIR / "index.html").read_text(encoding="utf-8").lower()

    assert "<html" in content
    assert "<form" in content
    assert 'id="task-form"' in content
    assert 'id="pending-tasks"' in content
    assert 'id="in_progress-tasks"' in content
    assert 'id="done-tasks"' in content


def test_app_js_contains_task_loading_logic():
    content = (SRC_DIR / "js" / "app.js").read_text(encoding="utf-8")

    assert "async function loadTasks()" in content
    assert "window.taskApi.listTasks()" in content
    assert "addEventListener(\"submit\"" in content


def test_api_js_contains_api_functions():
    content = (SRC_DIR / "js" / "api.js").read_text(encoding="utf-8")

    assert "const taskApi" in content
    assert "listTasks()" in content
    assert "createTask(task)" in content
    assert "updateTask(taskId, task)" in content
    assert "deleteTask(taskId)" in content


def test_index_html_loads_runtime_config_before_app_scripts():
    content = (SRC_DIR / "index.html").read_text(encoding="utf-8")

    runtime_config_pos = content.index('./js/runtime-config.js')
    api_pos = content.index('./js/api.js')
    app_pos = content.index('./js/app.js')

    assert runtime_config_pos < api_pos < app_pos


def test_frontend_build_creates_dist_and_copies_files():
    subprocess.run(
        [sys.executable, str(ROOT_DIR / "build_frontend.py")],
        cwd=ROOT_DIR.parent,
        check=True,
    )

    assert DIST_DIR.exists()
    assert (DIST_DIR / "index.html").exists()
    assert (DIST_DIR / "css" / "styles.css").exists()
    assert (DIST_DIR / "js" / "api.js").exists()
    assert (DIST_DIR / "js" / "app.js").exists()
