import requests

def get_students_with_param_requests(course: int):
    url = "http://127.0.0.1:8005/students"
    response = requests.get(url, params={"course": course})
    return response.json()


students = get_students_with_param_requests(course=2)
for student in students:
    print(student)