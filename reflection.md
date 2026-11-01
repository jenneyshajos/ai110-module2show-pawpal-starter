# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

My initial UML design is built around three actions: adding a pet, scheduling a walk, and seeing today's tasks. The Owner is the starting point because the owner needs access to all of this information. The Owner owns many pets, each Pet has many tasks, and the Owner uses one Scheduler to manage the tasks. A walk is just a Task with its type set to "walk," which keeps the design simple.

- What classes did you include, and what responsibilities did you assign to each?

I included four classes: Owner, Pet, Task, and Scheduler. The Owner adds pets, schedules walks, and views today's tasks by passing those requests to the Scheduler. The Pet stores its name, species, age, and its own list of tasks. The Task represents one care activity and can mark itself complete and check if it is due today. The Scheduler holds all the tasks and is responsible for adding them, finding today's tasks, and sorting them by time.


**b. Design changes**

- Did your design change during implementation?

Yes, my design changed after I reviewed the UML against my class skeleton. I found that a task did not know which pet it belonged to, and the scheduler could not build a daily plan based on limits.

- If yes, describe at least one change and why you made it.

The first change was adding a pet_name attribute to the Task class. Before this, a Pet could see its tasks, but a Task could not point back to its pet, so today's task list could show "Walk at 8:00" without saying whose walk it was. The second change was adding a time budget for the day. I gave the Owner an available_minutes attribute, changed priority from text to a number (1 is high and 3 is low), and added a build_daily_plan method to the Scheduler. This lets the scheduler choose the most important tasks that fit in the owner's day, which the app needs in order to build a real plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**
- What constraints does your scheduler consider (for example: time, priority, preferences)?

My scheduler considers the owner's available minutes for the day, each task's priority, and each task's scheduled time and duration. It also only plans tasks that are due today and not already completed, and it checks for tasks whose times overlap.

- How did you decide which constraints mattered most?

I decided priority mattered most because missing a walk or medication is worse than missing grooming. The time budget came next, since the owner cannot do more than the time they have. Overlapping times only give a warning instead of blocking the task, because the owner knows best how to fix their own schedule.

**b. Tradeoffs**
- Describe one tradeoff your scheduler makes.

My scheduler picks tasks by priority first instead of trying to fill every available minute. For example, with 30 minutes, it will choose a high priority 20 minute walk over two low priority 15 minute tasks, even though the two smaller tasks would fill all 30 minutes.

- Why is that tradeoff reasonable for this scenario?

This is reasonable because a missed walk or missed medication is a bigger problem than a few unused minutes. It also keeps the plan easy to understand, and the scheduler lists any tasks it left out so the owner can decide what to do with them.

---

## 3. AI Collaboration

**a. How you used AI**
- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used AI for design brainstorming, debugging, and refactoring. I first asked it what parts of my scheduling logic felt too manual or simple, then had it build features like sorting, filtering, conflict warnings, and recurring tasks. Later I asked it how to make my code simpler and more readable.

- What kinds of prompts or questions were most helpful?

The most helpful prompts were specific ones that named a method or rule, such as asking that a daily task's next date be today + 1 day using timedelta. Asking it to "make sure" a feature or step was done was also helpful, because it checked the code and found gaps, like a missing test for a pet with no tasks.

**b. Judgment and verification**
- Describe one moment where you did not accept an AI suggestion as-is.

When I asked how to simplify my code, the AI gave me six suggestions. I only accepted the first four, which simplified sorting, the daily plan, and conflict detection, and left the rest out.

- How did you evaluate or verify what the AI suggested?

I verified each change by running python -m pytest and checking that all tests passed, and by running main.py to see the output myself. After the simplification, one test failed, which showed that the change had caused a real bug, so it had to be fixed before I kept it.


---

## 4. Testing and Verification

**a. What you tested**
- What behaviors did you test?

I tested sorting by time, filtering by pet and status, conflict detection for the same pet and different pets, daily and weekly recurring tasks, the daily plan staying within the time budget, and edge cases like a pet with no tasks, back-to-back tasks, and invalid input.

- Why were these tests important?

These tests were important because they check that the owner sees tasks in the right order, is warned about clashes, and never loses a repeating task like medication. They also caught a real bug when I changed my sorting code.


**b. Confidence**
- How confident are you that your scheduler works correctly?
I am very confident that my scheduler works correctly because all 45 of my tests pass. 🌟🌟🌟🌟🌟

- What edge cases would you test next if you had more time?

I would test tasks that run past midnight into the next day, an owner with 0 available minutes, two pets with the same name, and completing a task that does not belong to any pet.


---

## 5. Reflection

**a. What went well**
- What part of this project are you most satisfied with?

I am most satisfied with the code and how clean it looks. 

**b. What you would improve**
- If you had another iteration, what would you improve or redesign?
In another iteration, I would add the ability to edit and delete tasks in the app.


**c. Key takeaway**
- What is one important thing you learned about designing systems or working with AI on this project?

Something important I learned is to be very direct with what your expectations are and what you want to see from the AI, as many times it will do/add things that are completely unnecessary and can very quickly make code or a diagram busy and hard to understand/read. 
