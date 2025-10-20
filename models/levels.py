import sqlite3

class Level:
    def __init__(self, id: str, groups: int, sections: int, max_members_per_section: int):
        self.id = id
        self.groups = groups
        self.sections = sections
        self.max_members_per_section = max_members_per_section

    def write_to_db(self, cur: sqlite3.Cursor):
        try:
            cur.execute("""
                INSERT INTO Levels (id, groups, sections, max_members_per_section)
                VALUES (?, ?, ?, ?);
            """, (self.id, self.groups, self.sections, self.max_members_per_section))

        except sqlite3.Error as e:
            print("Error (write_to_db):", e)

    def update_db(self, cur: sqlite3.Cursor):
        try:
            cur.execute("""
                UPDATE Levels
                SET groups = ?, sections = ?, max_members_per_section = ?
                WHERE id = ?;
            """, (self.groups, self.sections, self.max_members_per_section, self.id))

        except sqlite3.Error as e:
            print("Error (update_db):", e)

    def delete_db(self, cur: sqlite3.Cursor):
        try:
            cur.execute("""
                DELETE FROM Levels WHERE id = ?;
            """, (self.id,))
            
            # NOTE: the levels will be deleted from CourseLevels too due to the ON DELETE CASCADE in the schema. 
            # but I added it for safety.
            cur.execute("""
                DELETE FROM CourseLevels WHERE level_id = ?;
            """, (self.id,))

        except sqlite3.Error as e:
            print("Error (delete_db):", e)

    @classmethod
    def load_db(cls, cur: sqlite3.Cursor):
        """Load all levels from the database and return them as Level objects."""
        try:
            cur.execute("""
                SELECT id, groups, sections, max_members_per_section
                FROM Levels
                ORDER BY id;
            """)

            rows = cur.fetchall()

            levels = [cls(id=row[0], groups=row[1], sections=row[2], max_members_per_section=row[3]) for row in rows]
            return levels

        except sqlite3.Error as e:
            print("Error (load_db):", e)
            return []
        