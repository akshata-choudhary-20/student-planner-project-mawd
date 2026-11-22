import sqlite3
import hashlib
import secrets
import time
from datetime import date
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
def create_tables():
    db = sqlite3.connect("planner.db")
    db.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            student_id INTEGER NOT NULL,
            expires_at INTEGER NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            name TEXT NOT NULL COLLATE NOCASE,
            UNIQUE(student_id, name)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            subject_id INTEGER NOT NULL,
            class_date TEXT NOT NULL,
            period INTEGER NOT NULL,
            present INTEGER NOT NULL CHECK (present IN (0, 1)),
            PRIMARY KEY (subject_id, class_date, period)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            student_id INTEGER NOT NULL,
            semester INTEGER NOT NULL,
            course TEXT NOT NULL COLLATE NOCASE,
            credits INTEGER NOT NULL CHECK (credits > 0),
            grade_points REAL NOT NULL CHECK (grade_points BETWEEN 0 AND 10),
            PRIMARY KEY (student_id, semester, course)
        )
    """)
    db.commit()
    db.close()


create_tables()


@app.get("/register")
def show_register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={"title": "Register", "error": ""},
    )
@app.post("/register")
def register_student(request: Request, username: str = Form(), password: str = Form()):
    username = username.strip().lower()
    error = ""
    message = ""

    if len(username) < 3:
        error = "Choose a username with at least 3 characters."
    elif len(password) < 8:
        error = "Choose a password with at least 8 characters."
    else:
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), 600_000
        ).hex()

        db = sqlite3.connect("planner.db")
        try:
            db.execute(
                "INSERT INTO students (username, salt, password_hash) VALUES (?, ?, ?)",
                (username, salt, password_hash),
            )
            db.commit()
            message = "Account created!"
        except sqlite3.IntegrityError:
            error = "That username is already taken."
        finally:
            db.close()

    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={"title": "Register", "error": error, "message": message},
    )

@app.get("/login")
def show_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={"title": "Log in"},
    )
@app.post("/login")
def check_login(request: Request, username: str = Form(), password: str = Form()):
    username = username.strip().lower()

    db = sqlite3.connect("planner.db")
    db.row_factory = sqlite3.Row

    try:
        student = db.execute(
            "SELECT id, salt, password_hash FROM students WHERE username = ?",
            (username,),
        ).fetchone()
    finally:
        db.close()

    error = "Incorrect username or password."
    message = ""

    if student is not None:
        entered_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(student["salt"]), 600_000
        ).hex()

        if secrets.compare_digest(entered_hash, student["password_hash"]):
            token = secrets.token_urlsafe(32)
            one_day = 24 * 60 * 60

            db = sqlite3.connect("planner.db")
            try:
                db.execute(
                    "INSERT INTO sessions (token, student_id, expires_at) VALUES (?, ?, ?)",
                    (token, student["id"], int(time.time()) + one_day),
                )
                db.commit()
            finally:
                db.close()

            response = RedirectResponse("/dashboard", status_code=303)
            response.set_cookie(
                "session", token, max_age=one_day, httponly=True, samesite="strict"
            )
            return response

    
    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={"title": "Log in", "error": error, "message": message},
    )


def get_current_student(request: Request):
    token = request.cookies.get("session")

    db = sqlite3.connect("planner.db")
    db.row_factory = sqlite3.Row
    try:
        return db.execute("""
            SELECT students.id, students.username
            FROM sessions
            JOIN students ON students.id = sessions.student_id
            WHERE sessions.token = ? AND sessions.expires_at > ?
        """, (token, int(time.time()))).fetchone()
    finally:
        db.close()

def attendance_summary(attended, total):
    if total == 0:
        return "No classes recorded yet."

    percentage = attended * 100 / total

    balance = 4 * attended - 3 * total

    if balance < 0:
        advice = f"Classes to attend in a row to reach 75%: {-balance}"
    else:
        advice = f"Classes you can miss and stay at or above 75%: {balance // 3}"

    return f"{percentage:.1f}% attendance.\n {advice}."
def calculate_cgpa(grades):
    total_credits = 0
    total_points = 0

    for grade in grades:
        total_credits += grade["credits"]
        total_points += grade["credits"] * grade["grade_points"]

    if total_credits == 0:
        return None

    return round(total_points / total_credits, 2)

@app.get("/dashboard")
def show_dashboard(request: Request):
    student = get_current_student(request)
    if student is None:
        return RedirectResponse("/login", status_code=303)

    db = sqlite3.connect("planner.db")
    db.row_factory = sqlite3.Row
    try:
        subjects = db.execute(
                        """
            SELECT subjects.id, subjects.name,
                   COUNT(attendance.period) AS total,
                   COALESCE(SUM(attendance.present), 0) AS attended
            FROM subjects
            LEFT JOIN attendance ON attendance.subject_id = subjects.id
            WHERE subjects.student_id = ?
            GROUP BY subjects.id, subjects.name
            ORDER BY subjects.name
            """,
            (student["id"],),
        ).fetchall()
        tasks = db.execute(
            "SELECT id, title, due_date, done FROM tasks WHERE student_id = ? ORDER BY due_date, id",
            (student["id"],),
        ).fetchall()
        grades = db.execute("""
            SELECT semester, course, credits, grade_points
            FROM grades
            WHERE student_id = ?
            ORDER BY semester, course
        """, (student["id"],)).fetchall()
    finally:
        db.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
                context={
            "username": student["username"],
            "subjects": subjects,
                        "tasks": tasks,
                        "grades": grades,
                        "cgpa": calculate_cgpa(grades),
            "attendance_summary": attendance_summary,
        },
    )


@app.post("/subjects")
def add_subject(request: Request, name: str = Form(max_length=60)):
    student = get_current_student(request)
    if student is None:
        return RedirectResponse("/login", status_code=303)

    name = name.strip()
    if name:
        db = sqlite3.connect("planner.db")
        try:
            db.execute("""
                INSERT INTO subjects (student_id, name) VALUES (?, ?)
                ON CONFLICT(student_id, name) DO NOTHING
            """, (student["id"], name))
            db.commit()
        finally:
            db.close()

    return RedirectResponse("/dashboard", status_code=303)

@app.post("/tasks/{task_id}/delete")
def delete_task(request: Request, task_id: int):
    student = get_current_student(request)
    if student is None:
        return RedirectResponse("/login", status_code=303)

    db = sqlite3.connect("planner.db")
    try:
        db.execute(
            "DELETE FROM tasks WHERE id = ? AND student_id = ?",
            (task_id, student["id"]),
        )
        db.commit()
    finally:
        db.close()

    return RedirectResponse("/dashboard", status_code=303)

@app.post("/logout")
def logout(request: Request):
    token = request.cookies.get("session")

    db = sqlite3.connect("planner.db")
    try:
        db.execute("DELETE FROM sessions WHERE token = ?", (token,))
        db.commit()
    finally:
        db.close()

    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("session")
    return response

@app.post("/attendance")
def mark_attendance(
    request: Request,
    subject_id: int = Form(),
    class_date: date = Form(),
    period: int = Form(ge=1, le=12),
    present: int = Form(ge=0, le=1),
):
    student = get_current_student(request)
    if student is None:
        return RedirectResponse("/login", status_code=303)

    if class_date > date.today():
        raise HTTPException(400, "Choose today or an earlier date.")

    db = sqlite3.connect("planner.db")
    try:
        subject = db.execute(
            "SELECT id FROM subjects WHERE id = ? AND student_id = ?",
            (subject_id, student["id"]),
        ).fetchone()

        if subject is None:
            raise HTTPException(404, "Subject not found.")

        db.execute("""
            INSERT INTO attendance (subject_id, class_date, period, present)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(subject_id, class_date, period)
            DO UPDATE SET present = excluded.present
        """, (subject_id, class_date.isoformat(), period, present))
        db.commit()
    finally:
        db.close()

    return RedirectResponse("/dashboard", status_code=303)

@app.post("/tasks")
def add_task(request: Request, title: str = Form(max_length=100), due_date: date = Form()):
    student = get_current_student(request)
    if student is None:
        return RedirectResponse("/login", status_code=303)

    title = title.strip()
    if not title:
        raise HTTPException(400, "Enter a task name.")

    db = sqlite3.connect("planner.db")
    try:
        db.execute(
            "INSERT INTO tasks (student_id, title, due_date) VALUES (?, ?, ?)",
            (student["id"], title, due_date.isoformat()),
        )
        db.commit()
    finally:
        db.close()

    return RedirectResponse("/dashboard", status_code=303)


@app.post("/tasks/{task_id}/done")
def mark_task_done(request: Request, task_id: int):
    student = get_current_student(request)
    if student is None:
        return RedirectResponse("/login", status_code=303)

    db = sqlite3.connect("planner.db")
    try:
        db.execute(
            "UPDATE tasks SET done = 1 WHERE id = ? AND student_id = ?",
            (task_id, student["id"]),
        )
        db.commit()
    finally:
        db.close()

    return RedirectResponse("/dashboard", status_code=303)



@app.post("/grades")
def save_grade(
    request: Request,
    semester: int = Form(ge=1),
    course: str = Form(max_length=60),
    credits: int = Form(gt=0),
    grade_points: float = Form(ge=0, le=10),
):
    student = get_current_student(request)
    if student is None:
        return RedirectResponse("/login", status_code=303)

    course = course.strip()
    if not course:
        raise HTTPException(400, "Enter a course name.")

    db = sqlite3.connect("planner.db")
    try:
        db.execute("""
            INSERT INTO grades (student_id, semester, course, credits, grade_points)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id, semester, course)
            DO UPDATE SET credits = excluded.credits,
                          grade_points = excluded.grade_points
        """, (student["id"], semester, course, credits, grade_points))
        db.commit()
    finally:
        db.close()

    return RedirectResponse("/dashboard", status_code=303)

    