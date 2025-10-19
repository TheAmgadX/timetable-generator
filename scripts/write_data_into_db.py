import sqlite3
from scripts.read_data_from_csv import load_data

def write_to_db():
    conn = sqlite3.connect("timetable.db")
    cur = conn.cursor()    

    courses, instructors, rooms  = load_data()

    for course in courses:
        course.write_to_db(cur)

    for instructor in instructors:
        instructor.write_to_db(cur)
    
    for room in rooms:
        room.write_to_db(cur)

    conn.commit()
    conn.close()
    print("all data written to db successfully.")


if __name__ == "__main__":
    write_to_db()