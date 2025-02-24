from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
from datetime import date, datetime
from typing import Optional
import re

class RBStudent: # Создали класс для оптимизации передачи аргументов в запросе и передадим его в эндпоинт
    def __init__(self, course: int, major: Optional[str] = None, enrollment_year: Optional[int] = None):
        self.course: int = course
        self.major: Optional[str] = major
        self.enrollment_year: Optional[int] = enrollment_year

class Major(str, Enum):         # задаем перечисление существующих факультетов через enum и получаем  
    informatics = "Информатика" # дополнительные возможности перечисления,такие как ограничение набора 
    economics = "Экономика"     # возможных значений и удобные методы для работы с этими значениями.
    law = "Право"
    medicine = "Медицина"
    engineering = "Инженерия"
    languages = "Языки"
    mathimatics = "Математика"
    ecology = "Экология"
    history = "История"
    sycology = "Психология"

class SStudent(BaseModel): # Pydantic-схема, SS - дополнительная S говорит о том что добавил схему(модель)
    student_id: int
    phone_number: str = Field(default=..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(default=..., min_length=1, max_length=50, description="Имя студента, от 1 до 50 символов")
    last_name: str = Field(default=..., min_length=1, max_length=50, description="Фамилия студента, от 1 до 50 символов")
    date_of_birth: date = Field(default=..., description="Дата рождения студента в формате ГГГГ-ММ-ДД")
    email: EmailStr = Field(default=..., description="Электронная почта студента")
    address: str = Field(default=..., min_length=10, max_length=200, description="Адрес студента, не более 200 символов")
    enrollment_year: int = Field(default=..., ge=2002, description="Год поступления должен быть не меньше 2002")
    major: Major = Field(default=..., description="Специальность студента")
    course: int = Field(default=..., ge=1, le=5, description="Курс должен быть в диапазоне от 1 до 5")
    special_notes: Optional[str] = Field(default=None, max_length=500,
                                         description="Дополнительные заметки, не более 500 символов")

    @field_validator("phone_number")   # Валидатор вводимого номера телефона
    @classmethod                       # Проверяет, что номер телефона начинается с "+" и содержит от 10 до 11 цифр.
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r'^\+\d{10,11}$', values): # Используем регулярное выражение
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 10 до 11 цифр')
        return values

    @field_validator("date_of_birth") # Валидатор дня рождения (введенный др должен быть в прошлом)
    @classmethod
    def validate_date_of_birth(cls, values: date):
        if values and values >= datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return values
