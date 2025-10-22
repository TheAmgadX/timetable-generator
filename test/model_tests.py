import unittest
import sqlite3
import heapq

# --- Import all your model classes
# This assumes your models are in a directory named 'models'
from models.levels import Level
from models.room import Room
from models.course import Course
from models.instructor import Instructor

# --- Database Schema
# The exact schema from your script, to be created in-memory
SCHEMA = """
CREATE TABLE IF NOT EXISTS Levels (
    id TEXT PRIMARY KEY,
    groups INTEGER,
    sections INTEGER,
    max_members_per_section INTEGER,
    students_count INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS Courses (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    type TEXT CHECK(type IN ('Lecture', 'Lab', 'Tutorial', 'Graduation', 'Japanese')),
    time_slots INTEGER
);
CREATE TABLE IF NOT EXISTS CourseLevels (
    course_id TEXT,
    level_id TEXT,
    PRIMARY KEY (course_id, level_id),
    FOREIGN KEY (course_id) REFERENCES Courses(id) ON DELETE CASCADE,
    FOREIGN KEY (level_id) REFERENCES Levels(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS Instructors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT
);
CREATE TABLE IF NOT EXISTS InstructorCourses (
    instructor_id TEXT,
    course_id TEXT,
    PRIMARY KEY (instructor_id, course_id),
    FOREIGN KEY (instructor_id) REFERENCES Instructors(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Courses(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS Rooms (
    id TEXT PRIMARY KEY,
    type TEXT CHECK(type IN ('Lecture', 'Lab', 'Tutorial')),
    capacity INTEGER
);
"""

class TestModelBase(unittest.TestCase):
    """
    Base test class that sets up a fresh in-memory database
    for EVERY single test. This guarantees test isolation
    and doesn't touch the real 'timetable.db' file.
    """
    def setUp(self):
        """Called before every test method."""
        # Create a new in-memory database
        self.conn = sqlite3.connect(':memory:')
        self.cur = self.conn.cursor()
        
        # Enable foreign key constraints
        self.cur.execute("PRAGMA foreign_keys = ON;")
        
        # Create the full database schema
        self.cur.executescript(SCHEMA)
        self.conn.commit()

    def tearDown(self):
        """Called after every test method."""
        # Close the cursor and connection, destroying the in-memory db
        self.cur.close()
        self.conn.close()

# --- CRUD Tests for each Model ---

class TestLevelModel(TestModelBase):
    """Tests for the Level model."""
    
    def test_level_write_and_load(self):
        level1 = Level("L1", 1, 2, 30, 60)
        level1.write_to_db(self.cur)
        self.conn.commit()
        
        loaded_levels = Level.load_db(self.cur)
        
        self.assertEqual(len(loaded_levels), 1)
        self.assertEqual(loaded_levels[0].id, "L1")
        self.assertEqual(loaded_levels[0].groups, 1)
        self.assertEqual(loaded_levels[0].students_count, 60)

    def test_level_update(self):
        level1 = Level("L1", 1, 2, 30, 60)
        level1.write_to_db(self.cur)
        self.conn.commit()
        
        level1_updated = Level("L1", 2, 4, 25, 100)
        level1_updated.update_db(self.cur)
        self.conn.commit()
        
        loaded_levels = Level.load_db(self.cur)
        
        self.assertEqual(len(loaded_levels), 1)
        self.assertEqual(loaded_levels[0].groups, 2)
        self.assertEqual(loaded_levels[0].sections, 4)
        self.assertEqual(loaded_levels[0].students_count, 100)

    def test_level_delete(self):
        level1 = Level("L1", 1, 2, 30, 60)
        level1.write_to_db(self.cur)
        self.conn.commit()
        
        level1.delete_db(self.cur)
        self.conn.commit()
        
        loaded_levels = Level.load_db(self.cur)
        self.assertEqual(len(loaded_levels), 0)

class TestRoomModel(TestModelBase):
    """Tests for the Room model."""
    
    def test_room_write_and_load(self):
        room1 = Room("R101", "Lecture", 100)
        room1.write_to_db(self.cur)
        self.conn.commit()
        
        loaded_rooms = Room.load_db(self.cur)
        
        self.assertEqual(len(loaded_rooms), 1)
        self.assertEqual(loaded_rooms[0].id, "R101")
        self.assertEqual(loaded_rooms[0].type, "Lecture")
        self.assertEqual(loaded_rooms[0].capacity, 100)

    def test_room_update(self):
        room1 = Room("R101", "Lecture", 100)
        room1.write_to_db(self.cur)
        self.conn.commit()
        
        room1_updated = Room("R101", "Lab", 50)
        room1_updated.update_db(self.cur)
        self.conn.commit()
        
        loaded_rooms = Room.load_db(self.cur)
        
        self.assertEqual(len(loaded_rooms), 1)
        self.assertEqual(loaded_rooms[0].type, "Lab")
        self.assertEqual(loaded_rooms[0].capacity, 50)

    def test_room_delete(self):
        room1 = Room("R101", "Lecture", 100)
        room1.write_to_db(self.cur)
        self.conn.commit()
        
        room1.delete_db(self.cur)
        self.conn.commit()
        
        loaded_rooms = Room.load_db(self.cur)
        self.assertEqual(len(loaded_rooms), 0)

class TestCourseModel(TestModelBase):
    """Tests for the Course model. Needs to manage relations."""
    
    def setUp(self):
        """Extend the base setup to create prerequisite data."""
        super().setUp()
        # Courses need Levels to exist first
        self.level1 = Level("L1", 1, 2, 30, 60)
        self.level2 = Level("L2", 2, 4, 30, 120)
        self.level1.write_to_db(self.cur)
        self.level2.write_to_db(self.cur)
        
        # Instructors need Courses to exist, and Courses need Instructors
        # for load_db. This is a bit complex.
        # For write/update/delete, we only need Levels.
        self.course1 = Course("C101", "Intro to CS", "Lecture", 3, {"L1"}, set())
        
        # For load_db, we need a fully linked item
        self.inst1 = Instructor("I101", "Dr. A", "Prof", {"C101"})
        
    def test_course_write(self):
        self.course1.write_to_db(self.cur)
        self.conn.commit()
        
        # Check Courses table
        res_course = self.cur.execute("SELECT * FROM Courses WHERE id=?", ("C101",)).fetchone()
        self.assertIsNotNone(res_course)
        self.assertEqual(res_course[1], "Intro to CS")
        
        # Check CourseLevels table
        res_level = self.cur.execute("SELECT * FROM CourseLevels WHERE course_id=?", ("C101",)).fetchone()
        self.assertIsNotNone(res_level)
        self.assertEqual(res_level[1], "L1")

    def test_course_load_db(self):
        """
        Tests load_db. NOTE: Your load_db uses INNER JOIN on
        CourseLevels AND InstructorCourses, so a Course will ONLY
        load if it's linked to BOTH a level and an instructor.
        """
        # 1. Write the course (linked to L1)
        self.course1.write_to_db(self.cur)
        
        # 2. Write the instructor (linked to C101)
        self.inst1.write_to_db(self.cur)
        self.conn.commit()
        
        # 3. Now, load_db should find it
        loaded_courses = Course.load_db(self.cur)
        
        self.assertEqual(len(loaded_courses), 1)
        self.assertEqual(loaded_courses[0].code, "C101")
        self.assertEqual(loaded_courses[0].course_levels, {"L1"})
        self.assertEqual(loaded_courses[0].course_instructors, {"I101"})

    def test_course_update(self):
        self.course1.write_to_db(self.cur)
        self.conn.commit()
        
        # Update name and change level from L1 to L2
        course1_updated = Course("C101", "Advanced CS", "Lecture", 3, {"L2"}, set())
        course1_updated.update_db(self.cur)
        self.conn.commit()
        
        # Check Courses table for new name
        res_course = self.cur.execute("SELECT * FROM Courses WHERE id=?", ("C101",)).fetchone()
        self.assertEqual(res_course[1], "Advanced CS")
        
        # Check CourseLevels table: L1 link should be gone
        res_level1 = self.cur.execute("SELECT * FROM CourseLevels WHERE course_id=? AND level_id=?", ("C101", "L1")).fetchone()
        self.assertIsNone(res_level1)
        
        # Check CourseLevels table: L2 link should exist
        res_level2 = self.cur.execute("SELECT * FROM CourseLevels WHERE course_id=? AND level_id=?", ("C101", "L2")).fetchone()
        self.assertIsNotNone(res_level2)

    def test_course_delete(self):
        self.course1.write_to_db(self.cur)
        self.inst1.write_to_db(self.cur)
        self.conn.commit()
        
        self.course1.delete_db(self.cur)
        self.conn.commit()
        
        # Check tables are now empty
        res_course = self.cur.execute("SELECT * FROM Courses").fetchall()
        self.assertEqual(len(res_course), 0)
        
        res_level = self.cur.execute("SELECT * FROM CourseLevels").fetchall()
        self.assertEqual(len(res_level), 0)
        
        # Check cascade delete on InstructorCourses
        res_inst_course = self.cur.execute("SELECT * FROM InstructorCourses").fetchall()
        self.assertEqual(len(res_inst_course), 0)

class TestInstructorModel(TestModelBase):
    """Tests for the Instructor model. Needs to manage relations."""
    
    def setUp(self):
        super().setUp()
        # Instructors need Courses to exist first
        self.level1 = Level("L1", 1, 2, 30, 60)
        self.level1.write_to_db(self.cur)
        
        self.course1 = Course("C101", "Intro to CS", "Lecture", 3, {"L1"}, set())
        self.course2 = Course("C102", "Data Struct", "Lab", 2, {"L1"}, set())
        self.course1.write_to_db(self.cur)
        self.course2.write_to_db(self.cur)
        
        self.inst1 = Instructor("I101", "Dr. A", "Prof", {"C101"})

    def test_instructor_write(self):
        self.inst1.write_to_db(self.cur)
        self.conn.commit()
        
        # Check Instructors table
        res_inst = self.cur.execute("SELECT * FROM Instructors WHERE id=?", ("I101",)).fetchone()
        self.assertIsNotNone(res_inst)
        self.assertEqual(res_inst[1], "Dr. A")
        
        # Check InstructorCourses table
        res_link = self.cur.execute("SELECT * FROM InstructorCourses WHERE instructor_id=?", ("I101",)).fetchone()
        self.assertIsNotNone(res_link)
        self.assertEqual(res_link[1], "C101")

    def test_instructor_load_db(self):
        """
        Tests load_db. NOTE: Your load_db uses INNER JOIN,
        so an Instructor will ONLY load if they are qualified
        for at least one course.
        """
        self.inst1.write_to_db(self.cur)
        self.conn.commit()
        
        loaded_inst = Instructor.load_db(self.cur)
        
        self.assertEqual(len(loaded_inst), 1)
        self.assertEqual(loaded_inst[0].instructor_id, "I101")
        self.assertEqual(loaded_inst[0].qualified_courses, {"C101"})

    def test_instructor_update(self):
        self.inst1.write_to_db(self.cur)
        self.conn.commit()
        
        # Update name and change course from C101 to C102
        inst1_updated = Instructor("I101", "Dr. B", "Assist. Prof", {"C102"})
        inst1_updated.update_db(self.cur)
        self.conn.commit()
        
        # Check Instructors table for new name
        res_inst = self.cur.execute("SELECT * FROM Instructors WHERE id=?", ("I101",)).fetchone()
        self.assertEqual(res_inst[1], "Dr. B")
        self.assertEqual(res_inst[2], "Assist. Prof")
        
        # Check InstructorCourses table: C101 link should be gone
        res_link1 = self.cur.execute("SELECT * FROM InstructorCourses WHERE instructor_id=? AND course_id=?", ("I101", "C101")).fetchone()
        self.assertIsNone(res_link1)
        
        # Check InstructorCourses table: C102 link should exist
        res_link2 = self.cur.execute("SELECT * FROM InstructorCourses WHERE instructor_id=? AND course_id=?", ("I101", "C102")).fetchone()
        self.assertIsNotNone(res_link2)

    def test_instructor_delete(self):
        self.inst1.write_to_db(self.cur)
        self.conn.commit()
        
        self.inst1.delete_db(self.cur)
        self.conn.commit()
        
        # Check tables are now empty
        res_inst = self.cur.execute("SELECT * FROM Instructors").fetchall()
        self.assertEqual(len(res_inst), 0)
        
        res_link = self.cur.execute("SELECT * FROM InstructorCourses").fetchall()
        self.assertEqual(len(res_link), 0)

# --- Algorithm Logic Tests ---

class TestInstructorMapping(unittest.TestCase):
    """
    Tests the Instructor.map_instructors_to_courses algorithm.
    This test does NOT use the database. It tests the Python logic.
    """
    
    def setUp(self):
        """Create all the mock objects needed for the algorithm."""
        
        # 1. Mock Levels
        # L1: 1 group, 2 sections
        self.l1 = Level("L1", 1, 2, 30, 60)
        # L2: 2 groups, 4 sections
        self.l2 = Level("L2", 2, 4, 30, 120)
        self.levels_map = { "L1": self.l1, "L2": self.l2 }
        
        # 2. Mock Instructors (with varying initial loads)
        self.i1 = Instructor("I1", "Inst 1", "Prof", set())
        self.i1.time_slots_assigned = 10
        
        self.i2 = Instructor("I2", "Inst 2", "Prof", set())
        self.i2.time_slots_assigned = 20
        
        self.i3 = Instructor("I3", "Inst 3", "TA", set())
        self.i3.time_slots_assigned = 5
        
        self.i4 = Instructor("I4", "Inst 4", "TA", set())
        self.i4.time_slots_assigned = 0
        
        self.instructors_map = {
            "I1": self.i1, "I2": self.i2, "I3": self.i3, "I4": self.i4
        }
        
        # 3. Mock Courses
        # Lecture (1 inst), L1 (1 group) -> 3 * 1 = 3 slots
        self.c_lec = Course("C1", "Lecture 1", "Lecture", 3, {"L1"}, {"I1", "I2"})
        
        # Lab (2 inst), L1 (2 sections) -> 2 * 2 = 4 slots
        self.c_lab = Course("C2", "Lab 1", "Lab", 2, {"L1"}, {"I1", "I2", "I3"})
        
        # Japanese (3 inst), L2 (4 sections) -> 1 * 4 = 4 slots
        self.c_jap = Course("C3", "Japanese 1", "Japanese", 1, {"L2"}, {"I1", "I2", "I3", "I4"})
        
        self.courses_map = {
            "C1": self.c_lec,
            "C2": self.c_lab,
            "C3": self.c_jap
        }

    def test_mapping_load_balancing(self):
        """
        Run the full mapping and check final loads and assignments.
        We run this as one large test to check how loads accumulate.
        
        Initial Loads: I1=10, I2=20, I3=5, I4=0
        """
        
        # Create a stable order for the test
        # We can't guarantee dict iteration order, so we process one by one
        
        # --- 1. Process Lecture (C1) ---
        # Needs 1 instructor. Qualified: {I1, I2}. Loads: I1=10, I2=20
        # Should pick I1 (least loaded)
        # Slots to add: type=Lecture, slots=3, L1.groups=1 -> 3*1 = 3
        
        lec_map = {"C1": self.c_lec}
        Instructor.map_instructors_to_courses(self.instructors_map, lec_map, self.levels_map)
        
        self.assertIn(self.c_lec.name, self.i1.assigned_courses)
        self.assertNotIn(self.c_lec.name, self.i2.assigned_courses)
        self.assertEqual(self.i1.time_slots_assigned, 10 + 3) # 13
        self.assertEqual(self.i2.time_slots_assigned, 20)
        
        # --- 2. Process Lab (C2) ---
        # Needs 2 instructors. Qualified: {I1, I2, I3}.
        # Loads: I1=13, I2=20, I3=5
        # Should pick I3 and I1 (the two least loaded)
        # Slots to add: type=Lab, slots=2, L1.sections=2 -> 2*2 = 4
        
        lab_map = {"C2": self.c_lab}
        Instructor.map_instructors_to_courses(self.instructors_map, lab_map, self.levels_map)
        
        self.assertIn(self.c_lab.name, self.i1.assigned_courses)
        self.assertIn(self.c_lab.name, self.i3.assigned_courses)
        self.assertNotIn(self.c_lab.name, self.i2.assigned_courses)
        self.assertEqual(self.i1.time_slots_assigned, 13 + 4) # 17
        self.assertEqual(self.i2.time_slots_assigned, 20)
        self.assertEqual(self.i3.time_slots_assigned, 5 + 4)  # 9

        # --- 3. Process Japanese (C3) ---
        # Needs 3 instructors. Qualified: {I1, I2, I3, I4}
        # Loads: I1=17, I2=20, I3=9, I4=0
        # Should pick I4, I3, and I1 (the three least loaded)
        # Slots to add: type=Japanese, slots=1, L2.sections=4 -> 1*4 = 4
        
        jap_map = {"C3": self.c_jap}
        Instructor.map_instructors_to_courses(self.instructors_map, jap_map, self.levels_map)

        self.assertIn(self.c_jap.name, self.i1.assigned_courses)
        self.assertIn(self.c_jap.name, self.i3.assigned_courses)
        self.assertIn(self.c_jap.name, self.i4.assigned_courses)
        self.assertNotIn(self.c_jap.name, self.i2.assigned_courses)

        # --- 4. Check Final Loads ---
        self.assertEqual(self.i1.time_slots_assigned, 17 + 4) # 21
        self.assertEqual(self.i2.time_slots_assigned, 20)       # 20 (unchanged)
        self.assertEqual(self.i3.time_slots_assigned, 9 + 4)  # 13
        self.assertEqual(self.i4.time_slots_assigned, 0 + 4)   # 4

    def test_assignment_counts(self):
        """Test just the number of assigned instructors."""
        
        # Reset loads to 0 for a simple count test
        for inst in self.instructors_map.values():
            inst.time_slots_assigned = 0
            inst.assigned_courses = set()
            
        # Run the full mapping
        Instructor.map_instructors_to_courses(self.instructors_map, self.courses_map, self.levels_map)
        
        # Check how many instructors were assigned to each course
        
        lec_assignees = {i.instructor_id for i in self.instructors_map.values() if self.c_lec.name in i.assigned_courses}
        lab_assignees = {i.instructor_id for i in self.instructors_map.values() if self.c_lab.name in i.assigned_courses}
        jap_assignees = {i.instructor_id for i in self.instructors_map.values() if self.c_jap.name in i.assigned_courses}
        
        self.assertEqual(len(lec_assignees), 1) # Lecture
        self.assertEqual(len(lab_assignees), 2) # Lab
        self.assertEqual(len(jap_assignees), 3) # Japanese

if __name__ == '__main__':
    unittest.main()
