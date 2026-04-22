from __future__ import annotations

from typing import Dict, List, Optional

from app.models.task_model import Task, VALID_STATUSES


class TaskNotFoundError(Exception):
    """Raised when a task cannot be found."""


class ValidationError(Exception):
    """Raised when task data does not meet business rules."""


class TaskService:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1

    def list_tasks(self) -> List[dict]:
        return [task.to_dict() for task in self._tasks.values()]

    def get_task(self, task_id: int) -> dict:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task with id {task_id} was not found.")
        return task.to_dict()

    def create_task(self, title: str, description: str = "", status: str = "pending") -> dict:
        normalized_title = self._validate_title(title)
        normalized_status = self._validate_status(status)
        task = Task(
            id=self._next_id,
            title=normalized_title,
            description=(description or "").strip(),
            status=normalized_status,
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task.to_dict()

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        task = self._require_task(task_id)
        if title is not None:
            task.title = self._validate_title(title)
        if description is not None:
            task.description = description.strip()
        if status is not None:
            task.status = self._validate_status(status)
        return task.to_dict()

    def update_task_status(self, task_id: int, status: str) -> dict:
        task = self._require_task(task_id)
        task.status = self._validate_status(status)
        return task.to_dict()

    def delete_task(self, task_id: int) -> dict:
        task = self._tasks.pop(task_id, None)
        if task is None:
            raise TaskNotFoundError(f"Task with id {task_id} was not found.")
        return task.to_dict()

    def _require_task(self, task_id: int) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task with id {task_id} was not found.")
        return task

    @staticmethod
    def _validate_title(title: Optional[str]) -> str:
        if title is None or not title.strip():
            raise ValidationError("Title is required.")
        return title.strip()

    @staticmethod
    def _validate_status(status: Optional[str]) -> str:
        if status is None or status not in VALID_STATUSES:
            raise ValidationError(
                "Status must be one of: pending, in_progress, done."
            )
        return status
