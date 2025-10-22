import sqlite3

from models.course import Course
from models.levels import Level
import heapq
from typing import List, Tuple


class Instructor:
    def __init__(self, instructor_id: int, name: str, role: str, qualified_courses: set[str]):
        self.instructor_id = instructor_id
        self.name = name
        self.role = role
        self.qualified_courses = qualified_courses
        self.assigned_courses = set()
        self.time_slots_assigned = 0

    # check if the instructor is qualified for the course.
    def is_qualified_for(self, course_code: str) -> bool:
        """Check if the instructor can teach a given course."""
        return course_code in self.qualified_courses

    def write_to_db(self, cur : sqlite3.Cursor):
        try:
            cur.execute("""
                INSERT INTO Instructors (id, name, role)
                        VALUES (?, ?, ?);
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

    """
        build the data representaion for the instructors to be used in the algorithm.
    """
    @classmethod
    def build_data_representation(cls, instructors : list["Instructor"]):
        instructors_map = {}
        for instructor in instructors:
            instructors_map[instructor.instructor_id] = instructor

        return instructors_map

    """
        Helper method used inside map_instructors_to_courses class public method
            this method uses max heap (min heap with negative values to simulate max heap) to select the least x instructors to assign the course to them.
    """
    @classmethod
    def _insert_to_heap(cls, least_loaded_heap: list[str],
        instructors : dict[str, "Instructor"], instructors_count: int, instructor_id: str):

        cur_time_slots = instructors[instructor_id].time_slots_assigned

        heapq.heappush(least_loaded_heap, (-cur_time_slots, instructor_id))

        if len(least_loaded_heap) > instructors_count:
            heapq.heappop(least_loaded_heap)

    """
        assign the course to the instructors and increase the time_slots_assigned in each instructor
    """
    @classmethod
    def _assign_course_to_instructors(cls, instructors: dict[str, "Instructor"],
        least_loaded_heap:List[Tuple[int, str]], course: "Course", levels: dict[str, "Level"]):

        for _, instructor_id in least_loaded_heap:
            instructors[instructor_id].assigned_courses.add(course.name)

            # calculate time_slots 
            time_slots = 0 
            for level_id in course.course_levels:
                # if lecture handle it via groups, else if Tut or Lab handle it via sections.
                if course.type.lower() == "lecture":
                    time_slots += course.time_slots * levels[level_id].groups
                
                else:
                    time_slots += course.time_slots * levels[level_id].sections

            instructors[instructor_id].time_slots_assigned += time_slots

    @classmethod
    def map_instructors_to_courses(cls, instructors : dict[str, "Instructor"], courses : dict[str, "Course"], levels : dict[str, "Level"]):
        """
            - each course has instructors who can teach this course.
            - each instructor has courses he can teach

            - Data Representation: 
                map[course-name] : CourseObj
                map[instructor-id] : InstructorObj

                CourseObj -> has set of instructor_ids who can teach it and has set of the isntructor_ids actually teach it.
                InstructorObj -> has set of course_ids he can teach, and a set of course_ids he actually teach.  


            Algorithm: 
                iterate over courses: 
                    for each course see the available instructors
                        see the least instructor has time_slots assigned to him
                            assign the course for this instructor

            Notes: 
                Japanes courses are special courses that have 3 instructors. 
                Tutorials and Labs have 2 instructors assigned to them.
                Lectures have 1 instructor assigned to them.

                Using max heap in the algorithm to determine the instructors who have least time_slots.

                if the course type is graduation we will skip it since we don't care about the instructor for this course. 
        """ 
        for course in courses.values():
            least_loaded_heap = []
            # look for the instructor who has the least time slots assigned to him
            """
                in the Japanes and Tutorials and Labs the heap works like that
                    if the heap size is lower than expected (3 for japanes and 2 for labs and tuts):
                        push to the heap
                    else
                        if the time_slots are lower than the top of the heap:
                            heap pop and heap push the current instructor.
            """

            instructors_count = 0
            if course.type.lower() == "graduation":
                continue
            elif course.type.lower() == "lecture":
                instructors_count = 1
            elif course.type.lower() == "japanese":
                instructors_count = 3
            else:
                instructors_count = 2

            for instructor_id in course.course_instructors:
                cls._insert_to_heap(least_loaded_heap, instructors, instructors_count, instructor_id)

            # assign course to instructors
            cls._assign_course_to_instructors(instructors, least_loaded_heap, course, levels)