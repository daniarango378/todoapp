from __future__ import annotations

import pytest

from app import create_app
from app.services.task_service import TaskService


@pytest.fixture
def sample_task_data():
    return {
        "title": "Prepare CI pipeline",
        "description": "Create the base validation flow for tests",
        "status": "pending",
    }


@pytest.fixture
def task_service():
    service = TaskService()
    service.reset()
    return service


@pytest.fixture
def app(task_service):
    flask_app = create_app({"TESTING": True, "TASK_SERVICE": task_service})
    return flask_app


@pytest.fixture
def test_client(app):
    return app.test_client()
