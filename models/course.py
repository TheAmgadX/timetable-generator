import sqlite3

class Course:
    def __init__(self, code: str, name: str, type: str, time_slots: int, course_levels: str):
        self.code = code
        self.name = name
        self.type = type
        self.time_slots = time_slots
        self.course_levels = course_levels

    def build_structure(self):
        pass

    def write_to_db(self, cur : sqlite3.Cursor):
        try:
            cur.execute("""
                INSERT INTO Courses (id, title, type, time_slots)
                        VALUES (?, ?, ?, ?);
                """, (self.code, self.name, self.type, self.time_slots))
            
            for level_id in self.course_levels:
                cur.execute("""
                    INSERT INTO CourseLevels (course_id, level_id)
                            VALUES (?, ?);
                    """, (self.code, level_id))

        except sqlite3.Error as e:
            print("Error: ", e)
