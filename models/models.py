class Course:
    def __init__(self, code: str, name: str, credit: int, type: str):
        self.code = code
        self.name = name
        self.credit = credit
        self.type = type

    def build_structure(self):
        pass

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

    # check if the instructor prefer this slot or not.
    def prefers_slot(self, slot: str) -> bool:
        return not slot in self.not_preferred_slots
    
    # build the representation of the data in the program.
    def build_structure(self):
        pass

    # class method.
    def from_row(cls, row: list[str]):
        """ Create an Instructor from a CSV row. """

        instructor_id = row[0].strip()
        name = row[1].strip()
        role = row[2].strip().lower()

        # in the data it's like `Not on Sunday` => I just need `sunday`.
        tmp = row[3].split(' ')
        not_preferred_slot = tmp[2].lower()

        # Split the courses by comma and clean spaces ["XYZ123", "APC123", ...]
        courses = row[4].split(',')
        qualified_courses = [course.strip() for course in courses]

        return cls(instructor_id, name, role, not_preferred_slot, qualified_courses)

class Room:
    def __init__(self, id: str, type: str, capacity: int):
        self.id = id
        self.type = type
        self.capacity = capacity

    def build_structure(self):
        pass