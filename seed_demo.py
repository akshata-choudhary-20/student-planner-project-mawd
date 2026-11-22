import hashlib
import secrets
import sqlite3
from contextlib import closing

from main import create_tables


def add_account(db, username, password):
    if db.execute("SELECT id FROM students WHERE username = ?", (username,)).fetchone():
        print(username + " already exists. Its password and records have been preserved.")
        return None
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 600_000
    ).hex()
    return db.execute(
        "INSERT INTO students (username, salt, password_hash) VALUES (?, ?, ?)",
        (username, salt, password_hash),
    ).lastrowid


def seed_demo():
    create_tables()
    with closing(sqlite3.connect("planner.db")) as db, db:
        db.execute("BEGIN IMMEDIATE")

        if add_account(db, "student 02", "PlannerDemo02!"):
            print("student 02 created.")

        student = add_account(db, "student 01", "PlannerDemo01!")
        if student is None:
            return

        attendance = {
            "Mathematics": [("2026-11-22", 1, 0)],
            "physics": [("2026-11-21", 1, 1), ("2026-11-22", 2, 1)],
            "testing subject": [("2026-11-22", 1, 0)],
        }
        for name, classes in attendance.items():
            subject = db.execute(
                "INSERT INTO subjects (student_id, name) VALUES (?, ?)", (student, name)
            ).lastrowid
            for day, period, present in classes:
                db.execute(
                    "INSERT INTO attendance (subject_id, class_date, period, present) VALUES (?, ?, ?, ?)",
                    (subject, day, period, present),
                )

        db.executemany(
            "INSERT INTO tasks (student_id, title, due_date, done) VALUES (?, ?, ?, ?)",
            [
                (student, "finish maths assignment", "2026-12-01", 1),
                (student, "finish  english assignment", "2026-11-20", 0),
            ],
        )
        db.executemany(
            "INSERT INTO grades (student_id, semester, course, credits, grade_points) VALUES (?, ?, ?, ?, ?)",
            [(student, 1, "english", 2, 8), (student, 1, "mathematics", 4, 9),
             (student, 1, "physics", 4, 6)],
        )
    print("Demo account created.")


if __name__ == "__main__":
    seed_demo()