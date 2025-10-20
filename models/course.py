import sqlite3

class Course:
    def __init__(self, code: str, name: str, type: str, time_slots: int, course_levels : list[str]):
        self.code = code
        self.name = name
        self.type = type
        self.time_slots = time_slots
        self.course_levels = course_levels

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

    def update_db(self, cur : sqlite3.Cursor):
        try:
            cur.execute("""
                UPDATE Courses SET title = ?, type = ?, time_slots = ? WHERE id = ?;
                """, (self.name, self.type, self.time_slots, self.code))
            
            # delete old connections 
            if self.course_levels:
                placeholders = ','.join('?' * len(self.course_levels))
                cur.execute(f"""
                    DELETE FROM CourseLevels 
                            WHERE course_id = ? 
                            and level_id not in({placeholders});
                    """, (self.code, *self.course_levels))
            else:
                cur.execute("""
                DELETE FROM CourseLevels 
                        WHERE course_id = ?;
                """, (self.code))

            for level_id in self.course_levels:
                cur.execute("""
                    INSERT OR IGNORE INTO CourseLevels (course_id, level_id)
                            VALUES (?, ?);
                    """, (self.code, level_id))

        except sqlite3.Error as e:
            print("Error: ", e)

    def delete_db(self, cur : sqlite3.Cursor):
        try:
            cur.execute("""
                DELETE FROM Courses WHERE id = ?;
                """, (self.code,))

        # NOTE: the levels will be deleted due to the ON DELETE CASCADE in the schema. 
        # but I added it for safety.
            cur.execute("""
                DELETE FROM CourseLevels WHERE course_id = ?;
                """, (self.code,))

        except sqlite3.Error as e:
            print("Error: ", e)

    @classmethod
    def load_db(cls, cur: sqlite3.Cursor):
        query = """
            SELECT 
                c.id AS course_id,
                c.title AS course_name,
                c.type AS course_type,
                c.time_slots AS course_slots,
                cl.level_id AS level_id
            FROM Courses c
            INNER JOIN CourseLevels cl ON c.id = cl.course_id
            ORDER BY c.id;
        """
        try:
            cur.execute(query)
            rows = cur.fetchall()

            courses = {}
            for course_id, name, type_, slots, level_id in rows:
                if course_id not in courses:
                    courses[course_id] = Course(
                        code=course_id,
                        name=name,
                        type=type_,
                        time_slots=slots,
                        course_levels=[]
                    )
                courses[course_id].course_levels.append(str(level_id))

            return list(courses.values())

        except sqlite3.Error as e:
            print("Error loading courses:", e)
            return []
        