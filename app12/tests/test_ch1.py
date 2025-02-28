import httpx
from app.auth.models import Student
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError


def get_all_students():
    url = "http://127.0.0.1:8005/students"
    response = requests.get(url)
    return response.json()

"""
students = get_all_students()
for i in students:
    print(i)

# выполним запрос с параметром запроса 
def get_students_with_param_requests(major: str):
    url = "http://127.0.0.1:8005/students/3"
    response = requests.get(url, params={"major": major})
    return response.json()


students = get_students_with_param_requests(major="Экология")
for student in students:
    print(student)

# получим всех студентов второго курса, используя параметр пути
def get_students_with_param_path(course: int):
    url = f"http://127.0.0.1:8005/students/{course}"
    response = requests.get(url)
    return response.json()


students = get_students_with_param_path(4)
for student in students:
    print(student)
"""
# Миксуем параметры пути и параметры запроса.

def get_students_with_param_mix(course: int, major: str, enrollment_year: int):
    url = f"http://127.0.0.1:8005/students/{course}"
    response = requests.get(url, params={"major": major, "enrollment_year": enrollment_year})
    return response.json()

def test_valid_student(data: dict) -> None:
    try:
        student = Student(**data)
        print(student)
    except ValidationError as e:
        print(f"Ошибка валидации: {e}")

students = get_students_with_param_mix(2, major=None, enrollment_year=2018)
print(students)