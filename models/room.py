import sqlite3

class Room:
    def __init__(self, id: str, type: str, capacity: int):
        self.id = id
        self.type = type
        self.capacity = capacity

    def build_structure(self):
        pass

    def write_to_db(self, cur : sqlite3.Cursor):
        try:
            cur.execute("""
                INSERT INTO Rooms (id, type, capacity)
                        VALUES (?, ?, ?);
                """, (self.id, self.type, self.capacity))

        except sqlite3.Error as e:
            print("Error: ", e)
