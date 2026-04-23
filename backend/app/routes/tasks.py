"""Flask routes for task management operations."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from app.services.task_service import TaskNotFoundError, ValidationError

tasks_bp = Blueprint("tasks", __name__)


def _service():
    """Return the task service configured in the Flask application."""
    return current_app.config["TASK_SERVICE"]


@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task from the incoming JSON payload."""
    payload = request.get_json(silent=True) or {}
    task = _service().create_task(
        title=payload.get("title"),
        description=payload.get("description", ""),
        status=payload.get("status", "pending"),
    )
    return jsonify(task), 201


@tasks_bp.route("/tasks", methods=["GET"])
def list_tasks():
    """Return all tasks currently stored in the system."""
    return jsonify(_service().list_tasks()), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id: int):
    """Return a single task identified by its ID."""
    return jsonify(_service().get_task(task_id)), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id: int):
    """Update all editable fields of an existing task."""
    payload = request.get_json(silent=True) or {}
    task = _service().update_task(
        task_id=task_id,
        title=payload.get("title"),
        description=payload.get("description"),
        status=payload.get("status"),
    )
    return jsonify(task), 200


@tasks_bp.route("/tasks/<int:task_id>/status", methods=["PATCH"])
def update_task_status(task_id: int):
    """Update only the status field of an existing task."""
    payload = request.get_json(silent=True) or {}
    task = _service().update_task_status(task_id, payload.get("status"))
    return jsonify(task), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id: int):
    """Delete a task identified by its ID and return the deleted record."""
    deleted = _service().delete_task(task_id)
    return (
        jsonify(
            {
                "message": "Task deleted successfully.",
                "task": deleted,
            }
        ),
        200,
    )


@tasks_bp.errorhandler(TaskNotFoundError)
def handle_not_found(error: TaskNotFoundError):
    """Return a 404 response when the requested task does not exist."""
    return jsonify({"error": str(error)}), 404


@tasks_bp.errorhandler(ValidationError)
def handle_validation(error: ValidationError):
    """Return a 400 response when the request payload is invalid."""
    return jsonify({"error": str(error)}), 400