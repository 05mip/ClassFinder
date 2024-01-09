from datetime import datetime, timedelta


class Course:
    def __init__(self, id, type, section, credits, instructor, schedule,
                 classroom, capacity, enrolled, status) -> None:
        self.id = id
        self.type = type
        self.section = section
        self.credits = credits
        self.instructor = instructor
        self.schedule = schedule
        self.classroom = classroom
        self.capacity = capacity
        self.enrolled = enrolled
        self.status = status
        self.rating = -1
        self.priority = float('inf')


def rate_time(time):
    time_format = "%I:%M%p"
    start, end = time.split('-')

    if 'p' not in end.lower():
        start += 'am'
        end += 'am'
    else:
        start += 'pm'
        end += 'm'

    start_time = datetime.strptime(start.strip(), time_format)
    end_time = datetime.strptime(end.strip(), time_format)

    target_time = datetime.strptime("2:00PM", time_format)

    midpoint = start_time + (end_time - start_time) / 2
    time_difference = abs(midpoint - target_time)

    max_difference = timedelta(hours=5)
    score = 1.0 - min(1.0, time_difference.total_seconds() / max_difference.total_seconds())
    return round(score, 2)


def rate_type(type):
    if "lec" in type.lower() or "sem" in type.lower():
        return 0
    elif "dis" in type.lower() or "lab" in type.lower():
        return 1
    else:
        raise ValueError("Something went wrong")


def convert_to_24_hour(time_str):
    hours_minutes, period = time_str[:-1].split(':')
    hours = int(hours_minutes)
    minutes = int(period)

    if time_str[-1] == 'p':
        if hours != 12:
            hours = (hours + 12) % 24

    if hours == 12 and time_str[-1] == 'a':
        hours = 0

    time_24_hour = hours + minutes / 60.0
    return time_24_hour


def convert_time(timeslot):

    time_start, time_end = map(str.strip, timeslot.split('-'))
    if 'p' in time_end:
        time_start_num = float(time_start[:time_start.index(':')])
        time_end_num = float(time_end.strip()[:time_end.index(':')])
        if time_start_num <= time_end_num and time_start_num != 11:
            time_start += 'p'
        else:
            time_start += 'a'
    else:
        time_start += 'a'
        time_end += 'a'

    time_start = convert_to_24_hour(time_start)
    time_end = convert_to_24_hour(time_end)

    return time_start, time_end


def days_overlap(days1, days2):
    days_overlap = set(days1) & set(days2)
    return bool(days_overlap)


def times_overlap(time, schedule):
    class_days = time[:time.index(' ')]
    class_start, class_end = convert_time(time[time.index(' ') + 3:])
    for course in schedule:
        # print(course)
        start_time, end_time = convert_time(course[1].schedule[course[1].schedule.index(' ')+3:])
        if class_start < end_time and start_time < class_end and days_overlap(class_days, course[1].schedule[:course[1].schedule.index(' ')]):
            return True
    return False


def contains_letter(s):
    return any(char.isalpha() for char in s)


def make_schedule(classes):
    schedule = []

    for i in range(len(classes)):
        classes[i] = [classes[i][0]] + sorted(classes[i][1:], key=lambda x: (rate_type(x.type), -x.rating, -rate_time(x.schedule[x.schedule.index(" ") + 1:])))


    for course in classes:
        main_sections = [section for section in course[1:] if section.type.lower() in ['lec', 'sem']]
        secondary_sections = [section for section in course[1:] if section.type.lower() in ['dis', 'lab']]

        best_main = None
        best_secondary = None
        multiple_secondaries = True if any(contains_letter(course.section) for course in secondary_sections) else False

        for main_section in main_sections:
            if not times_overlap(main_section.schedule, schedule) and "open" in main_section.status.lower():
                best_main = main_section 

                if secondary_sections != []:
                    for secondary_section in secondary_sections:
                            if (multiple_secondaries and main_section.section.strip() in secondary_section.section) or not multiple_secondaries:                       #if match main and times don't overlap
                                if not times_overlap(secondary_section.schedule, schedule) and 'open' in secondary_section.status.lower():                 #set as best
                                    best_secondary = secondary_section
                                    break

                    if best_secondary == None:
                        best_main = None
                        best_secondary = None
                        continue
                    else:
                        schedule.append((course[0], best_main))
                        schedule.append((course[0], best_secondary))
                        break
                else:
                    schedule.append((course[0], best_main))
                    break
        if best_main == None or (best_main != None and best_secondary == None):
            raise ValueError(f'No sections from {course[0]} could fit in your schedule')
    return schedule


# ====================================================================================

def test():
    from tabulate import tabulate

    class Cours:
        def __init__(self, id, type, section, credits, instructor, schedule,
                    classroom, capacity, enrolled, status, rating) -> None:
            self.id = id
            self.type = type
            self.section = section
            self.credits = credits
            self.instructor = instructor
            self.schedule = schedule
            self.classroom = classroom
            self.capacity = capacity
            self.enrolled = enrolled
            self.status = status
            self.rating = rating
            self.priority = float('inf')

    classes = [
        [
            "MATH 3A",
            Cours('44580', 'Lec', 'A', '4', 'ZHANG, Y.', 'MWF   9:00- 9:50', 'PSLH 100', '171', '0', 'OPEN', 3.4),
            Cours('44583', 'Dis', 'A1', '0', 'STAFF', 'TuTh   3:00- 3:50p', 'DBH 1500', '63', '0', 'OPEN', -1),
            Cours('44586', 'Dis', 'A2', '0', 'STAFF', 'TuTh   8:00- 8:50', 'MSTB 122', '54', '0', 'OPEN', -1),
            Cours('44587', 'Dis', 'A3', '0', 'STAFF', 'TuTh   12:00-12:50p', 'MSTB 122', '54', '0', 'OPEN', -1),
            Cours('44590', 'Lec', 'B', '4', 'LIEBER, J.', 'MWF   11:00-11:50', 'SSH 100', '171', '0', 'OPEN', 4.8),
            Cours('44591', 'Dis', 'B1', '0', 'STAFF', 'TuTh   8:00- 8:50', 'PSCB 120', '57', '0', 'OPEN', -1),
            Cours('44596', 'Dis', 'B2', '0', 'STAFF', 'TuTh   12:00-12:50p', 'DBH 1500', '60', '0', 'OPEN', -1),
            Cours('44597', 'Dis', 'B3', '0', 'STAFF', 'TuTh   1:00- 1:50p', 'MSTB 122', '54', '0', 'OPEN', -1),
            Cours('44602', 'Lec', 'C', '4', 'LIEBER, J.', 'MWF   12:00-12:50p', 'SSH 100', '171', '0', 'OPEN', 4.8),
            Cours('44603', 'Dis', 'C1', '0', 'STAFF', 'TuTh   11:00-11:50', 'SSTR 103', '60', '0', 'OPEN', -1),
            Cours('44606', 'Dis', 'C2', '0', 'STAFF', 'TuTh   8:00- 8:50', 'PSCB 140', '57', '0', 'OPEN', -1),
            Cours('44607', 'Dis', 'C3', '0', 'STAFF', 'TuTh   2:00- 2:50p', 'MSTB 122', '54', '0', 'OPEN', -1)
        ],
        [
            "ICS 6B",
            Cours('35510', 'Lec', 'A', '4', 'DILLENCOURT, M.', 'MWF   9:00- 9:50', 'ELH 100', '195', '0', 'OPEN', 3.3),
            Cours('35511', 'Dis', '1', '0', 'STAFF DILLENCOURT, M.', 'MW   11:00-11:50', 'SH 134', '65', '0', 'OPEN', -1),
            Cours('35512', 'Dis', '2', '0', 'STAFF DILLENCOURT, M.', 'MW   12:00-12:50p', 'SH 134', '65', '0', 'OPEN', -1),
            Cours('35513', 'Dis', '3', '0', 'STAFF DILLENCOURT, M.', 'MW   3:00- 3:50p', 'SH 134', '65', '0', 'OPEN', -1)
        ],
        [
            "ICS 33",
            Cours('35620', 'Lec', 'A', '4', 'THORNTON, A.', 'TuTh   5:00- 6:20p', 'PSLH 100', '210', '0', 'OPEN', 4.5),
            Cours('35621', 'Lec', 'B', '4', 'STAFF THORNTON, A.', 'TuTh   6:30- 7:50p', 'ELH 100', '210', '0', 'OPEN', -1),
            Cours('35622', 'Lab', '1', '0', 'STAFF THORNTON, A.', 'MWF   8:00- 9:20', 'ICS 364A', '48', '0', 'OPEN', -1),
            Cours('35623', 'Lab', '2', '0', 'STAFF THORNTON, A.', 'MWF   9:30-10:50', 'ICS 364A', '48', '0', 'OPEN', -1),
            Cours('35624', 'Lab', '3', '0', 'STAFF THORNTON, A.', 'MWF   11:00-12:20p', 'ICS 364A', '48', '0', 'OPEN', -1),
            Cours('35625', 'Lab', '4', '0', 'STAFF THORNTON, A.', 'MWF   12:30- 1:50p', 'ICS 364A', '48', '0', 'OPEN', -1),
            Cours('35626', 'Lab', '5', '0', 'STAFF THORNTON, A.', 'MWF   2:00- 3:20p', 'ICS 364A', '48', '0', 'OPEN', -1),
            Cours('35627', 'Lab', '6', '0', 'STAFF THORNTON, A.', 'MWF   3:30- 4:50p', 'ICS 364A', '48', '0', 'OPEN', -1),
            Cours('35628', 'Lab', '7', '0', 'STAFF THORNTON, A.', 'MWF   5:00- 6:20p', 'ICS 364A', '48', '0', 'OPEN', -1),
            Cours('35629', 'Lab', '8', '0', 'STAFF THORNTON, A.', 'MWF   6:30- 7:50p', 'ICS 364A', '48', '0', 'OPEN', -1)

        ]
    ]

    def print_schedule(schedule):

        data = [
            [
                course[0], course[1].id, course[1].type, course[1].section, course[1].credits,
                course[1].instructor, course[1].schedule, course[1].classroom,
                course[1].capacity, course[1].enrolled, course[1].rating, course[1].status, course[1].rating
            ]
            for course in schedule
        ]

        headers = [
            'Course', 'ID', 'Type', 'Section',
            'Credits', 'Instructor', 'Schedule',
            'Classroom', 'Capacity', 'Enrolled', 'Rating', 'Status', 'Professor Rating'
        ]
        print("SCHEDULE:")
        print(tabulate(data, headers=headers, tablefmt='grid'))


    schedule = make_schedule(classes)
    print_schedule(schedule)

