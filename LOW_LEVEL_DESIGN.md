# Student Academic Planner

## Low-Level Design

### 1. Project files

- `main.py` handles form submissions, reads and saves data, and calculates attendance and CGPA.
- `templates/account.html` contains the form used for registration and login.
- `templates/dashboard.html` displays the logged-in student’s attendance, tasks, and grades.
- `static/style.css` controls the appearance of the forms, buttons, and dashboard cards.
- `static/script.js` shows how attending or missing one more class would affect attendance.
- `planner.db` is the SQLite database that stores accounts and academic records.

### 2. Database tables

**Students**

The `students` table contains `id`, `username`, `salt`, and `password_hash`. Each username is unique. During registration, the application generates a salt and hashes the password. During login, it uses the saved salt to check the password entered by the student.

**Sessions**

The `sessions` table contains `token`, `student_id`, and `expires_at`. After login, the browser receives a token. The application uses that token to identify the student when they open the dashboard or submit a form.

**Subjects**

The `subjects` table contains `id`, `student_id`, and `name`. Each student has their own subject list. Two students can both add Mathematics, but each student can add it only once.

**Attendance**

The `attendance` table contains `subject_id`, `class_date`, `period`, and `present`. The subject, date, and period together identify one class. A value of `1` means present and `0` means absent. Saving the same class again updates its status.

**Tasks**

The `tasks` table contains `id`, `student_id`, `title`, `due_date`, and `done`. A new task starts with `done = 0`. Marking it complete changes the value to `1`.

**Grades**

The `grades` table contains `student_id`, `semester`, `course`, `credits`, and `grade_points`. Saving a grade for the same student, semester, and course updates the existing entry.

### 3. Main routes

**Account and dashboard**

- `POST /register` checks the registration details and saves the student account.
- `POST /login` checks the password, creates a session, and opens the dashboard.
- `GET /dashboard` checks the session and loads that student’s records.
- `POST /logout` deletes the session and clears the session cookie.

**Subjects and attendance**

- `POST /subjects` adds a subject to the student’s list.
- `POST /attendance` checks that the subject belongs to the student, then saves or corrects the attendance entry.

**Tasks and grades**

- `POST /tasks` saves a task and its due date.
- `POST /tasks/{task_id}/done` marks the student’s task as complete.
- `POST /tasks/{task_id}/delete` removes the student’s task.
- `POST /grades` adds a course grade or updates a previous entry.

### 4. Example of an attendance correction

Suppose I marked Mathematics, period 2, as absent by mistake.

1. I select Mathematics, the same date, and period 2. I change the status to Present and click **Save attendance**.
2. Python checks my session and confirms that the subject belongs to my account.
3. SQLite finds the existing class entry and changes `present` from `0` to `1`.
4. When the dashboard reloads, my attended count increases by one. The total number of classes stays the same.

### 5. Attendance calculation

Attendance percentage is calculated as `100 × attended / total`. When no classes have been recorded, the dashboard displays “No classes recorded yet.”

To work out how many classes a student can miss or needs to attend, the backend calculates `balance = 4 × attended − 3 × total`.

- If the balance is negative, its absolute value gives the number of consecutive classes the student needs to attend to reach 75%.
- If the balance is zero or positive, `balance // 3` gives the number of classes the student can miss while staying at or above 75%.

For example, attending 18 out of 25 classes gives a balance of −3. Attending the next three brings the total to 21 out of 28, which is exactly 75%.

### 6. CGPA calculation

The planner uses a 10-point grading scale. It multiplies each course’s credits by its grade points, adds the results, and divides by the total credits.

For example, a 4-credit course with 9 grade points contributes 36 points. A 2-credit course with 8 grade points contributes 12 points.A 4- credit course with 6 grade points will contribute 24 points. Together, the courses give a CGPA of `(36 + 16+ 24) / 10 = 7.60`.