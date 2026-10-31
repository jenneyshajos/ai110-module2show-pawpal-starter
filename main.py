"""Testing ground: build a sample owner, pets, and tasks, then print today's schedule."""

from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Task


def at(hour: int, minute: int = 0) -> datetime:
    """Return a datetime for today at the given time."""
    return datetime.combine(date.today(), time(hour, minute))


PRIORITY_COLORS = {1: "🔴", 2: "🟡", 3: "🟢"}


def print_schedule(owner: Owner) -> None:
    """Print today's tasks in time order."""
    tasks = owner.view_todays_tasks()

    print(f"\n🐾 Today's Schedule for {owner.name} ({date.today():%A, %B %d})")
    print("-" * 52)
    for task in tasks:
        status = "✓" if task.completed else " "
        print(
            f"[{status}] {PRIORITY_COLORS[task.priority]} {task.scheduled_time:%I:%M %p}  "
            f"{task.pet_name:<6} {task.description:<20} "
            f"{task.duration_min:>3} min"
        )
    print("-" * 52)
    total = sum(task.duration_min for task in tasks)
    print(f"{len(tasks)} tasks, {total} minutes total")
    print("🔴 high   🟡 medium   🟢 low\n")


def main() -> None:
    owner = Owner("Jenney", available_minutes=90)

    rex = Pet("Rex", "dog", 3)
    mia = Pet("Mia", "cat", 5)
    owner.add_pet(rex)
    owner.add_pet(mia)

    # Added out of order on purpose so the schedule shows sorting by time.
    owner.schedule_walk(rex, at(18, 0), 30)
    owner.scheduler.add_task(
        mia, Task("Breakfast", "Mia", "feeding", at(7, 30), 10, frequency="daily", priority=1)
    )
    owner.schedule_walk(rex, at(8, 0), 30)
    owner.scheduler.add_task(
        mia, Task("Brush fur", "Mia", "grooming", at(15, 0), 15, priority=3)
    )
    owner.scheduler.add_task(
        rex, Task("Heartworm pill", "Rex", "medication", at(9, 0), 5, priority=1)
    )

    print_schedule(owner)


if __name__ == "__main__":
    main()
