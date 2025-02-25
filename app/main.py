from fastapi import FastAPI, Depends, HTTPException
from app.auth.utils import json_to_dict_list, add_student, upd_student
from app.auth.models import SStudent, RBStudent, SUpdateFilter, SStudentUpdate
import os
from typing import Optional, List

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

"""# Функция, которая будет возвращать список из всех наших студентов
@app.get("/students")
def get_all_students():
    return json_to_dict_list(path_to_json)

# Параметры пути (path parameters) включены в сам маршрут URL и используются для идентификации ресурса
@app.get("/students/{course}")
def get_all_students_course(course: int):
    students = json_to_dict_list(path_to_json)
    return_list = []
    for student in students:
        if student["course"] == course:
            return_list.append(student)
    return return_list
"""
# Параметры запроса , то что после ?
@app.get("/students")
def get_all_students(course: Optional[int] = None):
    students = json_to_dict_list()
    if course is None:
        return students
    else:
        return_list = []
        for student in students:
            if student["course"] == course:
                return_list.append(student)
        return return_list


@app.get("/students/{course}")
def get_all_students_course(request_body: RBStudent = Depends())->List[SStudent]: 
    # оптимизируем запрос в эндпоинте  позставив класс аргументов для передачи
    students = json_to_dict_list()
    filtered_students = []
    for student in students:
        if student["course"] == request_body.course:
            filtered_students.append(student)

    if request_body.major:
        filtered_students = [student for student in filtered_students if 
                             student['major'].lower() == request_body.major.lower()]

    if request_body.enrollment_year:
        filtered_students = [student for student in filtered_students if 
                             student['enrollment_year'] == request_body.enrollment_year]

    return filtered_students

# Параметры пути (path parameters) включены в сам маршрут URL и используются для идентификации ресурса
@app.get("/student/{student_id}")
def get_all_students_course(student_id: int):
    students = json_to_dict_list()
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
    students = json_to_dict_list()
    for student in students:
        if student["student_id"] == student_id:
            return student
        
@app.post("/add_student")
def add_student_handler(student: SStudent):
    # Получаем список всех студентов для проверки на совпадение email
    students = json_to_dict_list()

    # Проверяем наличие дубликата email
    for existing_student in students:
        if existing_student["email"] == student.email: # .lower() - не используем потому что в Pydantic-схеме
            raise HTTPException(                       # уже автоматически приводится e-mail к нижнему регистру 
                status_code=400,                       # посредством email: EmailStr
                detail="Студент с таким email уже существует"
            )
    # Добавляем студента, если проверка пройдена
    student_dict = student.model_dump()
    check = add_student(student_dict)
    if check:
        return {"message": "Студент успешно добавлен!"}
    else:
        raise HTTPException(
            status_code=400, 
            detail="Ошибка при добавлении студента"
        )

@app.put("/update_student")
def update_student_handler(filter_student: SUpdateFilter, new_data: SStudentUpdate):
    check = upd_student(filter_student.dict(), new_data.dict())
    if check:
        return {"message": "Информация о студенте успешно обновлена!"}
    else:
        raise HTTPException(status_code=400, detail="Ошибка при обновлении информации о студенте")