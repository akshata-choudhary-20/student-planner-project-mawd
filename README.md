# Student Academic Planner

I built this website to keep track of attendance, assignment deadlines, and grades in one place. Each student has their own account and dashboard.

## Features

- **Attendance:** Add subjects, mark classes present or absent, and see how many classes you need to attend to reach 75%. To correct an entry, save the same subject, date, and period again.
- **Tasks:** Add a task with a due date, mark it as completed, or delete it.
- **Grades:** Enter credits and grade points for each course to calculate CGPA on a 10-point scale.

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