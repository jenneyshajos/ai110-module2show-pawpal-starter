"""Tests for the PawPal+ classes in pawpal_system.py."""

from datetime import datetime

from pawpal_system import Pet, Task


def make_task(description: str = "Breakfast") -> Task:
    """Return a simple sample task."""
    return Task(description, "Mia", "feeding", datetime(2026, 10, 31, 7, 30), 10)


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mia", "cat", 5)
    assert len(pet.get_tasks()) == 0

    pet.add_task(make_task())

    assert len(pet.get_tasks()) == 1
