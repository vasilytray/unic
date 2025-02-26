# Создание собственного API на Python (FastAPI) 
(повторение туториалов от [Yakovenko Oleksii](https://github.com/Yakvenalex))
1. [Создание собственного API на Python (FastAPI): Знакомство и первые функции](https://habr.com/ru/companies/amvera/articles/826196/)
2. [Создание собственного API на Python (FastAPI): Гайд по POST, PUT, DELETE запросам и моделям Pydantic](https://habr.com/ru/articles/827134/)

## Знакомство и первые функции
### Установка зависимостей

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

## Гайд по POST, PUT, DELETE запросам и моделям Pydantic

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
### Внтуренние валидаторы полей в Pydantic

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

### Pydantic модель и GET эндпоинт

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

### POST метод в FastApi

Для дальнейшего изучения установим библиотеку json_db_lite и трансформируем наш JSON-файл со списком студентов в мини-базу.
```sh
pip install --upgrade json_db_lite
```
Смысл **POST** методов в том, чтоб отправить данные от клиента на сервер (базу данных). В качестве примера добавим нового студента в базу данных.

Для начала напишем функции, которые позволят нам имитировать работу с базой данных, изменим файл **app/auth/utils.py** (предыдущий файл utils.py переименуем в utils_ch1.py - мы его использовали в первой части, оставим для информации)

подробное описание каждого метода этой библиотеки описаны в статье [Новая библиотека для работы с JSON: json_db_lite](https://habr.com/ru/articles/826434/).

Теперь правильно напишем **POST** запрос, который будет принимать данные о студенте для добавления, после будет выполнять проверку их валидности, а затем, если все данные валидные, мы будем добавлять новое значение в нашу мини базу данных (add_student).
```py
@app.post("/add_student")
def add_student_handler(student: SStudent):
    student_dict = student.model_dump() # поскольку dict - depricated, используем madel_dump
    check = add_student(student_dict)
    if check:
        return {"message": "Студент успешно добавлен!"}
    else:
        return {"message": "Ошибка при добавлении студента"}
```
добавим  запрос вместе с импортом ```add_student``` в файл **model.py**
```py
from app.auth.utils import json_to_dict_list, add_student
```
и попробуем добавить нового студента, запустив FastAPI
```json
  {
    "student_id": 11,
    "phone_number": "+7016789",
    "first_name": "Ольга",
    "last_name": "Никитина",
    "date_of_birth": "1999-06-20",
    "email": "olga.nikitina@example.com",
    "address": "г. Томск, ул. Ленина, д. 60, кв. 18",
    "enrollment_year": 2018,
    "major": "Экология",
    "course": 3,
    "special_notes": "Без особых примет"
  }
```
1. первая попытка вернула ошибку с невалидным форматом телефонного номера.
2. сделаем номер валидным и повтрорим попытку добавить пользователя.
Действительно такой пользователь добавился, НО! уже есть такой с таким же ID, **нам необходимо сделать проверку на пользователя!**
Добавим проверку по существующему email:

1. Получаем текущий список студентов с помощью json_to_dict_list()
2. Проходим по всем существующим записям и сравниваем email (с приведением к нижнему регистру)
3. При обнаружении дубликата сразу возвращаем ошибку 400
4. Если дубликатов нет, вызываем add_student() и обрабатываем результат

```py
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
```
проверка по e-mail теперь возвращает ошибку! Поменяем e-mail нового студента и повторим попытку:
в результате получаем ответ:
```json
{
  "message": "Студент успешно добавлен!"
}
```

### Обработка PUT методов в FastAPI

Обратимся в файле app/auth/utils.py к функции обновления данных ```def upd_student(upd_filter: dict, new_data: dict)```

И добавим в файл app/auth/model.py две модели:
```py
# Определение модели для фильтрации данных студента
class SUpdateFilter(BaseModel):
    student_id: int


# Определение модели для новых данных студента
class SStudentUpdate(BaseModel):
    course: int = Field(..., ge=1, le=5, description="Курс должен быть в диапазоне от 1 до 5")
    major: Optional[Major] = Field(..., description="Специальность студента")
```

Теперь добавим в main.py метод ```@app.put("/update_student") def update_student_handler(filter_student: SUpdateFilter, new_data: SStudentUpdate)```
и импортируем из **utils.py** ```upd_student``` и из **models.py** ```SUpdateFilter, SStudentUpdate```

Данный метод будет обновлять данные по конкретному студенту, принимая его ID. 

В новых данных мы должны будем передать курс и специальность студента.

```json
{
  "message": "Информация о студенте успешно обновлена!"
}
```

### Обработка DELETE запросов в FastAPI

В **utils.py** мы записали функцию удаления записи студента ```def dell_student(key: str, value: str)```

Добавим в  **models.py** модель не забыв импортировать из **typing** ```, Any```

```py
class SDeleteFilter(BaseModel):
    key: str
    value: Any
```

И теперь добавим функцию для удаления студента из списка не забыв импортировать ```SDeleteFilter``` из **models.py**
и ```dell_student``` из **utils.py**

```py
@app.delete("/delete_student")
def delete_student_handler(filter_student: SDeleteFilter)
...
```
запускаем и пробуем удалить студента.
обработчик возвращает успех, НО смотрим в JSON и видим, что запись на самом деле не удалена!
Проведем корректировку:


## Структура проекта, SQLAlchemy PostgreSQL, миграции и первые модели таблиц

Создадим новый проект под новую главу, дабы не терять того, что наработано и куда можно подсмотреть

Назову приложение app3 - т.к. это изучаю третью статью цикла
3. [Создание собственного API на Python (FastAPI): Структура проекта, SQLAlchemy PostgreSQL, миграции и первые модели таблиц](https://habr.com/ru/articles/827222/)

Структурируем наш проект:

### Зависимости проекта

- `fastapi[all]==0.115.0` - высокопроизводительный веб-фреймворк
- `pydantic==2.9.2` - валидация данных
- `uvicorn==0.31.0` - ASGI-сервер
- `jinja2==3.1.4` - шаблонизатор
- `SQLAlchemy==2.0.35` - ORM для работы с базами данных
- `aiosqlite==0.20.0` - асинхронная поддержка SQLite
- `alembic==1.13.3` - управление миграциями базы данных
- `loguru==0.7.2` - красивое и удобное логирование

### Структура проекта

Проект построен с учётом модульной архитектуры, что позволяет легко расширять приложение и упрощает его поддержку.
Каждый модуль отвечает за отдельные задачи, такие как авторизация или управление данными.

### Основная структура проекта

```
my_fastapi_project/
├── tests/
│   └── test.py                 # тут мы будем добавлять функции для Pytest
├── app/
│   ├── students/               # Модуль отвечающий за работу с данными студентов
│   │   ├── dao.py              # Data Access Object для работы с БД
│   │   ├── models.py           # Модели данных для авторизации
│   │   ├── router.py           # Роутеры FastAPI для маршрутизации
│   │   └── utils.py            # Вспомогательные функции для авторизации
│   ├── database.py/            # Подключение к базе данных и управление сессиями        
│   ├── migration/              # Миграции базы данных
│   │   ├── versions/           # Файлы миграций Alembic
│   │   ├── env.py              # Настройки среды для Alembic
│   │   ├── README              # Документация по миграциям
│   │   └── script.py.mako      # Шаблон для генерации миграций
│   ├── config.py               # Конфигурация приложения
│   └── main.py                 # Основной файл для запуска приложения
├── data/                       # Папка для хранения файла БД
│   └── db.sqlite3              # Файл базы данных SQLite
├── .env                        # Конфигурация окружения
├── alembic.ini                 # Конфигурация Alembic
├── README.md                   # Документация проекта
└── requirements.txt            # Зависимости проекта
```

### Подготовка
1. Развернем базу данных в PostgreSQL локально в Docker - контейнере.
1.1. Поставим [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2.2. Создадим в корне проекта  файл docker-compose.yml 

```yml
version: '3.9'

services:
  postgres:
    image: postgres:latest
    container_name: postgres_container
    environment:
      POSTGRES_USER: amin
      POSTGRES_PASSWORD: my_super_password
      POSTGRES_DB: fast_api
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "5430:5432"
    volumes:
      - ./pgdata:/var/lib/postgresql/data/pgdata
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    command: >
      postgres -c max_connections=1000
               -c shared_buffers=256MB
               -c effective_cache_size=768MB
               -c maintenance_work_mem=64MB
               -c checkpoint_completion_target=0.7
               -c wal_buffers=16MB
               -c default_statistics_target=100
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U postgres_user -d postgres_db" ]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped
    tty: true
    stdin_open: true

volumes:
  pgdata:
    driver: local
```
#### Краткий обзор Docker Compose файла

1. services/postgres:

**image**: используемая Docker-образ PostgreSQL, в данном случае postgres:latest.

**container_name**: имя контейнера, в котором будет запущен PostgreSQL.

**environment**: переменные окружения для настройки PostgreSQL (пользователь, пароль, имя базы данных - не забудьте указать свои).

**ports**: проброс портов, где "5430:5432" означает, что порт PostgreSQL внутри контейнера (5432) проброшен на порт хоста (5430). Это значит что для подключения к постгрес нужно будет прописывать порт 5430.

**volumes**: монтируем локальный каталог ``./pgdata`` внутрь контейнера для сохранения данных PostgreSQL.

**deploy**: определяет ресурсы и стратегию развертывания для Docker Swarm (необязательно для стандартного использования Docker Compose).

**command**: дополнительные параметры командной строки PostgreSQL для настройки параметров производительности.

**healthcheck**: проверка состояния PostgreSQL с использованием pg_isready.

***restart, tty, stdin_open***: настройки перезапуска контейнера и взаимодействия с ним через терминал.

2. volumes/pgdata:

Определяет том **pgdata**, который используется для постоянного хранения данных PostgreSQL.

#### Запуск PostgreSQL

- Запустим Docker Desktop

- Выполняем команду 

```sh
docker-compose up -d
```

Эта команда запустит контейнер PostgreSQL в фоновом режиме **(-d)** на основе настроек, указанных в файле ``docker-compose.yml``

```sh
docker-compose up -d
time="2025-02-26T19:24:11+07:00" level=warning msg="C:\\www\\pyfapi\\unic\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion"
[+] Running 15/15
 ✔ postgres Pulled                                                                                                                          27.6s 
[+] Running 3/3
 ✔ Network unic_default         Created                                                                                                      0.2s 
 ✔ Volume "unic_pgdata"         Created                                                                                                      0.0s 
 ✔ Container postgres_fast_api  Started
```