from datetime import datetime
from typing import Optional
import re
from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationError, ConfigDict, model_validator
from app.utils.phone_parser import PhoneParser


# class SUser(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
# Базовая схема пользователя
class SUserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_phone: str = Field(..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя пользователя, от 3 до 50 символов")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия пользователя, от 3 до 50 символов")
    user_nick: Optional[str] = Field(..., min_length=3, max_length=50, description="Ник пользователя, от 3 до 50 символов")
    # user_pass: str = Field(..., min_length=5, max_length=50, description="Пароль пользователя, от 5 до 50 символов")
    user_email: EmailStr = Field(..., description="Электронная почта пользователя")
    two_fa_auth: int = Field(0, ge=0, le=1)
    email_verified: int = Field(0, ge=0, le=1)
    phone_verified: int = Field(0, ge=0, le=1)
    user_status: Optional[int] = Field(None, ge=0, description="юридический статус пользователя")

    role_id: int = Field(..., ge=1, description="ID роли пользователя")
    role: Optional[str] = Field(..., description="Название роли")
    tg_chat_id: Optional[str] = Field(None, max_length=25, description="ID telegram_chata не более 25 символов")
    special_notes: Optional[str] = Field(None, max_length=500, description="Дополнительные заметки, не более 500 символов")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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
    
# Схема для роли
class RoleResponse(BaseModel):
    id: int
    role_name: str

    model_config = ConfigDict(from_attributes=True)

# Полная схема пользователя для ответа
class SUserResponse(SUserBase):
    role: Optional[RoleResponse] = None

# Схема для списка пользователей
class SUserListResponse(BaseModel):
    users: list[SUserResponse]
    total: int

class SUserRegister(BaseModel):
    user_phone: str = Field(..., description="Номер телефона в международном формате, начинающийся с '+'")
    user_email: EmailStr = Field(..., description="Электронная почта пользователя")
    user_pass: str = Field(..., min_length=5, max_length=50, description="Пароль пользователя, от 5 до 50 символов")
    user_pass_check: str = Field(..., min_length=5, max_length=50, description="Подтверждение пароля")
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")
    user_nick: Optional[str] = Field(None, min_length=3, max_length=50, description="Ник пользователя, от 3 до 50 символов. Если не указан, будет сгенерирован автоматически")
    role_id: Optional[int] = Field(4, description="ID роли пользователя")

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

    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Проверяет, что пароли совпадают"""
        if self.user_pass != self.user_pass_check:
            raise ValueError('Пароли не совпадают')
        return self

    @field_validator("user_phone")
    def validate_user_phone(cls, value):
        if not re.match(r'^\+\d{10,11}$', value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 10 до 11 цифр')
        return value

    @field_validator("user_nick")
    def validate_user_nick(cls, value):
        if value is not None:
            if not re.match(r'^[a-zA-Z0-9_]{3,50}$', value):
                raise ValueError('Никнейм может содержать только латинские буквы, цифры и подчеркивания, от 3 до 50 символов')
        return value

class SUserAuth(BaseModel):
    user_email: EmailStr = Field(..., description="Электронная почта")
    user_pass: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")

class SUserAdd(BaseModel):
    user_phone: str = Field(..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя пользователя, от 3 до 50 символов")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия пользователя, от 3 до 50 символов")
    user_nick: str = Field(..., min_length=3, max_length=50, description="Ник пользователя, от 3 до 50 символов")
    user_pass: str = Field(..., min_length=5, max_length=50, description="Пароль пользователя, от 5 до 50 символов")
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

class SUserEmailRequest(BaseModel):
    user_email: EmailStr = Field(..., description="Электронная почта пользователя")

class SUserByEmailResponse(BaseModel):
    id: int
    user_phone: str = Field(..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")
    user_nick: Optional[str] = Field(..., description="Ник пользователя")
    user_email: EmailStr = Field(..., description="Электронная почта пользователя")
    two_fa_auth: int = Field(0, ge=0, le=1)
    email_verified: int = Field(0, ge=0, le=1)
    phone_verified: int = Field(0, ge=0, le=1)
    user_status: Optional[int] = Field(None, description="Статус пользователя")
    role_id: int = Field(..., description="ID роли пользователя")
    tg_chat_id: Optional[str] = Field(None, description="ID telegram чата")
    special_notes: Optional[str] = Field(None, description="Дополнительные заметки")
    role: Optional[RoleResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

'''Схема для изменения роли'''

class SUserUpdateRole(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    new_role_id: int = Field(..., ge=1, description="Новый ID роли пользователя")

class SUserUpdateRoleResponse(BaseModel):
    message: str
    user_id: int
    old_role_id: int
    new_role_id: int
    user_email: str
    role_name: str

class SUserUpdateRoleByEmail(BaseModel):
    user_email: EmailStr = Field(..., description="Email пользователя")
    new_role_id: int = Field(..., ge=1, description="Новый ID роли пользователя")

class SUserRoleInfo(BaseModel):
    id: int
    user_email: str
    first_name: str
    last_name: str
    current_role_id: int
    current_role_name: str
    new_role_id: int
    new_role_name: str

    model_config = ConfigDict(from_attributes=True)

class SUserLogBase(BaseModel):
    action_type: str = Field(..., description="Тип действия")
    old_value: Optional[str] = Field(None, description="Старое значение")
    new_value: Optional[str] = Field(None, description="Новое значение")
    description: Optional[str] = Field(None, description="Описание действия")

class SUserLogCreate(SUserLogBase):
    user_id: int = Field(..., description="ID пользователя")
    changed_by: int = Field(..., description="ID пользователя, который внес изменение")

class SUserLogResponse(SUserLogBase):
    id: int
    user_id: int
    changed_by: int
    created_at: datetime
    user_email: Optional[str] = None
    changer_email: Optional[str] = None
    user_name: Optional[str] = None
    changer_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SUserLogsList(BaseModel):
    logs: list[SUserLogResponse]
    total: int

class SRoleChangeLog(BaseModel):
    id: int
    user_id: int
    user_email: str
    user_name: str
    old_role: str
    new_role: str
    changed_by: str
    changer_email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)