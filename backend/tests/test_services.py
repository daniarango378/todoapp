from __future__ import annotations

import pytest

from app.services.task_service import TaskNotFoundError, ValidationError


def test_create_task_success(task_service, sample_task_data):
    task = task_service.create_task(**sample_task_data)

    assert task["id"] == 1
    assert task["title"] == sample_task_data["title"]
    assert task["description"] == sample_task_data["description"]
    assert task["status"] == sample_task_data["status"]


def test_list_tasks_returns_created_tasks(task_service, sample_task_data):
    task_service.create_task(**sample_task_data)

    tasks = task_service.list_tasks()

    assert len(tasks) == 1
    assert tasks[0]["title"] == sample_task_data["title"]


def test_get_task_by_id_returns_expected_task(task_service, sample_task_data):
    created = task_service.create_task(**sample_task_data)

    task = task_service.get_task(created["id"])

    assert task == created


def test_update_task_modifies_existing_values(task_service, sample_task_data):
    created = task_service.create_task(**sample_task_data)

    updated = task_service.update_task(
        created["id"],
        title="Updated title",
        description="Updated description",
        status="in_progress",
    )

    assert updated["title"] == "Updated title"
    assert updated["description"] == "Updated description"
    assert updated["status"] == "in_progress"


def test_update_task_status_changes_only_status(task_service, sample_task_data):
    created = task_service.create_task(**sample_task_data)

    updated = task_service.update_task_status(created["id"], "done")

    assert updated["status"] == "done"
    assert updated["title"] == sample_task_data["title"]


def test_delete_task_removes_task_from_storage(task_service, sample_task_data):
    created = task_service.create_task(**sample_task_data)

    deleted = task_service.delete_task(created["id"])

    assert deleted["id"] == created["id"]
    assert task_service.list_tasks() == []


def test_get_task_raises_error_for_missing_task(task_service):
    with pytest.raises(TaskNotFoundError):
        task_service.get_task(999)


def test_update_status_raises_error_for_invalid_status(task_service, sample_task_data):
    created = task_service.create_task(**sample_task_data)

    with pytest.raises(ValidationError):
        task_service.update_task_status(created["id"], "blocked")


def test_create_task_raises_error_for_empty_title(task_service):
    with pytest.raises(ValidationError):
        task_service.create_task(title=" ", description="Missing title", status="pending")
