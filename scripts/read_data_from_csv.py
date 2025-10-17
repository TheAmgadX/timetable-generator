import csv
import glob
from models.models import *

courses = []
instructors = []
rooms = []


def load_data():
    # -------- Load Courses --------
    course_files = [
        "../level_1_courses.csv",
        "../level_2_courses.csv",
        "../level_3_cs_courses.csv",
        "../level_3_ai_courses.csv",
        "../level_3_cyber_courses.csv",
        "../level_3_bio_courses.csv",
        "../level_4_cs_courses.csv",
        "../level_4_ai_courses.csv",
        "../level_4_cyber_courses.csv",
        "../level_4_bio_courses.csv",
    ]

    total_courses = 0
    for file_path in course_files:
        try:
            with open(file_path, newline='') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # skip header line

                for row in reader:
                    # Expected: CourseID, CourseName, Type, Capacity_Per_Section
                    # We ignore Capacity_Per_Section.
                    if len(row) < 3:
                        continue

                    course_id = row[0].strip()
                    name = row[1].strip()
                    type_ = row[2].strip()
                    time_slots = row[3]
                    course = Course(course_id, name, type_, time_slots)
                    courses.append(course)
                    total_courses += 1

            print(f"Loaded {file_path} ({total_courses} total courses so far)")

        except FileNotFoundError:
            print(f"File not found: {file_path}")

    print(f"Total courses loaded: {total_courses}")

    # -------- Load Instructors --------
    try:
        with open("../Instructors.csv", newline='') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # skip header

            line_count = 0
            for row in reader:
                # Format: InstructorID,Name,Role,NotPreferredSlots,QualifiedCourses
                if len(row) < 4:
                    continue

                instructor_id = row[0].strip()
                name = row[1].strip()
                role = row[2].strip()
                not_pref = None
                # Format => Not on X where X is a day.
                if len(row) > 3 and row[3]:
                    text = row[3].strip()
                    if text.lower().startswith("not on"):
                        parts = text.split()
                        if len(parts) >= 3:
                            not_pref = parts[-1].lower()

                qualified_courses = [r.strip() for r in row[4:] if r.strip()]
                instructor = Instructor(instructor_id, name, role, not_pref, qualified_courses)
                instructors.append(instructor)
                line_count += 1

        print(f"Total instructors loaded: {line_count}")

    except FileNotFoundError:
        print("File not found: ../Instructors.csv")

    # -------- Load Rooms --------
    try:
        with open("../Rooms.csv", newline='') as f:
            reader = csv.reader(f)
            header = next(reader, None)

            line_count = 0
            for row in reader:
                # Format: RoomID,Type,Capacity
                if len(row) < 3:
                    continue

                room = Room(row[0].strip(), row[1].strip(), int(row[2]))
                rooms.append(room)
                line_count += 1

        print(f"Total rooms loaded: {line_count}")

    except FileNotFoundError:
        print("File not found: ../Rooms.csv")
