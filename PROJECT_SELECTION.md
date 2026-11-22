# Project Selection: Student Academic Planner

## Problem
A student who has attended 18 out of 25 classes has 72% attendance.
That percentage is easy to calculate, but it does not immediately tell
the student how many more classes they need to attend to reach 75%.
Students also have assignment deadlines and course grades to keep track of.

## Chosen project
I chose to build a personal academic planner where a student can log in
and manage their attendance, tasks, and grades in one place.

## Main features
- Record attendance by subject, date, and class period.
- Correct an attendance entry without counting the same class twice.
- See how many classes to attend or miss while meeting a 75% target.
- Add tasks with due dates, mark them done, and delete them.
- Enter course credits and grade points to calculate CGPA on a 10-point scale.

## Why I chose this project
The planner solves a problem I can demonstrate with a simple example.
At 18 out of 25 classes, attending the next three brings the total to
21 out of 28, which is exactly 75%. I can use examples like this to
check whether my backend gives the right answer.

## Technologies
The backend uses Python, FastAPI, and SQLite. The pages use HTML,
Jinja2 templates, and CSS. JavaScript previews how one more class
would affect attendance before the student saves it.