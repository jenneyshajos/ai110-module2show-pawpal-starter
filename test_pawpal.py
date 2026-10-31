"""Tests for the PawPal+ classes in pawpal_system.py."""

from datetime import date, datetime, time, timedelta, timezone

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def make_task(description: str = "Breakfast") -> Task:
    """Return a simple sample task."""
    return Task(description, "Mia", "feeding", datetime(2026, 10, 31, 7, 30), 10)


def at(hour: int, minute: int = 0) -> datetime:
    """Return a datetime for today at the given time."""
    return datetime.combine(date.today(), time(hour, minute))


def make_owner(available_minutes: int = 120) -> tuple[Owner, Pet, Pet]:
    """Return an owner with a dog and a cat and no tasks."""
    owner = Owner("Jenney", available_minutes)
    rex = Pet("Rex", "dog", 3)
    mia = Pet("Mia", "cat", 5)
    owner.add_pet(rex)
    owner.add_pet(mia)
    return owner, rex, mia


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


# Conflict detection


def test_find_conflicts_reports_overlapping_tasks():
    owner, rex, mia = make_owner()
    walk = owner.schedule_walk(rex, at(8, 0), 30)
    pill = owner.schedule(rex, "Heartworm pill", "medication", at(8, 15), 5)

    assert owner.scheduler.find_conflicts() == [(walk, pill)]


def test_back_to_back_tasks_do_not_conflict():
    owner, rex, mia = make_owner()
    owner.schedule_walk(rex, at(8, 0), 30)
    owner.schedule(mia, "Breakfast", "feeding", at(8, 30), 10)

    assert owner.scheduler.find_conflicts() == []


def test_completed_tasks_are_not_conflicts():
    owner, rex, mia = make_owner()
    walk = owner.schedule_walk(rex, at(8, 0), 30)
    owner.schedule(mia, "Breakfast", "feeding", at(8, 10), 10)

    owner.scheduler.complete_task(walk)

    assert owner.scheduler.find_conflicts() == []


def test_one_long_task_conflicts_with_each_task_inside_it():
    owner, rex, mia = make_owner()
    walk = owner.schedule_walk(rex, at(8, 0), 60)
    pill = owner.schedule(rex, "Pill", "medication", at(8, 10), 5)
    food = owner.schedule(mia, "Breakfast", "feeding", at(8, 30), 10)

    assert owner.scheduler.find_conflicts() == [(walk, pill), (walk, food)]


def test_same_pet_at_the_same_time_is_a_conflict():
    owner, rex, mia = make_owner()
    walk = owner.schedule_walk(rex, at(8, 0), 30)
    pill = owner.schedule(rex, "Pill", "medication", at(8, 0), 5)

    conflicts = owner.scheduler.find_conflicts()

    assert conflicts == [(walk, pill)]
    assert all(first.pet_name == second.pet_name for first, second in conflicts)


def test_different_pets_at_the_same_time_is_a_conflict():
    owner, rex, mia = make_owner()
    walk = owner.schedule_walk(rex, at(8, 0), 30)
    breakfast = owner.schedule(mia, "Breakfast", "feeding", at(8, 0), 10)

    conflicts = owner.scheduler.find_conflicts()

    assert conflicts == [(walk, breakfast)]
    assert all(first.pet_name != second.pet_name for first, second in conflicts)


def test_conflict_warnings_describe_same_time_and_overlap():
    owner, rex, mia = make_owner()
    owner.schedule_walk(rex, at(8, 0), 30)
    owner.schedule(mia, "Breakfast", "feeding", at(8, 0), 10)
    owner.schedule(rex, "Pill", "medication", at(8, 15), 5)

    assert owner.scheduler.conflict_warnings() == [
        "Different pets (Rex & Mia): 'Walk Rex' and 'Breakfast' both start at 08:00 AM",
        "Same pet (Rex): 'Pill' at 08:15 AM starts before 'Walk Rex' ends at 08:30 AM",
    ]


def test_no_conflict_warnings_for_a_clear_schedule():
    owner, rex, mia = make_owner()
    owner.schedule_walk(rex, at(8, 0), 30)
    owner.schedule(mia, "Breakfast", "feeding", at(9, 0), 10)

    assert owner.scheduler.conflict_warnings() == []


def test_check_conflict_returns_warning_for_a_clash():
    owner, rex, mia = make_owner()
    owner.schedule(mia, "Brush fur", "grooming", at(15, 0), 15)
    ears = Task("Ear cleaning", "Rex", "grooming", at(15, 0), 10)

    assert owner.scheduler.check_conflict(ears) == (
        "Different pets (Mia & Rex): 'Brush fur' and 'Ear cleaning' both start at 03:00 PM"
    )


def test_check_conflict_returns_none_when_clear():
    owner, rex, mia = make_owner()
    owner.schedule_walk(rex, at(8, 0), 30)
    done = owner.schedule(mia, "Breakfast", "feeding", at(9, 0), 10)
    owner.scheduler.complete_task(done)
    owner.schedule_walk(rex, at(10, 0) + timedelta(days=1), 30)

    # Back-to-back, a completed task, and a task on another day are all fine.
    assert owner.scheduler.check_conflict(Task("Pill", "Rex", "medication", at(8, 30), 5)) is None
    assert owner.scheduler.check_conflict(Task("Pill", "Rex", "medication", at(9, 0), 5)) is None
    assert owner.scheduler.check_conflict(Task("Pill", "Rex", "medication", at(10, 0), 5)) is None


def test_add_task_with_warning_still_adds_the_task():
    owner, rex, mia = make_owner()
    owner.schedule_walk(rex, at(8, 0), 30)
    pill = Task("Pill", "Rex", "medication", at(8, 15), 5)

    warning = owner.scheduler.add_task_with_warning(rex, pill)

    assert warning == "Same pet (Rex): 'Pill' at 08:15 AM starts before 'Walk Rex' ends at 08:30 AM"
    assert pill in rex.tasks


def test_add_task_with_warning_returns_none_when_clear():
    owner, rex, mia = make_owner()
    owner.schedule_walk(rex, at(8, 0), 30)

    assert owner.scheduler.add_task_with_warning(rex, Task("Pill", "Rex", "medication", at(9, 0), 5)) is None


def test_bad_time_data_gives_a_warning_instead_of_crashing():
    owner, rex, mia = make_owner()
    owner.schedule_walk(rex, at(8, 0), 30)
    # A timezone-aware time can't be compared with the plain times already scheduled.
    utc_pill = Task("Pill", "Rex", "medication", datetime.combine(date.today(), time(8, 0), timezone.utc), 5)

    assert owner.scheduler.check_conflict(utc_pill).startswith("Could not check 'Pill'")
    assert owner.scheduler.add_task_with_warning(rex, utc_pill).startswith("Could not add 'Pill'")
    assert utc_pill not in rex.tasks


# Recurring tasks


def test_daily_task_creates_next_occurrence_tomorrow():
    owner, rex, mia = make_owner()
    breakfast = owner.schedule(mia, "Breakfast", "feeding", at(7, 30), 10, frequency="daily")

    next_task = owner.scheduler.complete_task(breakfast)

    assert breakfast.completed is True
    assert next_task.completed is False
    assert next_task.scheduled_time == at(7, 30) + timedelta(days=1)
    assert next_task in mia.tasks


def test_weekly_task_creates_next_occurrence_next_week():
    task = Task("Bath", "Rex", "grooming", at(9, 0), 20, frequency="weekly")

    next_task = task.mark_complete()

    assert next_task.scheduled_time == at(9, 0) + timedelta(weeks=1)


def test_overdue_daily_task_repeats_from_today_not_its_old_date():
    three_days_ago = at(7, 30) - timedelta(days=3)
    task = Task("Breakfast", "Mia", "feeding", three_days_ago, 10, frequency="daily")

    next_task = task.mark_complete()

    assert next_task.scheduled_time == at(7, 30) + timedelta(days=1)


def test_daily_task_finished_early_repeats_from_its_own_date():
    tomorrow = at(7, 30) + timedelta(days=1)
    task = Task("Breakfast", "Mia", "feeding", tomorrow, 10, frequency="daily")

    next_task = task.mark_complete()

    assert next_task.scheduled_time == tomorrow + timedelta(days=1)


def test_next_occurrence_keeps_the_task_details():
    task = Task("Pill", "Rex", "medication", at(9, 0), 5, frequency="daily", priority=1)

    next_task = task.mark_complete()

    assert next_task is not task
    assert (next_task.description, next_task.pet_name, next_task.task_type) == ("Pill", "Rex", "medication")
    assert (next_task.duration_min, next_task.frequency, next_task.priority) == (5, "daily", 1)


def test_one_time_task_does_not_repeat():
    owner, rex, mia = make_owner()
    walk = owner.schedule_walk(rex, at(8, 0), 30)

    assert owner.scheduler.complete_task(walk) is None
    assert len(rex.tasks) == 1


# Skipped tasks and budget


def test_daily_plan_reports_tasks_that_do_not_fit():
    owner, rex, mia = make_owner(available_minutes=40)
    pill = owner.schedule(rex, "Pill", "medication", at(9, 0), 5, priority=1)
    walk = owner.schedule_walk(rex, at(8, 0), 30)
    brush = owner.schedule(mia, "Brush fur", "grooming", at(15, 0), 15, priority=3)

    plan = owner.get_daily_plan()

    assert plan.planned == [walk, pill]
    assert plan.skipped == [brush]


def test_daily_plan_counts_used_and_remaining_minutes():
    owner, rex, mia = make_owner(available_minutes=60)
    owner.schedule_walk(rex, at(8, 0), 30)
    owner.schedule(mia, "Breakfast", "feeding", at(7, 30), 10)

    plan = owner.get_daily_plan()

    assert (plan.used, plan.available, plan.remaining) == (40, 60, 20)


# Next free slot and auto-shift


def test_next_free_slot_skips_past_busy_times():
    owner, rex, mia = make_owner()
    owner.schedule_walk(rex, at(8, 0), 30)
    owner.schedule(mia, "Breakfast", "feeding", at(8, 40), 10)

    # The 10-minute gap from 8:30 to 8:40 is too short for 15 minutes.
    assert owner.scheduler.next_free_slot(15, at(8, 0)) == at(8, 50)
    # But it fits a 10-minute task.
    assert owner.scheduler.next_free_slot(10, at(8, 0)) == at(8, 30)


def test_next_free_slot_returns_requested_time_when_free():
    owner, rex, mia = make_owner()
    owner.schedule_walk(rex, at(8, 0), 30)

    assert owner.scheduler.next_free_slot(20, at(12, 0)) == at(12, 0)


def test_auto_shift_moves_task_out_of_a_conflict():
    owner, rex, mia = make_owner()
    owner.schedule_walk(rex, at(18, 0), 30)

    fetch = owner.schedule(rex, "Play fetch", "play", at(18, 0), 20, auto_shift=True)

    assert fetch.scheduled_time == at(18, 30)
    assert owner.scheduler.find_conflicts() == []


def test_without_auto_shift_task_keeps_its_time():
    owner, rex, mia = make_owner()
    owner.schedule_walk(rex, at(18, 0), 30)

    fetch = owner.schedule(rex, "Play fetch", "play", at(18, 0), 20)

    assert fetch.scheduled_time == at(18, 0)


# Filtering


def test_filter_tasks_by_pet_status_and_type():
    owner, rex, mia = make_owner()
    walk = owner.schedule_walk(rex, at(8, 0), 30)
    pill = owner.schedule(rex, "Pill", "medication", at(9, 0), 5)
    breakfast = owner.schedule(mia, "Breakfast", "feeding", at(7, 30), 10)
    owner.scheduler.complete_task(walk)

    scheduler = owner.scheduler
    assert scheduler.filter_tasks(pet_name="Rex") == [walk, pill]
    assert scheduler.filter_tasks(completed=False) == [breakfast, pill]
    assert scheduler.filter_tasks(pet_name="Rex", completed=False) == [pill]
    assert scheduler.filter_tasks(task_type="feeding") == [breakfast]
    assert scheduler.filter_tasks() == [breakfast, walk, pill]


# Sorting


def test_higher_priority_comes_first_at_the_same_time():
    owner, rex, mia = make_owner()
    brush = owner.schedule(mia, "Brush fur", "grooming", at(8, 0), 10, priority=3)
    pill = owner.schedule(rex, "Pill", "medication", at(8, 0), 5, priority=1)

    assert owner.view_todays_tasks() == [pill, brush]


def test_sorting_still_correct_after_a_task_time_is_changed():
    owner, rex, mia = make_owner()
    breakfast = owner.schedule(mia, "Breakfast", "feeding", at(7, 30), 10)
    walk = owner.schedule_walk(rex, at(8, 0), 30)

    breakfast.scheduled_time = at(9, 0)  # moved after it was added

    assert owner.scheduler.sort_by_time() == [walk, breakfast]


def test_overlaps_is_true_only_for_overlapping_times():
    walk = Task("Walk", "Rex", "walk", at(8, 0), 30)

    assert walk.overlaps(Task("Pill", "Rex", "medication", at(8, 15), 5))
    assert walk.overlaps(Task("Pill", "Rex", "medication", at(7, 50), 15))
    assert not walk.overlaps(Task("Pill", "Rex", "medication", at(8, 30), 5))
    assert not walk.overlaps(Task("Pill", "Rex", "medication", at(7, 50), 10))


def test_sort_by_time_merges_tasks_across_pets():
    owner, rex, mia = make_owner()
    evening = owner.schedule_walk(rex, at(18, 0), 30)
    breakfast = owner.schedule(mia, "Breakfast", "feeding", at(7, 30), 10)
    morning = owner.schedule_walk(rex, at(8, 0), 30)

    assert owner.scheduler.sort_by_time() == [breakfast, morning, evening]


# Generic task helper


def test_schedule_fills_in_pet_name_and_options():
    owner, rex, mia = make_owner()

    task = owner.schedule(mia, "Breakfast", "feeding", at(7, 30), 10, frequency="daily", priority=1)

    assert task.pet_name == "Mia"
    assert task.frequency == "daily"
    assert task.priority == 1
    assert task in mia.tasks


def test_schedule_walk_uses_generic_helper():
    owner, rex, mia = make_owner()

    walk = owner.schedule_walk(rex, at(8, 0), 30)

    assert walk.description == "Walk Rex"
    assert walk.task_type == "walk"
    assert walk in rex.tasks


# One source of truth


def test_identical_tasks_are_kept_as_separate_tasks():
    owner, rex, mia = make_owner()
    first = Task("Treat", "Rex", "feeding", at(12, 0), 5)
    second = Task("Treat", "Rex", "feeding", at(12, 0), 5)

    owner.scheduler.add_task(rex, first)
    owner.scheduler.add_task(rex, second)

    assert len(owner.get_all_tasks()) == 2


def test_tasks_added_to_pet_directly_are_seen_by_scheduler():
    owner, rex, mia = make_owner()
    task = Task("Breakfast", "Mia", "feeding", at(7, 30), 10)

    mia.add_task(task)

    assert owner.view_todays_tasks() == [task]


def test_pet_with_existing_tasks_is_registered_once():
    owner = Owner("Jenney")
    pet = Pet("Rex", "dog", 3, tasks=[Task("Walk", "Rex", "walk", at(8, 0), 30)])

    owner.add_pet(pet)
    owner.add_pet(pet)

    assert len(owner.get_pets()) == 1
    assert len(owner.get_all_tasks()) == 1


def test_standalone_scheduler_tracks_pets_it_is_given():
    scheduler = Scheduler()
    rex = Pet("Rex", "dog", 3)

    walk = scheduler.schedule_walk(rex, at(8, 0), 30)

    assert scheduler.pets == [rex]
    assert scheduler.tasks == [walk]


# Input validation


@pytest.mark.parametrize(
    "overrides",
    [{"priority": 0}, {"priority": 4}, {"frequency": "monthly"}, {"duration_min": 0}, {"duration_min": -5}],
)
def test_invalid_task_values_are_rejected(overrides):
    values = {
        "description": "Walk",
        "pet_name": "Rex",
        "task_type": "walk",
        "scheduled_time": datetime(2026, 10, 31, 8, 0),
        "duration_min": 30,
    }
    values.update(overrides)

    with pytest.raises(ValueError):
        Task(**values)
