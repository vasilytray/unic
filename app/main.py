from fastapi import FastAPI
from app.auth.utils import json_to_dict_list
from app.main import SStudent
import os
from typing import Optional

# Получаем путь к директории текущего скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

# Переходим на уровень выше
parent_dir = os.path.dirname(script_dir)

# Получаем путь к JSON
path_to_json = os.path.join(parent_dir, 'students.json')
#можно сократить, сложив все в одну строчку как матрешку:
# path_to_json = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'students.json')

app = FastAPI()

# Функция главной страницы
@app.get("/")
def home_page():
    return {"message": "Привет, Главный!"}

# Функция, которая будет возвращать список из всех наших студентов
@app.get("/students")
def get_all_students():
    return json_to_dict_list(path_to_json)
"""
# Параметры пути (path parameters) включены в сам маршрут URL и используются для идентификации ресурса
@app.get("/students/{course}")
def get_all_students_course(course: int):
    students = json_to_dict_list(path_to_json)
    return_list = []
    for student in students:
        if student["course"] == course:
            return_list.append(student)
    return return_list

# Параметры запроса , то что после ?
@app.get("/students")
def get_all_students(course: Optional[int] = None):
    students = json_to_dict_list(path_to_json)
    if course is None:
        return students
    else:
        return_list = []
        for student in students:
            if student["course"] == course:
                return_list.append(student)
        return return_list
"""

@app.get("/students/{course}")
def get_all_students_course(course: int = None, major: Optional[str] = None, enrollment_year: Optional[int] = None):
    students = json_to_dict_list(path_to_json)
    filtered_students = []
    for student in students:
        if student["course"] == course:
            filtered_students.append(student)

    if major:
        filtered_students = [student for student in filtered_students if student['major'].lower() == major.lower()]

    if enrollment_year:
        filtered_students = [student for student in filtered_students if student['enrollment_year'] == enrollment_year]

    return filtered_students

# Параметры пути (path parameters) включены в сам маршрут URL и используются для идентификации ресурса
@app.get("/student/{student_id}")
def get_all_students_course(student_id: int):
    students = json_to_dict_list(path_to_json)
    return_list = []
    for student in students:
        if student["student_id"] == student_id:
            return_list.append(student)
    return return_list

# Параметры запроса , то что после ?
"""@app.get("/student")
def get_all_students(student_id: Optional[int] = None):
    students = json_to_dict_list(path_to_json)
    if student_id is None:
        return students
    else:
        return_list = []
        for student in students:
            if student["student_id"] == student_id:
                return_list.append(student)
        return return_list
    """
@app.get("/student")
def get_student_from_param_id(student_id: int) -> SStudent:
    students = json_to_dict_list(path_to_json)
    for student in students:
        if student["student_id"] == student_id:
            return student