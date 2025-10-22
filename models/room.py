import sqlite3

class Room:
    def __init__(self, id: str, type: str, capacity: int):
        self.id = id
        self.type = type
        self.capacity = capacity

    def write_to_db(self, cur : sqlite3.Cursor):
        try:
            cur.execute("""
                INSERT INTO Rooms (id, type, capacity)
                        VALUES (?, ?, ?);
                """, (self.id, self.type, self.capacity))

        except sqlite3.Error as e:
            print("Error: ", e)

    def update_db(self, cur: sqlite3.Cursor):
        try:
            cur.execute("""
                UPDATE Rooms
                SET type = ?, capacity = ?
                WHERE id = ?;
            """, (self.type, self.capacity, self.id))

        except sqlite3.Error as e:
            print("Error (update_db):", e)

    def delete_db(self, cur: sqlite3.Cursor):
        try:
            cur.execute("""
                DELETE FROM Rooms WHERE id = ?;
            """, (self.id,))
            
        except sqlite3.Error as e:
            print("Error (delete_db):", e)

    @classmethod
    def load_db(cls, cur: sqlite3.Cursor):
        try:
            cur.execute("""
                SELECT id, type, capacity
                FROM Rooms
                ORDER BY id;
            """)

            rows = cur.fetchall()

            rooms = [cls(id=row[0], type=row[1], capacity=row[2]) for row in rows]

            return rooms

        except sqlite3.Error as e:
            print("Error (load_db):", e)
            return []
    
    """
        build the data representaion for the rooms to be used in the algorithm.
    """
    @classmethod
    def build_data_representation(cls, rooms: list["Room"]):
        """
            Rooms Map:
                    {
                        Type:{
                            Capacity: set_of_rooms with those properties
                        }
                    }
        """
        rooms_m = {}

        for room in rooms:
            rooms_m[room.type][room.capacity].add(room)

        return rooms_m