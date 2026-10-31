"""PawPal+ system classes: Owner, Pet, Task, and Scheduler (skeleton from diagrams/uml.mmd)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Task:
    """One pet care activity, such as a walk or a feeding."""

    description: str
    pet_name: str
    task_type: str
    scheduled_time: datetime
    duration_min: int
    frequency: str = "once"  # "once", "daily", or "weekly"
    priority: int = 2  # 1 = high, 2 = medium, 3 = low
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_due_today(self) -> bool:
        """Return True if this task is scheduled for today."""
        return self.scheduled_time.date() == date.today()


@dataclass
class Pet:
    """A pet and its list of care tasks."""

    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all of this pet's tasks."""
        return list(self.tasks)


class Scheduler:
    """Holds every task and handles scheduling and sorting."""

    def __init__(self) -> None:
        """Start the scheduler with an empty task list."""
        self.tasks: list[Task] = []

    def add_task(self, pet: Pet, task: Task) -> None:
        """Add a task for the given pet."""
        task.pet_name = pet.name
        pet.add_task(task)
        self.tasks.append(task)

    def schedule_walk(self, pet: Pet, time: datetime, duration_min: int) -> Task:
        """Create a walk task for the given pet and return it."""
        walk = Task(
            description=f"Walk {pet.name}",
            pet_name=pet.name,
            task_type="walk",
            scheduled_time=time,
            duration_min=duration_min,
        )
        self.add_task(pet, walk)
        return walk

    def get_todays_tasks(self) -> list[Task]:
        """Return the tasks that are due today, ordered by time."""
        todays = [task for task in self.tasks if task.is_due_today()]
        return sorted(todays, key=lambda task: task.scheduled_time)

    def sort_by_time(self) -> list[Task]:
        """Return the tasks sorted by scheduled time."""
        return sorted(self.tasks, key=lambda task: task.scheduled_time)

    def build_daily_plan(self, available_minutes: int) -> list[Task]:
        """Pick today's tasks by priority until the time budget is used, ordered by time."""
        pending = [task for task in self.get_todays_tasks() if not task.completed]
        # Most important first; earlier tasks win ties within the same priority.
        pending.sort(key=lambda task: (task.priority, task.scheduled_time))

        plan: list[Task] = []
        minutes_left = available_minutes
        for task in pending:
            if task.duration_min <= minutes_left:
                plan.append(task)
                minutes_left -= task.duration_min

        return sorted(plan, key=lambda task: task.scheduled_time)


class Owner:
    """The pet owner; the entry point for adding pets and viewing tasks."""

    def __init__(self, name: str, available_minutes: int = 120) -> None:
        """Create an owner with no pets, a daily time budget, and their own scheduler."""
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []
        self.scheduler = Scheduler()

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner and register any tasks it already has."""
        self.pets.append(pet)
        for task in pet.tasks:
            if task not in self.scheduler.tasks:
                self.scheduler.tasks.append(task)

    def get_pets(self) -> list[Pet]:
        """Return all of this owner's pets."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    def schedule_walk(self, pet: Pet, time: datetime, duration_min: int) -> Task:
        """Schedule a walk for a pet through the scheduler."""
        return self.scheduler.schedule_walk(pet, time, duration_min)

    def view_todays_tasks(self) -> list[Task]:
        """Return today's tasks through the scheduler."""
        return self.scheduler.get_todays_tasks()

    def get_daily_plan(self) -> list[Task]:
        """Return today's plan within this owner's available minutes."""
        return self.scheduler.build_daily_plan(self.available_minutes)
