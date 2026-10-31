"""Testing ground: build a sample owner, pets, and tasks, then print today's schedule."""

from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Task


def at(hour: int, minute: int = 0) -> datetime:
    """Return a datetime for today at the given time."""
    return datetime.combine(date.today(), time(hour, minute))


PRIORITY_COLORS = {1: "🔴", 2: "🟡", 3: "🟢"}


def task_line(task: Task, show_date: bool = False) -> str:
    """Format one task as a schedule row, optionally with its date."""
    status = "✓" if task.completed else " "
    when = f"{task.scheduled_time:%a %b %d %I:%M %p}" if show_date else f"{task.scheduled_time:%I:%M %p}"
    return (
        f"[{status}] {PRIORITY_COLORS[task.priority]} {when}  "
        f"{task.pet_name:<6} {task.description:<20} "
        f"{task.duration_min:>3} min"
    )


def print_schedule(owner: Owner) -> None:
    """Print today's plan, what was left out, any time conflicts, and the time budget."""
    plan = owner.get_daily_plan()

    print(f"\n🐾 Today's Plan for {owner.name} ({date.today():%A, %B %d})")
    print("-" * 52)
    for task in plan.planned:
        print(task_line(task))
    print("-" * 52)
    print(f"{len(plan.planned)} tasks, {plan.used} of {plan.available} minutes used, {plan.remaining} left")

    if plan.skipped:
        print("\nLeft out (not enough time):")
        for task in plan.skipped:
            print(task_line(task))

    warnings = owner.scheduler.conflict_warnings()
    if warnings:
        print("\n⚠️  Scheduling conflicts:")
        for warning in warnings:
            print(f"    {warning}")

    print("\n🔴 high   🟡 medium   🟢 low\n")


def main() -> None:
    owner = Owner("Jenney", available_minutes=90)

    rex = Pet("Rex", "dog", 3)
    mia = Pet("Mia", "cat", 5)
    owner.add_pet(rex)
    owner.add_pet(mia)

    # Added out of order on purpose so the schedule shows sorting by time.
    owner.schedule_walk(rex, at(18, 0), 30)
    breakfast = owner.schedule(mia, "Breakfast", "feeding", at(7, 30), 10, frequency="daily", priority=1)
    owner.schedule_walk(rex, at(8, 0), 30)
    owner.schedule(mia, "Brush fur", "grooming", at(15, 0), 15, priority=3)
    owner.schedule(mia, "Dinner", "feeding", at(17, 0), 10, priority=1)

    # Two tasks at the exact same time as ones already scheduled. Each is still added,
    # and the scheduler hands back a warning instead of crashing.
    print("Adding tasks at the same time as existing ones:")
    same_time_tasks = [
        (rex, Task("Ear cleaning", "Rex", "grooming", at(15, 0), 10, priority=3)),  # vs. Mia's brushing
        (mia, Task("Evening meds", "Mia", "medication", at(17, 0), 5, priority=1)),  # vs. Mia's dinner
    ]
    for pet, task in same_time_tasks:
        warning = owner.scheduler.add_task_with_warning(pet, task)
        print(f"  ⚠️  {warning}" if warning else f"  ✓ {task.description} added with no conflict")
    print()

    # 8:15 lands in the middle of the morning walk, so it shows up as a conflict.
    owner.schedule(rex, "Heartworm pill", "medication", at(8, 15), 5, priority=1)
    # Asked for 6:00 PM, but the evening walk is then, so it moves to the next free slot.
    owner.schedule(rex, "Play fetch", "play", at(18, 0), 20, priority=3, auto_shift=True)

    next_breakfast = owner.scheduler.complete_task(breakfast)
    print(f"Completed {breakfast.description}; next one is {next_breakfast.scheduled_time:%a %b %d at %I:%M %p}")

    print("\nAll tasks, sorted by time:")
    for task in owner.scheduler.sort_by_time():
        print(task_line(task, show_date=True))

    print("\nRex's tasks still to do:")
    for task in owner.scheduler.filter_tasks(pet_name="Rex", completed=False):
        print(task_line(task))

    print("\nCompleted tasks:")
    for task in owner.scheduler.filter_tasks(completed=True):
        print(task_line(task))

    print_schedule(owner)


if __name__ == "__main__":
    main()
