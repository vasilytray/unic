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
    user_status: Optional[int] = Field(None, ge=0, description="статус пользователя")

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
    def generate_user_nick(self):
        """Автоматически генерирует никнейм, если он не указан"""
        if not self.user_nick:
            self.user_nick = self._create_user_nick(self.first_name, self.last_name)
        
        # Проверяем длину сгенерированного ника
        if len(self.user_nick) < 3:
            # Если сгенерированный ник слишком короткий, добавляем префикс
            self.user_nick = f"user_{self.user_nick}"
        
        # Установка роли по умолчанию
        if self.role_id is None:
            self.role_id = 4  # Роль по умолчанию

        return self

    @staticmethod
    def _create_user_nick(first_name: str, last_name: str) -> str:
        """Создает никнейм из имени и фамилии"""
        # Транслитерация кириллицы в латиницу (базовый вариант)
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
            'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '',
            'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
        
        def transliterate(text: str) -> str:
            """Транслитерирует кириллический текст в латиницу"""
            result = []
            for char in text:
                if char in translit_map:
                    result.append(translit_map[char])
                elif char.isalnum():
                    result.append(char)
                else:
                    result.append('_')
            return ''.join(result)
        
        # Транслитерируем имя и фамилию
        first_latin = transliterate(first_name.lower())
        last_latin = transliterate(last_name.lower())
        
        # Убираем лишние символы и создаем ник
        first_clean = re.sub(r'[^a-z0-9]', '', first_latin)
        last_clean = re.sub(r'[^a-z0-9]', '', last_latin)
        
        # Если после очистки что-то пустое, используем альтернативные варианты
        if not first_clean and not last_clean:
            return f"user_{hash(first_name + last_name) % 10000:04d}"
        elif not first_clean:
            return last_clean[:47] if len(last_clean) > 47 else last_clean
        elif not last_clean:
            return first_clean[:47] if len(first_clean) > 47 else first_clean
        
        # Создаем базовый ник
        base_nick = f"{first_clean}_{last_clean}"
        
        # Обрезаем если слишком длинный
        if len(base_nick) > 50:
            base_nick = base_nick[:50]
        
        return base_nick

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
