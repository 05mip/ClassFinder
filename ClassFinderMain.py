from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from tabulate import tabulate
import ratemyprofessor
import CourseModule


def _connect(website):
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(website)
    driver.minimize_window()
    return driver


def print_terms(driver):
    terms = Select(driver.find_element(By.NAME, "YearTerm"))
    for term in terms.options[0:5]:
        print(f'{terms.options.index(term) + 1}. {term.text}')
    return terms


def ask_term(driver):
    print("Choose Term:\n")
    terms_dropdown = print_terms(driver)
    while True:
        try:
            user_term = int(input("\nEnter Desired Term Number: "))
            if 1 <= user_term <= 5:
                break
            else:
                print("\nInvalid Term\n")
        except:
            print("\nInvalid Term\n")
    terms_dropdown.select_by_index(user_term - 1)


def get_depts(driver):
    dept_names = Select(driver.find_element(By.NAME, "Dept"))
    longest = 0
    depts = {}
    for dept_name_option in dept_names.options:
        dept_name = dept_name_option.text
        if "." not in dept_name:
            continue
        dept_id = dept_name[:dept_name.index(".")].strip()
        dept_full = dept_name.split('.')[-1].strip()
        depts[dept_id] = dept_full
        if len(dept_id) > longest:
            longest = len(dept_id)
    return dept_names, depts, longest


def print_depts(depts, longest):
    for id in depts.keys():
        num_spaces = " "*(longest - len(id) + 5)
        print(f"{id}{num_spaces}{depts[id]}")


def ask_dept(driver):
    depts_dropdown, depts, longest = get_depts(driver)

    print()
    print("------------------------------------------------")
    print("**********ALL DEPARTMENTS LISTED BELOW**********")
    print("------------------------------------------------")
    print_depts(depts, longest)
    print()
    print("------------------------------------------------")
    while True:
        course_dept = input("Enter Desired Department (Must be exact): ")
        if course_dept.upper() in depts.keys():
            break
    depts_dropdown.select_by_value(course_dept)
    return course_dept


def submit_params(driver):
    submit_button = driver.find_element(By.XPATH, "//input[@value='Display Web Results']")
    submit_button.click()


def find_course(driver, course_dept):
    course_id = input("Enter the course ID (e.g. 50, 6B, 32A): ")

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    courses = []
    in_sections = False

    for element in soup.find_all('tr', valign = 'top'):
        text = element.get_text(strip=True).upper()
        if not in_sections:
            if course_dept.upper() in text and course_id.upper() in text:
                rest = text[text.index(course_id) + len(course_id):]
                if not rest[0].isdigit():
                    courses.append(text)
                    in_sections = True
        else:
            if text.startswith(course_dept):
                break
            text_soup = BeautifulSoup(str(element), 'html.parser')
            course_data = [td.get_text(strip=True) for td in text_soup.find_all('td')]

            id = course_data[0]
            type = course_data[1]
            section = course_data[2]
            credits = course_data[3]
            instructor = course_data[4]
            schedule = course_data[6]
            classroom = course_data[7]
            capacity = course_data[9]
            enrolled = course_data[10]
            status = course_data[17]

            course = CourseModule.Course(
                id, type, section, credits, 
                instructor, schedule, classroom,
                capacity, enrolled, status
            )

            courses.append(course)

    return courses


def print_sections(courses):    
    data = [
        [
            course.id, course.type, course.section, course.credits,
            course.instructor, course.schedule, course.classroom, 
            course.capacity, course.enrolled, course.status
        ]
        for course in courses[1:]
    ]

    headers = [
    'ID', 'Type', 'Section', 'Credits',
    'Instructor', 'Schedule', 'Classroom',
    'Capacity', 'Enrolled', 'Status'
    ]

    print("\n" + courses[0])
    print(tabulate(data, headers=headers, tablefmt='grid'))
    

def print_schedule(schedule):

    data = [
        [
            course[0], course[1].id, course[1].type, course[1].section, course[1].credits,
            course[1].instructor, course[1].schedule, course[1].classroom, 
            course[1].capacity, course[1].enrolled, course[1].status
        ]
        for course in schedule
    ]

    headers = [
        'Course', 'ID', 'Type', 'Section', 
        'Credits', 'Instructor', 'Schedule', 
        'Classroom', 'Capacity', 'Enrolled', 'Status'
    ]
    print("SCHEDULE:")    
    print(tabulate(data, headers=headers, tablefmt='grid'))


def confirm_classes():
    while True:
        confirm = input("CONFIRM ADD Y/N: ")
        if confirm == "Y":
            return True
        elif confirm == "N":
            return False


def search_profs(classes):
    print("\nSearching professors on Rate My Professors...")
    for course in classes:
        for section in course[1:]:
            if "Dis" in section.type:
                continue
            name = section.instructor
            if "." in section.instructor:
                name = section.instructor.replace(".", "")
            
            professor = ratemyprofessor.get_professor_by_school_and_name(
                        ratemyprofessor.get_school_by_name("UC Irvine"), name)
            if not professor:
                continue
            section.rating = professor.rating
        if classes.index(course) == len(classes) // 2:
            print("\nAlmost Done...\n")


def main(classes):
    webreg = 'https://www.reg.uci.edu/perl/WebSoc'
    driver = _connect(webreg)
    while True:
        ask_term(driver)
        course_dept = ask_dept(driver)
        submit_params(driver)
        sections = find_course(driver, course_dept)
        print_sections(sections)
        if confirm_classes():
            classes.append(sections)
        
        if classes != []:
            finished_adding = input("Are you done adding classes Y/N? ")
            if finished_adding == "Y":
                driver.close()
                break
            elif finished_adding == "N":
                driver.close()
                driver = _connect(webreg)
                continue
    search_profs(classes)
    schedule = CourseModule.make_schedule(classes)

    print_schedule(schedule)


if __name__ == "__main__":
    classes = []
    main(classes)
    
#classes[
#   ["course1 name", Course, Course, Course]
#   ["course2 Name", Course, Course, Course]
# ]


# Notes
# Make it not open a new window everytime
# make it so u only have to choose term once
# make it so department list is passed around as arg instead of being made everytime
# error handling if class not found
# room for error so user doesnt have to put in exact class name (make upper/lower)
# Fix for only labs no main
# Fix TBA