from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from app.dao.base import BaseDAO
from app.users.models import User
from app.database import async_session_maker

class UsersDAO(BaseDAO):
    model = User

    @classmethod
    async def find_full_data(cls, user_id: int):
        """Найти пользователя с полными данными (включая роль)"""
        return await cls.find_one_or_none(id=user_id)

    @classmethod
    async def find_all_with_roles(cls, **filter_by):
        """Найти всех пользователей с загруженными ролями"""
        async with async_session_maker() as session:
            query = select(cls.model).options(joinedload(cls.model.role)).filter_by(**filter_by)
            result = await session.execute(query)
            return result.unique().scalars().all()

    @classmethod
    async def find_by_email(cls, user_email: str):
        """Найти пользователя по email"""
        return await cls.find_one_or_none(user_email=user_email)

    @classmethod
    async def find_by_phone(cls, user_phone: str):
        """Найти пользователя по телефону"""
        return await cls.find_one_or_none(user_phone=user_phone)

    @classmethod
    async def add_user(cls, **user_data: dict):
        """Добавить пользователя (возвращает ID)"""
        new_user = await cls.add(**user_data)
        return new_user.id if new_user else None

    @classmethod
    async def delete_user_by_id(cls, user_id: int):
        """Удалить пользователя по ID"""
        result = await cls.delete(id=user_id)
        return result > 0