import sqlite3

class Instructor:
    def __init__(self, instructor_id: int, name: str, role: str, qualified_courses: set[str]):
        self.instructor_id = instructor_id
        self.name = name
        self.role = role
        self.qualified_courses = qualified_courses
        self.assigned_courses = set()
        

    # check if the instructor is qualified for the course.
    def is_qualified_for(self, course_code: str) -> bool:
        """Check if the instructor can teach a given course."""
        return course_code in self.qualified_courses

    def write_to_db(self, cur : sqlite3.Cursor):
        try:
            cur.execute("""
                INSERT INTO Instructors (id, name, role)
                        VALUES (?, ?, ?, ?);
                """, (self.instructor_id, self.name, self.role))

            for course_id in self.qualified_courses:
                cur.execute("""
                    INSERT INTO InstructorCourses (instructor_id, course_id)
                    VALUES(?, ?);
                    """, (self.instructor_id, course_id))

        except sqlite3.Error as e:
            print("Error: ", e)

    def update_db(self, cur: sqlite3.Cursor):
        try:
            cur.execute("""
                UPDATE Instructors
                SET name = ?, role = ?
                WHERE id = ?;
            """, (self.name, self.role, self.instructor_id))

            if self.qualified_courses:
                placeholders = ','.join('?' * len(self.qualified_courses))
                cur.execute(f"""
                    DELETE FROM InstructorCourses
                    WHERE instructor_id = ?
                    AND course_id NOT IN ({placeholders});
                """, (self.instructor_id, *self.qualified_courses))
            else:
                cur.execute("""
                    DELETE FROM InstructorCourses
                    WHERE instructor_id = ?;
                """, (self.instructor_id,))

            for course_id in self.qualified_courses:
                cur.execute("""
                    INSERT OR IGNORE INTO InstructorCourses (instructor_id, course_id)
                    VALUES (?, ?);
                """, (self.instructor_id, course_id))

        except sqlite3.Error as e:
            print("Error (update_db):", e)

    def delete_db(self, cur: sqlite3.Cursor):
        try:
            cur.execute("""
                DELETE FROM Instructors WHERE id = ?;
            """, (self.instructor_id,))

            # NOTE: the InstructorCourses will be deleted due to the ON DELETE CASCADE in the schema. 
            # but I added this for safety.
            cur.execute("""
                DELETE FROM InstructorCourses WHERE instructor_id = ?;
            """, (self.instructor_id,))

        except sqlite3.Error as e:
            print("Error (delete_db):", e)

    @classmethod
    def load_db(cls, cur: sqlite3.Cursor):
        query = """
            SELECT 
                i.id AS instructor_id,
                i.name AS instructor_name,
                i.role AS instructor_role,
                ic.course_id AS course_id
            FROM Instructors i
            INNER JOIN InstructorCourses ic ON i.id = ic.instructor_id
            ORDER BY i.id;
        """
        try:
            cur.execute(query)
            rows = cur.fetchall()

            instructors = {}
            
            for instructor_id, name, role, course_id in rows:
                if instructor_id not in instructors:
                    instructors[instructor_id] = Instructor(
                        instructor_id=instructor_id,
                        name=name,
                        role=role,
                        qualified_courses=set()
                    )
                instructors[instructor_id].qualified_courses.add(str(course_id))

            return list(instructors.values())

        except sqlite3.Error as e:
            print("Error (load_db):", e)
            return []

    def __build_data_representation(self, instructor : "Instructor"):
        pass

    @classmethod
    def build_data_representation(cls, instructors : list["Instructor"]):
        pass

    @classmethod
    def map_instructors_to_courses(cls, instructors : list["Instructor"]):
        """
            - each course has instructors who can teach this course.
            - each instructor has courses he can teach

            - Data Representation: 
                map[course-code] : CourseObj
                map[instructor-code] : InstructorObj

                CourseObj -> has set of instructors can teach it and has attr for the isntructor actually teach it.
                InstructorObj -> has set of courses he can teach teaches, and a set of courses he actually teach.  


            Algorithm: 
                iterate over courses: 
                    for each course see the available instructors
                        see the least instructor has courses assigned to him
                            assign the course for this instructor
                
        """