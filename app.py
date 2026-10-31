from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Streamlit reruns this whole file on every click, so the Owner (with its pets,
# scheduler, and tasks) lives in session_state and is only created once.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=120)

owner = st.session_state.owner

PRIORITIES = {"high": 1, "medium": 2, "low": 3}
PRIORITY_COLORS = {1: "🔴", 2: "🟡", 3: "🟢"}


def task_rows(tasks: list[Task]) -> list[dict]:
    """Turn tasks into table rows for display."""
    return [
        {
            "Priority": PRIORITY_COLORS[task.priority],
            "Time": f"{task.scheduled_time:%I:%M %p}",
            "Pet": task.pet_name,
            "Task": task.description,
            "Minutes": task.duration_min,
            "Repeats": task.frequency,
        }
        for task in tasks
    ]


st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = st.number_input(
        "Minutes available today", min_value=0, max_value=1440, value=owner.available_minutes
    )

st.subheader("Pets")
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
    st.write(", ".join(f"{pet.name} ({pet.species}, {pet.age})" for pet in pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
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

    if st.button("Add task"):
        pet = next(pet for pet in pets if pet.name == pet_choice)
        owner.scheduler.add_task(
            pet,
            Task(
                description=task_description,
                pet_name=pet.name,
                task_type=task_type,
                scheduled_time=datetime.combine(date.today(), task_time),
                duration_min=int(duration),
                frequency=frequency,
                priority=PRIORITIES[priority],
            ),
        )
        st.success(f"Added {task_description} for {pet.name}.")

todays_tasks = owner.view_todays_tasks()
if todays_tasks:
    st.write("Today's tasks:")
    st.table(task_rows(todays_tasks))
elif pets:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Picks the most important tasks that fit in your available minutes, then orders them by time.")

if st.button("Generate schedule"):
    plan = owner.get_daily_plan()
    if not plan.planned:
        st.warning("Nothing fits in today's plan. Add tasks or increase your available minutes.")
    else:
        count = len(plan.planned)
        st.success(f"{count} task{'s' if count != 1 else ''} planned, {plan.used} of {plan.available} minutes used.")
        st.table(task_rows(plan.planned))

    if plan.skipped:
        st.markdown("**Left out (not enough time):**")
        for task in plan.skipped:
            st.write(f"{PRIORITY_COLORS[task.priority]} {task.description} for {task.pet_name} ({task.duration_min} min)")
    st.caption("🔴 high   🟡 medium   🟢 low")
