import sqlite3
import os

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cohort TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    credits INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    grade TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
);
"""

SEED_SQL = """
INSERT INTO students (name, cohort) VALUES 
('Alice Smith', 'A1'),
('Bob Jones', 'A1'),
('Charlie Brown', 'B2');

INSERT INTO courses (title, credits) VALUES 
('Introduction to Computer Science', 3),
('Calculus I', 4),
('Physics 101', 4);

INSERT INTO enrollments (student_id, course_id, grade) VALUES 
(1, 1, 'A'),
(1, 2, 'B'),
(2, 1, 'A'),
(3, 3, 'B');
"""

def create_database(db_path="app.db"):
    """
    1. Open SQLite database file.
    2. Execute schema SQL.
    3. Execute seed SQL.
    4. Commit.
    5. Return database path.
    """
    # If it already exists, remove it to start fresh for this script
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.executescript(SCHEMA_SQL)
    cursor.executescript(SEED_SQL)
    
    conn.commit()
    conn.close()
    
    return db_path

if __name__ == "__main__":
    db_path = create_database()
    print(f"Database initialized at {db_path}")
