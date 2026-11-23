# Student Academic Planner

I built this website to keep track of attendance, assignment deadlines, and grades in one place. Each student has their own account and dashboard.

https://student-planner-project-mawd-1.onrender.com/login

**Username:** `student 01`  
**Password on the deployed demo:** `PlannerDemo01!`

**Username:** `student 02`  
**Password on the deployed demo:** PlannerDemo02!
## Features

- **Attendance:** Add subjects, mark classes present or absent, and see how many classes you need to attend to reach 75%. To correct an entry, save the same subject, date, and period again.
- **Tasks:** Add a task with a due date, mark it as completed, or delete it.
- **Grades:** Enter credits and grade points for each course to calculate CGPA on a 10-point scale.

## Demo account

**Username:** `student 01`  
**Password on the deployed demo:** `PlannerDemo01!`

This shared account contains fictional student records. You can also register your own account to start with an empty dashboard.

![Student 01 dashboard](Dashboard-New.png)


### Attendance

- Mathematics: attended 0 of 1 class
- Physics: attended 2 of 2 classes
- Testing subject: attended 0 of 1 class

### Tasks

- Maths assignment: completed
- English assignment: pending

### Semester grades

- English: 8 grade points, 2 credits
- Mathematics: 9 grade points, 4 credits
- Physics: 6 grade points, 4 credits

**CGPA: 7.60 / 10**

## How to run it on Windows(Source)

Install Python, open the project folder in VS Code, and open a terminal. Run these commands one at a time:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open <http://127.0.0.1:8000/register> in a browser and create an account. The app creates its SQLite database the first time it starts. To stop the server, press **Ctrl + C** in the terminal.

## Technologies

Python, FastAPI, SQLite, HTML, CSS, Jinja2, and JavaScript.

## Project documents

- [Project selection](PROJECT_SELECTION.md)
- [High-level design](HIGH_LEVEL_DESIGN.md)
- [Low-level design](LOW_LEVEL_DESIGN.md)
