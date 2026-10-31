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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
