from __future__ import annotations

from dataclasses import dataclass


VALID_STATUSES = {"pending", "in_progress", "done"}


@dataclass
class Task:
    id: int
    title: str
    description: str
    status: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
        }
