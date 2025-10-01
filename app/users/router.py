from fastapi import APIRouter 
from sqlalchemy import select 
from app.database import async_session_maker 
from app.users.models import User

router = APIRouter(prefix='/users', tags=['Работа с пользователями'])

@router.get("/", summary="Получить список всех пользователей")
async def get_all_students():
    async with async_session_maker() as session: 
        query = select(User)
        result = await session.execute(query)
        users = result.scalars().all()
        return users