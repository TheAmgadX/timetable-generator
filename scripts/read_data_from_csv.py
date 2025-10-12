import csv
from models.models import *

courses = []
instructors = []
rooms = []

def load_data():

    ''' read courses file data '''
    with open("../Courses.csv") as courses_file:
        csv_reader = csv.reader(courses_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue

            course = Course(row[0], row[1], row[2], row[3])
            courses.append(course)
            line_count += 1


        print(f"number of courses: {line_count - 1}")
    
    ''' read instructors file data '''
    with open("../Instructors.csv") as instructors_file:
        csv_reader = csv.reader(instructors_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            # skip first line.
            if line_count == 0:
                line_count += 1
                continue

            instructor = Instructor.from_row(row)

            instructors.append(instructor)
            line_count += 1


        print(f"number of instructors: {line_count - 1}")

    ''' read rooms file data '''
    with open("../Rooms.csv") as rooms_file:
        csv_reader = csv.reader(rooms_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            # skip first line.
            if line_count == 0:
                line_count += 1
                continue

            room = Room(row[0], row[1], int(row[2]))
            rooms.append(room)
            line_count += 1


        print(f"number of rooms: {line_count - 1}")

