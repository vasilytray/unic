from sqlalchemy import event, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.dao.base import BaseDAO
from app.users.models import User
from app.roles.models import Role
from app.database import async_session_maker

@event.listens_for(User, 'after_insert')
def receive_after_insert(mapper, connection, target):
    role_id = target.role_id
    connection.execute(
        update(Role)
        .where(Role.id == role_id)
        .values(count_users=Role.count_users + 1)
    )


@event.listens_for(User, 'after_delete')
def receive_after_delete(mapper, connection, target):
    role_id = target.role_id
    connection.execute(
        update(Role)
        .where(Role.id == role_id)
        .values(count_users=Role.count_users - 1)
    )


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def find_full_data(cls, user_id: int):
        async with async_session_maker() as session:
            # Запрос для получения информации о пользователе вместе с информацией о группе
            query_user = select(cls.model).options(joinedload(cls.model.role)).filter_by(id=user_id)
            result_user = await session.execute(query_user)
            user_info = result_user.scalar_one_or_none()

            # Если пользователь не найден, возвращаем None
            if not user_info:
                return None

            user_data = user_info.to_dict()
            user_data['role'] = user_info.role.role_name
            return user_data
        
    @classmethod
    async def add_user(cls, **user_data: dict):
        async with async_session_maker() as session:
            async with session.begin():
                new_user = cls.model(**user_data)
                session.add(new_user)
                await session.flush()
                new_user_id = new_user.id
                await session.commit()
                return new_user_id

    @classmethod
    async def delete_user_by_id(cls, user_id: int):
        async with async_session_maker() as session:
            async with session.begin():
                query = select(cls.model).filter_by(id=user_id)
                result = await session.execute(query)
                user_to_delete = result.scalar_one_or_none()

                if not user_to_delete:
                    return None
                
                # Delete the user
                await session.execute(
                    delete(cls.model).filter_by(id=user_id)
                )

                await session.commit()
                return user_id