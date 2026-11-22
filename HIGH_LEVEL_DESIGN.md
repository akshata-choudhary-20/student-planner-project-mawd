# High-Level Design

## Student Academic Planner

The planner is a website where each student signs in to manage attendance, deadlines, and course grades. The dashboard brings these three features together on one page.

## How the system is organised

1. **Browser:** The student uses HTML forms to enter information. CSS arranges the dashboard into three cards. JavaScript previews how one more class would affect attendance.
2. **Python backend:** FastAPI receives form submissions, checks which student is signed in, and processes the request. Python calculates attendance advice and credit-weighted CGPA. Jinja2 puts the results into the HTML page.
3. **Database:** SQLite stores accounts, sessions, subjects, attendance, tasks, and grades in `planner.db`.

## How the parts work together

When a student marks a class present, the browser sends the selected subject, date, period, and status to FastAPI. The backend checks the login session and confirms that the subject belongs to that student. It then saves the entry in SQLite and redirects the browser to the dashboard. FastAPI loads the updated records, and the student sees the new attendance count.

## Student access

Each student uses the same dashboard layout but sees their own records. The backend identifies the student from their login session when loading or changing data.