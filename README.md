## Создание собственного API на Python (FastAPI) 
(повторение туториалов от [Yakovenko Oleksii](https://github.com/Yakvenalex))
1. [Создание собственного API на Python (FastAPI): Знакомство и первые функции](https://habr.com/ru/companies/amvera/articles/826196/)
2. [Создание собственного API на Python (FastAPI): Гайд по POST, PUT, DELETE запросам и моделям Pydantic](https://habr.com/ru/articles/827134/)

### Знакомство и первые функции
#### Установка зависимостей

```
pip install -r requirements.txt
```
Файл **app/auth/utils.py** - 
Пишем 2 простые функции. Первая **принимает список питоновских словарей**, создавая JSON файл. А вторая – **трансформирует JSON файл в список питоновских словарей**. 
Далее мы просто импортируем эту функцию в приложение FastApi

Пишем приложение (файл **app/main.py**):
- пропишем путь к JSON файлу и сохраним в переменной
- Создадим наше первое приложение:
```
app = FastAPI()
```
- Напишем функцию для главной страницы, ```@app.get("/") def home_page()```
- Напишем функцию, которая будет возвращать список из всех наших студентов ```@app.get("/students") def get_all_students()```
- Напишем функцию с параметрами пути для вывода студентов по курсу ```@app.get("/students/{course}") def get_all_students_course()```
- Добавим функцию с параметрами пути (path parameters) для идентификации ресурса (id студента) ```@app.get("/student/{student_id}") def get_all_students_course()```
- Добавим функцию с комбинированием параметров пути (курса) и запросов (специальность (major) и год 
поступления (enrollment_year)) ```@app.get("/students/{course}") def get_all_students_course()```

### Гайд по POST, PUT, DELETE запросам и моделям Pydantic

Во второй статье в качестве исходных данных создадим новый файл **students.json**
и перепишем в него из GitHub-а новые записи студентов с скорректированными параметрами. 
Для этого откроем коммиты проекта Туториала Алексея с коммитом "обновленный код под вторую статью".

Создадим  файл **app/auth/models.py**
- *Импорты*:

```python
from enum import Enum # для создания перечислений (enums).
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError # Pydantic используется для создания моделей данных и валидации.
from datetime import date, datetime # для работы с датами.
from typing import Optional # для указания необязательных полей.
import re # для использования регулярных выражений.
```
- Создадим класс перечисления валидных курсов ```class Major(str, Enum)```
- Создадим класс - модель **SStudent()** с описанием полей(field) и внутренними валидаторами.

```python
class SStudent(BaseModel): # Pydantic-схема, SS - дополнительная S говорит о том что добавил схему(модель)
```
#### Внтуренние валидаторы полей в Pydantic

**ge:** Это сокращение от "greater than or equal" (больше или равно). Используется для установки минимального допустимого значения для числового поля. Если значение поля меньше указанного, будет вызвано исключение валидации.

**le:** Это сокращение от "less than or equal" (меньше или равно). Используется для установки максимального допустимого значения для числового поля. Если значение поля больше указанного, также будет вызвано исключение валидации.

**min_lenght**: описываем минимальную длину строки

**max_lenght**: описываем максимальную длину строки

**gt, ge, lt, le**: Ограничения для числовых значений (больше, больше или равно, меньше, меньше или равно).

**multiple_of**: Число, на которое значение должно быть кратно.

**max_digits, decimal_places**: Ограничения для чисел с плавающей точкой (максимальное количество цифр, количество десятичных знаков)

**title**: Заголовок поля. Используется для документации или автоматической генерации API.

**examples**: Примеры значений для поля. Используются для документации и обучения.

Подробнее в документации [Pydantic](https://docs.pydantic.dev/).

Добавим внутренний валидатор для номера телефона: ```@field_validator("phone_number") @classmethod def validate_phone_number(cls, values: str)```

Добавим валидатор для даты рождения: ``` @field_validator("date_of_birth") @classmethod def validate_date_of_birth(cls, values: date)```

#### Pydantic модель и GET эндпоинт

Передалем модель ответа ```@app.get("/student")``` в **app/main.py** используя в качестве *response_model* (модель ответа) схему **SStudent**

```python
@app.get("/student")
def get_student_from_param_id(student_id: int) -> SStudent:
    students = json_to_dict_list(path_to_json)
    for student in students:
        if student["student_id"] == student_id:
            return student
```
Теперь, если информация о студенте, представленная в students.json не будет проходить валидацию,
мы получим ошибку сервера с расшифровкой ошибки (ожидалось - получили).

Изменим модель ответа ```@app.get("/students/{course}")``` в **app/main.py**  для списка студентов. Из модуля typing передаем List  и далее модель, говоря тем самым , что этот метод должен вернуть список студентов. и добавим ```request_body``` в обработчик параметров **course, major, enrollment_year**

```py
def get_all_students_course(course: int, major: Optional[str] = None, enrollment_year: Optional[int] = None) -> List[
    SStudent]
    ...
```

Оптимизируем передачу запросов аргументов (фильтров ) в адресе ссылки через создание класса с определением наших фильтров:

```py
class RBStudent:
    def __init__(self, course: int, major: Optional[str] = None, enrollment_year: Optional[int] = None):
        self.course: int = course
        self.major: Optional[str] = major
        self.enrollment_year: Optional[int] = enrollment_year
```

и передадим этот класс в наш эндпоинт, где выводим список студентов воспользоваться функцией Depends для обхода ошибки валидации поля ответа нашего класса ```app.main.RBStudent```:
```py
def get_all_students_course(request_body: RBStudent = Depends()) -> List[SStudent]:
    students = json_to_dict_list(path_to_json)
    ...
```

#### POST метод в FastApi

Для дальнейшего изучения установим библиотеку json_db_lite и трансформируем наш JSON-файл со списком студентов в мини-базу.
```sh
pip install --upgrade json_db_lite
```
Смысл **POST** методов в том, чтоб отправить данные от клиента на сервер (базу данных). В качестве примера добавим нового студента в базу данных.

Для начала напишем функции, которые позволят нам имитировать работу с базой данных, изменим файл **app/auth/utils.py**
