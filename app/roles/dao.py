from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.roles.models import Role

class RolesDAO(BaseDAO):
    model = Role

    @classmethod
    async def find_all_with_users_count(cls, **filters) -> list[Role]:
        """Получить все роли с подсчетом пользователей (оптимизированно)"""
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filters)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_name(cls, role_name: str) -> Role | None:
        """Найти роль по имени"""
        return await cls.find_one_or_none(role_name=role_name)

    @classmethod
    async def delete_role_by_name(cls, role_name: str) -> bool:
        """Удалить роль по имени (с проверкой на использование)"""
        async with async_session_maker() as session:
            async with session.begin():
                # Проверяем существует ли роль
                role = await cls.find_by_name(role_name)
                if not role:
                    return False
                
                # Проверяем, есть ли пользователи с этой ролью
                if role.count_users > 0:
                    raise ValueError(f"Невозможно удалить роль '{role_name}'. Есть пользователи с этой ролью.")
                
                # Удаляем роль
                await session.execute(
                    delete(cls.model).where(cls.model.role_name == role_name)
                )
                await session.commit()
                return True

    @classmethod
    async def get_role_stats(cls) -> dict:
        """Получить статистику по ролям"""
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)
            roles = result.scalars().all()
            
            return {
                "total_roles": len(roles),
                "total_users": sum(role.count_users for role in roles),
                "roles": [
                    {
                        "id": role.id,
                        "name": role.role_name,
                        "user_count": role.count_users,
                        "is_admin_role": role.is_admin_role
                    }
                    for role in roles
                ]
            }