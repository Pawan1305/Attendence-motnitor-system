import sqlite3
import os
from flask import g

DATABASE = os.path.join(os.path.dirname(__file__), 'attendance.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    if True:  # always run CREATE IF NOT EXISTS so it works on fresh deployments
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS students (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT NOT NULL,
                roll_no  TEXT NOT NULL UNIQUE,
                branch   TEXT,
                semester TEXT
            );

            CREATE TABLE IF NOT EXISTS subjects (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS attendance (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL REFERENCES students(id),
                subject_id INTEGER NOT NULL REFERENCES subjects(id),
                date       TEXT    NOT NULL,
                status     TEXT    NOT NULL CHECK(status IN ('Present','Absent'))
            );

            -- Seed subjects
            INSERT OR IGNORE INTO subjects (name, code) VALUES
                ('Mathematics',        'MATH101'),
                ('Physics',            'PHY101'),
                ('Computer Science',   'CS101'),
                ('English',            'ENG101'),
                ('Chemistry',          'CHEM101');

            -- Seed students
            INSERT OR IGNORE INTO students (name, roll_no, branch, semester) VALUES
                ('Aarav Sharma',   'CS001', 'Computer Science', '3rd'),
                ('Priya Patel',    'CS002', 'Computer Science', '3rd'),
                ('Rohan Mehta',    'CS003', 'Computer Science', '3rd'),
                ('Sneha Gupta',    'CS004', 'Computer Science', '3rd'),
                ('Arjun Singh',    'CS005', 'Computer Science', '3rd');
        ''')
        conn.commit()
        conn.close()
