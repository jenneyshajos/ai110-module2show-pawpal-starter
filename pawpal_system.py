"""PawPal+ system classes: Owner, Pet, Task, and Scheduler (skeleton from diagrams/uml.mmd)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """One pet care activity, such as a walk or a feeding."""

    title: str
    task_type: str
    scheduled_time: datetime
    duration_min: int
    priority: str = "medium"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def is_due_today(self) -> bool:
        """Return True if this task is scheduled for today."""
        pass


@dataclass
class Pet:
    """A pet and its list of care tasks."""

    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        pass

    def get_tasks(self) -> list[Task]:
        """Return all of this pet's tasks."""
        pass


class Scheduler:
    """Holds every task and handles scheduling and sorting."""

    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def add_task(self, pet: Pet, task: Task) -> None:
        """Add a task for the given pet."""
        pass

    def schedule_walk(self, pet: Pet, time: datetime, duration_min: int) -> Task:
        """Create a walk task for the given pet and return it."""
        pass

    def get_todays_tasks(self) -> list[Task]:
        """Return the tasks that are due today."""
        pass

    def sort_by_time(self) -> list[Task]:
        """Return the tasks sorted by scheduled time."""
        pass


class Owner:
    """The pet owner; the entry point for adding pets and viewing tasks."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: list[Pet] = []
        self.scheduler = Scheduler()

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_pets(self) -> list[Pet]:
        """Return all of this owner's pets."""
        pass

    def schedule_walk(self, pet: Pet, time: datetime, duration_min: int) -> Task:
        """Schedule a walk for a pet through the scheduler."""
        pass

    def view_todays_tasks(self) -> list[Task]:
        """Return today's tasks through the scheduler."""
        pass
