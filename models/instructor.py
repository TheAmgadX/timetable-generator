import sqlite3

class Instructor:
    def __init__(self, instructor_id: int, name: str, role: str,
                 not_preferred_slot: str, qualified_courses: list[str]):
        self.instructor_id = instructor_id
        self.name = name
        self.role = role
        self.not_preferred_slot = not_preferred_slot
        self.qualified_courses = qualified_courses

    # check if the instructor is qualified for the course.
    def is_qualified_for(self, course_code: str) -> bool:
        """Check if the instructor can teach a given course."""
        return course_code in self.qualified_courses

    
    # build the representation of the data in the program.
    def build_structure(self):
        pass

    def write_to_db(self, cur : sqlite3.Cursor):
        try:
            cur.execute("""
                INSERT INTO Instructors (id, name, role, notPreferredDay)
                        VALUES (?, ?, ?, ?);
                """, (self.instructor_id, self.name, self.role, self.not_preferred_slot))

            for course_id in self.qualified_courses:
                cur.execute("""
                    INSERT INTO InstructorCourses (instructor_id, course_id)
                    VALUES(?, ?);
                    """, (self.instructor_id, course_id))

        except sqlite3.Error as e:
            print("Error: ", e)
