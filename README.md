# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

The end of `python main.py` shows the plan that fits in the owner's 90 minutes, the tasks that were left out, and any scheduling conflicts:

```
🐾 Today's Plan for Jenney (Saturday, October 31)
----------------------------------------------------
[ ] 🟡 08:00 AM  Rex    Walk Rex              30 min
[ ] 🔴 08:15 AM  Rex    Heartworm pill         5 min
[ ] 🟢 03:00 PM  Rex    Ear cleaning          10 min
[ ] 🔴 05:00 PM  Mia    Dinner                10 min
[ ] 🔴 05:00 PM  Mia    Evening meds           5 min
[ ] 🟡 06:00 PM  Rex    Walk Rex              30 min
----------------------------------------------------
6 tasks, 90 of 90 minutes used, 0 left

Left out (not enough time):
[ ] 🟢 03:00 PM  Mia    Brush fur             15 min
[ ] 🟢 06:30 PM  Rex    Play fetch            20 min

⚠️  Scheduling conflicts:
    Same pet (Rex): 'Heartworm pill' at 08:15 AM starts before 'Walk Rex' ends at 08:30 AM
    Different pets (Rex & Mia): 'Ear cleaning' and 'Brush fur' both start at 03:00 PM
    Same pet (Mia): 'Dinner' and 'Evening meds' both start at 05:00 PM

🔴 high   🟡 medium   🟢 low
```

Earlier in the same run, it also prints the warnings as the clashing tasks are added, the next occurrence of a completed daily task, the full task list sorted by time, and filtered lists (Rex's unfinished tasks and all completed tasks).

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python3 -m pytest

Covers task completion, sorting, filtering, conflict detection, recurring tasks, and daily planning.

My Confidence Level in the systems reliability based on my test results: 🌟🌟🌟🌟🌟

```

Sample test output:

```
test_pawpal.py .............................................             [100%]

============================== 45 passed in 0.05s ==============================
```

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting | `Scheduler.sort_by_time()`, `time_key()` | Combines every pet's tasks into one list sorted by `(scheduled_time, priority)`: earliest first, and the higher-priority task first when two start at the same time. Sorts fresh on each call, so it stays correct even if a task's time is changed later. |
| Filtering| `Scheduler.filter_tasks()`, `Scheduler.get_todays_tasks()`| `filter_tasks(pet_name=, completed=, task_type=)` returns tasks in time order that match every filter given; filters left out are ignored, so `filter_tasks(pet_name="Rex", completed=False)` gives Rex's unfinished tasks. `get_todays_tasks()` keeps only tasks due today.|
| Conflict Handling| `Task.overlaps()`, `Scheduler.find_conflicts()`, `Scheduler.conflict_warnings()`, `Scheduler.add_task_with_warning()`| Two tasks conflict when each starts before the other ends (back-to-back tasks do not). `find_conflicts()` checks every pair of today's unfinished tasks for the same pet or different pets. `conflict_warnings()` turns each clash into a message like `Same pet (Mia): 'Dinner' and 'Evening meds' both start at 05:00 PM`. `add_task_with_warning()` checks only the new task and returns a warning instead of crashing; the task is still added.|
| Recurring tasks| `Scheduler.complete_task()`, `Task.mark_complete()`| Completing a task marks it done and, using `timedelta`, creates the next occurrence for the same pet: `"daily"` is today + 1 day, `"weekly"` is today + 7 days, at the same time of day; `"once"` does not repeat. A task completed early repeats from its own date, so no duplicate is made.|

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
