from datetime import datetime, date
from typing import Optional
import re
from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationError, ConfigDict, model_validator
from app.utils.phone_parser import PhoneParser


class SUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_phone: str = Field(..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя пользователя, от 1 до 50 символов")
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия пользователя, от 1 до 50 символов")
    user_nick: str = Field(..., min_length=1, max_length=50, description="Ник пользователя, от 1 до 50 символов")
    user_pass: str = Field(..., min_length=1, max_length=50, description="Пароль пользователя, от 1 до 50 символов")
    user_email: EmailStr = Field(..., description="Электронная почта пользователя")
    two_fa_auth: int = Field(..., ge=0, le=1)
    email_verified: int = Field(..., ge=0, le=1)
    phone_verified: int = Field(..., ge=0, le=1)
    user_status: int = Field(..., ge=0, description="статус пользователя")

    role_id: int = Field(..., ge=1, description="ID роли пользователя")
    role: Optional[str] = Field(..., description="Название роли")
    tg_chat_id: Optional[str] = Field(None, max_length=25, description="ID telegram_chata не более 25 символов")
    special_notes: Optional[str] = Field(None, max_length=500, description="Дополнительные заметки, не более 500 символов")

    @field_validator("user_phone")
    def validate_user_phone(cls, value):
        if not re.match(r'^\+\d{10,11}$', value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 10 до 11 цифр')
        return value

    #@field_validator("date_of_birth")
    #def validate_date_of_birth(cls, value):
    #    if value and value >= datetime.now().date():
    #        raise ValueError('Дата рождения должна быть в прошлом')
    #    return value

class SUserAdd(BaseModel):
    user_phone: str = Field(..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя пользователя, от 1 до 50 символов")
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия пользователя, от 1 до 50 символов")
    user_nick: str = Field(..., min_length=1, max_length=50, description="Ник пользователя, от 1 до 50 символов")
    user_pass: str = Field(..., min_length=1, max_length=50, description="Пароль пользователя, от 1 до 50 символов")
    user_email: EmailStr = Field(..., description="Электронная почта пользователя")
    two_fa_auth: int = Field(0, ge=0, le=1)
    role_id: int = Field(4, ge=1, description="ID роли пользователя")

    special_notes: Optional[str] = Field(None, max_length=500, description="Дополнительные заметки, не более 500 символов")

    @model_validator(mode='before')
    @classmethod
    def normalize_user_phone(cls, data):
        """Нормализует номер телефона перед валидацией"""
        if isinstance(data, dict) and 'user_phone' in data:
            phone = data['user_phone']
            if phone:
                normalized = PhoneParser.normalize_phone(phone)
                if not normalized:
                    raise ValueError('Неверный формат номера телефона')
                
                data['user_phone'] = normalized
        
        return data
    
    @field_validator("user_phone")
    def validate_user_phone(cls, value):
        if not re.match(r'^\+\d{10,11}$', value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 10 до 11 цифр')
        return value
