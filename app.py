from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption(
    "A pet care planner: add your pets and their care tasks, and PawPal+ sorts them, "
    "flags scheduling conflicts, repeats daily and weekly tasks, and builds a plan that "
    "fits the time you have today."
)

st.divider()

# Streamlit reruns this whole file on every click, so the Owner (with its pets,
# scheduler, and tasks) lives in session_state and is only created once.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=120)

owner = st.session_state.owner

PRIORITIES = {"high": 1, "medium": 2, "low": 3}
PRIORITY_LABELS = {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}


def task_label(task: Task) -> str:
    """Describe a task in one line for a dropdown."""
    return f"{task.scheduled_time:%a %I:%M %p} · {task.pet_name} · {task.description}"


def task_rows(tasks: list[Task], show_day: bool = True) -> list[dict]:
    """Turn tasks into table rows for display."""
    rows = []
    for task in tasks:
        row = {"Status": "✅ Done" if task.completed else "⬜ To do"}
        if show_day:
            row["Day"] = f"{task.scheduled_time:%a %b %d}"
        row.update(
            {
                "Time": f"{task.scheduled_time:%I:%M %p}",
                "Pet": task.pet_name,
                "Task": task.description,
                "Type": task.task_type.title(),
                "Priority": PRIORITY_LABELS[task.priority],
                "Minutes": task.duration_min,
                "Repeats": task.frequency.title(),
            }
        )
        rows.append(row)
    return rows


def show_conflicts() -> None:
    """Show today's scheduling conflicts in one warning box, or a success note if there are none."""
    warnings = owner.scheduler.conflict_warnings()
    if warnings:
        count = len(warnings)
        st.warning(
            f"**{count} scheduling conflict{'s' if count != 1 else ''} today**\n\n"
            + "\n".join(f"- {warning}" for warning in warnings),
            icon="⚠️",
        )
    else:
        st.success("No scheduling conflicts today.", icon="✅")


# ---------------------------------------------------------------- Owner

st.subheader("👤 Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = st.number_input(
        "Minutes available today", min_value=0, max_value=1440, value=owner.available_minutes
    )

# ---------------------------------------------------------------- Pets

st.subheader("🐶 Pets")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=40, value=2)

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Please enter a pet name.")
    elif any(pet.name == pet_name for pet in owner.get_pets()):
        st.error(f"{pet_name} is already added.")
    else:
        owner.add_pet(Pet(pet_name, species, int(age)))
        st.success(f"Added {pet_name}.")

pets = owner.get_pets()
if pets:
    st.table(
        [
            {
                "Pet": pet.name,
                "Species": pet.species.title(),
                "Age": pet.age,
                "Tasks to do": len(owner.scheduler.filter_tasks(pet_name=pet.name, completed=False)),
            }
            for pet in pets
        ],
        hide_index=True,
    )
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------- Tasks

st.subheader("📋 Tasks")
if not pets:
    st.caption("Add a pet first, then you can give it tasks.")
else:
    col1, col2 = st.columns(2)
    with col1:
        pet_choice = st.selectbox("For pet", [pet.name for pet in pets])
        task_description = st.text_input("Task", value="Morning walk")
        task_type = st.selectbox("Type", ["walk", "feeding", "medication", "grooming", "other"])
    with col2:
        task_time = st.time_input("Time", value=time(8, 0))
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", list(PRIORITIES), index=0)
    frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
    auto_shift = st.checkbox("If that time is already taken, move it to the next free slot")

    if st.button("Add task", type="primary"):
        pet = next(pet for pet in pets if pet.name == pet_choice)
        task = Task(
            description=task_description,
            pet_name=pet.name,
            task_type=task_type,
            scheduled_time=datetime.combine(date.today(), task_time),
            duration_min=int(duration),
            frequency=frequency,
            priority=PRIORITIES[priority],
        )
        requested = task.scheduled_time
        if auto_shift:
            task.scheduled_time = owner.scheduler.next_free_slot(task.duration_min, requested)

        # A clash doesn't block the task; the scheduler returns a warning instead of crashing.
        warning = owner.scheduler.add_task_with_warning(pet, task)
        if task not in pet.tasks:
            st.error(warning)
        elif warning:
            st.warning(
                f"Added **{task.description}** for {pet.name}, but it clashes with another task. "
                "See the conflicts below.",
                icon="⚠️",
            )
        else:
            st.success(f"Added **{task.description}** for {pet.name}.", icon="✅")
        if task.scheduled_time != requested:
            st.info(
                f"{requested:%I:%M %p} was taken, so **{task.description}** "
                f"was moved to {task.scheduled_time:%I:%M %p}.",
                icon="🕒",
            )

# Set by "Mark done" just before the page reruns, so the message survives the rerun.
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"), icon="✅")

pending = owner.scheduler.filter_tasks(completed=False)
if pending:
    st.markdown("#### Mark a task done")
    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    with col1:
        # Choose by position: Streamlit hands back copies of option objects, and
        # complete_task needs the original task to find its pet.
        choice = st.selectbox(
            "Task to mark done", range(len(pending)), format_func=lambda i: task_label(pending[i])
        )
        to_complete = pending[choice]
    with col2:
        if st.button("Mark done"):
            next_task = owner.scheduler.complete_task(to_complete)
            message = f"Marked **{to_complete.description}** for {to_complete.pet_name} done."
            if next_task:
                message += f" Next one is {next_task.scheduled_time:%a %b %d at %I:%M %p}."
            st.session_state.flash = message
            st.rerun()

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.markdown("#### Task list")

    done_count = len(owner.scheduler.filter_tasks(completed=True))
    col1, col2, col3 = st.columns(3)
    col1.metric("All tasks", len(all_tasks), border=True)
    col2.metric("To do", len(all_tasks) - done_count, border=True)
    col3.metric("Done", done_count, border=True)

    show_conflicts()

    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [pet.name for pet in pets])
    with col2:
        status_filter = st.selectbox("Show status", ["All", "To do", "Done"])

    shown = owner.scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "To do": False, "Done": True}[status_filter],
    )
    if shown:
        st.table(task_rows(shown), hide_index=True)
        st.caption(
            f"Showing {len(shown)} of {len(all_tasks)} tasks, sorted by time "
            "(higher priority first when two tasks start together)."
        )
    else:
        st.info("No tasks match these filters.")
elif pets:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------- Schedule

st.subheader("🗓️ Today's Schedule")
st.caption("Picks the most important tasks that fit in your available minutes, then orders them by time.")

if st.button("Generate schedule", type="primary"):
    plan = owner.get_daily_plan()

    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks planned", len(plan.planned), border=True)
    col2.metric("Minutes used", f"{plan.used} / {plan.available}", border=True)
    col3.metric("Minutes left", plan.remaining, border=True)
    if plan.available:
        st.progress(min(plan.used / plan.available, 1.0), text="Time budget used")

    if not plan.planned:
        st.warning("Nothing fits in today's plan. Add tasks or increase your available minutes.", icon="⚠️")
    else:
        count = len(plan.planned)
        st.success(
            f"{count} task{'s' if count != 1 else ''} planned for {owner.name} today, "
            f"in time order.",
            icon="✅",
        )
        st.table(task_rows(plan.planned, show_day=False), hide_index=True)

    if plan.skipped:
        count = len(plan.skipped)
        st.warning(
            f"{count} task{'s' if count != 1 else ''} left out because there wasn't enough time. "
            "Lower-priority tasks are dropped first.",
            icon="⏳",
        )
        st.table(task_rows(plan.skipped, show_day=False), hide_index=True)

    show_conflicts()
