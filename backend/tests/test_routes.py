from __future__ import annotations


def test_post_tasks_creates_task_and_returns_201(test_client, sample_task_data):
    response = test_client.post("/tasks", json=sample_task_data)

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["id"] == 1
    assert payload["title"] == sample_task_data["title"]


def test_get_tasks_returns_list_and_200(test_client, sample_task_data):
    test_client.post("/tasks", json=sample_task_data)

    response = test_client.get("/tasks")

    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert len(payload) == 1


def test_get_task_by_id_returns_existing_task(test_client, sample_task_data):
    created = test_client.post("/tasks", json=sample_task_data).get_json()

    response = test_client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.get_json()["id"] == created["id"]


def test_put_task_updates_task(test_client, sample_task_data):
    created = test_client.post("/tasks", json=sample_task_data).get_json()

    response = test_client.put(
        f"/tasks/{created['id']}",
        json={
            "title": "Refined task",
            "description": "Updated from route test",
            "status": "in_progress",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["title"] == "Refined task"
    assert payload["status"] == "in_progress"


def test_patch_task_status_changes_status(test_client, sample_task_data):
    created = test_client.post("/tasks", json=sample_task_data).get_json()

    response = test_client.patch(
        f"/tasks/{created['id']}/status",
        json={"status": "done"},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "done"


def test_delete_task_removes_task(test_client, sample_task_data):
    created = test_client.post("/tasks", json=sample_task_data).get_json()

    response = test_client.delete(f"/tasks/{created['id']}")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["task"]["id"] == created["id"]
    assert payload["message"] == "Task deleted successfully."


def test_get_task_returns_404_when_not_found(test_client):
    response = test_client.get("/tasks/321")

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_post_task_returns_400_for_invalid_data(test_client):
    response = test_client.post(
        "/tasks",
        json={"title": "", "description": "Invalid task", "status": "pending"},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()
