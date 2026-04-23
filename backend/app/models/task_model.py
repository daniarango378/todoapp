"""Task domain model and shared task status definitions."""

from __future__ import annotations

from dataclasses import dataclass

VALID_STATUSES = {"pending", "in_progress", "done"}


@dataclass
class Task:
    """Represents a task managed by the application."""

    id: int
    title: str
    description: str
    status: str

    def to_dict(self) -> dict:
        """Return the task as a serializable dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
        }
