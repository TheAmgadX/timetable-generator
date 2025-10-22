import os
import sqlite3

db_path = os.path.abspath("timetable.db")
print("Creating database at:", db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Enable foreign key constraints
cur.execute("PRAGMA foreign_keys = ON;")

# Create tables
cur.executescript("""
CREATE TABLE IF NOT EXISTS Levels (
    id TEXT PRIMARY KEY,
    groups INTEGER,
    sections INTEGER,
    max_members_per_section INTEGER,
    students_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Courses (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    type TEXT CHECK(type IN ('Lecture', 'Lab', 'Tutorial', 'Graduation', 'Japanese')),
    time_slots INTEGER
);

CREATE TABLE IF NOT EXISTS CourseLevels (
    course_id TEXT,
    level_id TEXT,
    PRIMARY KEY (course_id, level_id),
    FOREIGN KEY (course_id) REFERENCES Courses(id) ON DELETE CASCADE,
    FOREIGN KEY (level_id) REFERENCES Levels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Instructors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT
);

CREATE TABLE IF NOT EXISTS InstructorCourses (
    instructor_id TEXT,
    course_id TEXT,
    PRIMARY KEY (instructor_id, course_id),
    FOREIGN KEY (instructor_id) REFERENCES Instructors(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Courses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Rooms (
    id TEXT PRIMARY KEY,
    type TEXT CHECK(type IN ('Lecture', 'Lab', 'Tutorial')),
    capacity INTEGER
);
""")

conn.commit()
conn.close()

print("Database tables created successfully.")
