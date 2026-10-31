"""PawPal+ system classes: Owner, Pet, Task, and Scheduler (skeleton from diagrams/uml.mmd)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from itertools import combinations

# How far ahead each frequency's next occurrence is; None means it doesn't repeat.
FREQUENCIES = {"once": None, "daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
PRIORITY_LEVELS = (1, 2, 3)  # 1 = high, 2 = medium, 3 = low


def time_key(task: Task) -> tuple[datetime, int]:
    """Sort key: earliest first, and higher priority first when times match.

    Python compares tuples one item at a time, so tasks are ordered by scheduled_time
    and priority is only looked at as a tie-breaker. Priority 1 (high) sorts before 3 (low).
    """
    return (task.scheduled_time, task.priority)


def describe_conflict(first: Task, second: Task) -> str:
    """Return a readable warning for two clashing tasks, where first starts no later than second."""
    if first.pet_name == second.pet_name:
        who = f"Same pet ({first.pet_name})"
    else:
        who = f"Different pets ({first.pet_name} & {second.pet_name})"
    if first.scheduled_time == second.scheduled_time:
        what = (
            f"'{first.description}' and '{second.description}' "
            f"both start at {first.scheduled_time:%I:%M %p}"
        )
    else:
        what = (
            f"'{second.description}' at {second.scheduled_time:%I:%M %p} starts "
            f"before '{first.description}' ends at {first.end_time:%I:%M %p}"
        )
    return f"{who}: {what}"


# eq=False so tasks compare by identity: two separate but identical tasks stay two tasks.
@dataclass(eq=False)
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

    def __post_init__(self) -> None:
        """Reject values the scheduler can't handle."""
        if self.priority not in PRIORITY_LEVELS:
            raise ValueError(f"priority must be 1, 2, or 3, not {self.priority!r}")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(FREQUENCIES)}, not {self.frequency!r}")
        if self.duration_min <= 0:
            raise ValueError(f"duration_min must be positive, not {self.duration_min!r}")

    @property
    def end_time(self) -> datetime:
        """Return when this task finishes."""
        return self.scheduled_time + timedelta(minutes=self.duration_min)

    def overlaps(self, other: Task) -> bool:
        """Return True if this task and other are scheduled at overlapping times.

        Two time ranges overlap when each one starts before the other ends. Tasks that
        only touch (one ends at 8:30, the next starts at 8:30) do not overlap.
        """
        return self.scheduled_time < other.end_time and other.scheduled_time < self.end_time

    def mark_complete(self) -> Task | None:
        """Mark this task as completed and return its next occurrence, if it repeats.

        The next occurrence is today + 1 day (daily) or today + 7 days (weekly), at the
        same time of day. A task finished early counts from its own due date instead,
        so completing tomorrow's task today doesn't create a second one for tomorrow.
        """
        self.completed = True
        step = FREQUENCIES[self.frequency]
        if step is None:
            return None
        base_day = max(self.scheduled_time.date(), date.today())
        next_time = datetime.combine(base_day + step, self.scheduled_time.time())
        return replace(self, scheduled_time=next_time, completed=False)

    def is_due_today(self) -> bool:
        """Return True if this task is scheduled for today."""
        return self.scheduled_time.date() == date.today()


@dataclass(eq=False)
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


@dataclass
class DailyPlan:
    """Today's plan: the tasks that fit the time budget, the ones that didn't, and the minutes used."""

    available: int
    planned: list[Task] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)
    used: int = 0

    @property
    def remaining(self) -> int:
        """Return the minutes left after the planned tasks."""
        return self.available - self.used


class Scheduler:
    """Handles scheduling and sorting for every task across a list of pets."""

    def __init__(self, pets: list[Pet] | None = None) -> None:
        """Start the scheduler over a list of pets (shared with the owner, if given)."""
        self.pets: list[Pet] = pets if pets is not None else []

    @property
    def tasks(self) -> list[Task]:
        """Return every task across all pets; the pets' lists are the single source of truth."""
        return [task for pet in self.pets for task in pet.tasks]

    def add_task(self, pet: Pet, task: Task, auto_shift: bool = False) -> Task:
        """Add a task for the given pet, moving it to the next free slot if auto_shift is set."""
        if auto_shift:
            task.scheduled_time = self.next_free_slot(task.duration_min, task.scheduled_time)
        task.pet_name = pet.name
        if not any(known is pet for known in self.pets):
            self.pets.append(pet)
        pet.add_task(task)
        return task

    def schedule(
        self,
        pet: Pet,
        description: str,
        task_type: str,
        time: datetime,
        duration_min: int,
        frequency: str = "once",
        priority: int = 2,
        auto_shift: bool = False,
    ) -> Task:
        """Create a task for the given pet, add it, and return it."""
        task = Task(description, pet.name, task_type, time, duration_min, frequency, priority)
        return self.add_task(pet, task, auto_shift)

    def schedule_walk(self, pet: Pet, time: datetime, duration_min: int) -> Task:
        """Create a walk task for the given pet and return it."""
        return self.schedule(pet, f"Walk {pet.name}", "walk", time, duration_min)

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task done and add its next occurrence to the same pet if it repeats.

        Task.mark_complete works out the next date; this method finds the pet that owns
        the finished task and gives the new copy to that pet. Returns the new task, or
        None for a one-time task.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            pet = next(pet for pet in self.pets if any(t is task for t in pet.tasks))
            pet.add_task(next_task)
        return next_task

    def sort_by_time(self) -> list[Task]:
        """Return every pet's tasks in one list, sorted by scheduled time.

        Sorts fresh on each call (using time_key), so the order is always right even if
        a task's time was changed after it was added.
        """
        return sorted(self.tasks, key=time_key)

    def get_todays_tasks(self) -> list[Task]:
        """Return the tasks that are due today, ordered by time."""
        return [task for task in self.sort_by_time() if task.is_due_today()]

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        task_type: str | None = None,
    ) -> list[Task]:
        """Return tasks in time order, keeping only those that match every filter given.

        A filter left as None is ignored, so filters can be combined freely:
        filter_tasks(pet_name="Rex", completed=False) returns Rex's unfinished tasks,
        and filter_tasks() with no filters returns every task.
        """
        return [
            task
            for task in self.sort_by_time()
            if (pet_name is None or task.pet_name == pet_name)
            and (completed is None or task.completed == completed)
            and (task_type is None or task.task_type == task_type)
        ]

    def find_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of today's pending tasks whose times overlap, earlier task first.

        Compares every pair of today's unfinished tasks with Task.overlaps. This covers
        clashes for the same pet and between different pets, since the owner can only
        do one thing at a time. Checking every pair is simple and fast enough for the
        few dozen tasks a day an owner would have.
        """
        pending = [task for task in self.get_todays_tasks() if not task.completed]
        return [(first, second) for first, second in combinations(pending, 2) if first.overlaps(second)]

    def conflict_warnings(self) -> list[str]:
        """Return a readable warning for each clash; bad task data becomes a warning, not a crash."""
        try:
            return [describe_conflict(first, second) for first, second in self.find_conflicts()]
        except (TypeError, AttributeError) as error:
            return [f"Could not check today's tasks for conflicts: {error}"]

    def check_conflict(self, task: Task) -> str | None:
        """Return a warning if task overlaps any pending task, otherwise None.

        Lightweight: it compares one task against the others instead of re-checking
        every pair in the schedule, and it never raises, so bad data comes back as a warning.
        """
        try:
            return self._first_clash(task)
        except (TypeError, AttributeError) as error:
            return f"Could not check '{getattr(task, 'description', task)}' for conflicts: {error}"

    def add_task_with_warning(self, pet: Pet, task: Task) -> str | None:
        """Add a task and return a warning if it clashes or can't be added, otherwise None.

        A clash doesn't stop the task from being added; the owner decides what to do.
        A task that can't even be compared with the others (bad time data) is left out.
        """
        try:
            warning = self._first_clash(task)
        except (TypeError, AttributeError) as error:
            return f"Could not add '{getattr(task, 'description', task)}': {error}"
        self.add_task(pet, task)
        return warning

    def _first_clash(self, task: Task) -> str | None:
        """Return a warning for the first pending task that overlaps task, otherwise None.

        Stops at the first clash it finds. Completed tasks and the task itself are
        skipped. Raises TypeError if the times can't be compared (for example, mixing
        timezone-aware and plain times); the public callers turn that into a warning.
        """
        for other in self.tasks:
            if other is not task and not other.completed and task.overlaps(other):
                first, second = sorted((other, task), key=time_key)
                return describe_conflict(first, second)
        return None

    def next_free_slot(self, duration_min: int, after: datetime) -> datetime:
        """Return the earliest start at or after `after` with duration_min free minutes.

        Walks through the tasks in time order with a candidate start time. Tasks that
        are completed or already over by the candidate time are skipped. If the next
        task starts late enough to leave room, the candidate fits and is returned;
        otherwise the candidate moves to the end of that task and the search continues.
        """
        start = after
        for task in self.sort_by_time():
            if task.completed or task.end_time <= start:
                continue
            if task.scheduled_time >= start + timedelta(minutes=duration_min):
                break
            start = task.end_time
        return start

    def build_daily_plan(self, available_minutes: int) -> DailyPlan:
        """Pick today's tasks by priority until the time budget is used, ordered by time.

        A greedy, priority-first approach: unfinished tasks are tried from high to low
        priority, and each one that still fits in the remaining minutes is planned; the
        rest are skipped. This keeps important tasks in the plan even if it leaves some
        minutes unused. Both lists in the returned DailyPlan are in time order.
        """
        pending = [task for task in self.get_todays_tasks() if not task.completed]
        # Most important first; earlier tasks win ties within the same priority.
        pending.sort(key=lambda task: (task.priority, task.scheduled_time))

        plan = DailyPlan(available=available_minutes)
        for task in pending:
            if task.duration_min <= plan.remaining:
                plan.planned.append(task)
                plan.used += task.duration_min
            else:
                plan.skipped.append(task)

        plan.planned.sort(key=time_key)
        plan.skipped.sort(key=time_key)
        return plan


class Owner:
    """The pet owner; the entry point for adding pets and viewing tasks."""

    def __init__(self, name: str, available_minutes: int = 120) -> None:
        """Create an owner with no pets, a daily time budget, and a scheduler over their pets."""
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []
        self.scheduler = Scheduler(self.pets)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner; its tasks become visible to the scheduler."""
        if not any(known is pet for known in self.pets):
            self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return all of this owner's pets."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return self.scheduler.tasks

    def schedule(
        self,
        pet: Pet,
        description: str,
        task_type: str,
        time: datetime,
        duration_min: int,
        frequency: str = "once",
        priority: int = 2,
        auto_shift: bool = False,
    ) -> Task:
        """Schedule any kind of task for a pet through the scheduler."""
        return self.scheduler.schedule(
            pet, description, task_type, time, duration_min, frequency, priority, auto_shift
        )

    def schedule_walk(self, pet: Pet, time: datetime, duration_min: int) -> Task:
        """Schedule a walk for a pet through the scheduler."""
        return self.scheduler.schedule_walk(pet, time, duration_min)

    def view_todays_tasks(self) -> list[Task]:
        """Return today's tasks through the scheduler."""
        return self.scheduler.get_todays_tasks()

    def get_daily_plan(self) -> DailyPlan:
        """Return today's plan within this owner's available minutes."""
        return self.scheduler.build_daily_plan(self.available_minutes)
