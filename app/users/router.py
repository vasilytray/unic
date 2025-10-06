from fastapi import APIRouter, Depends
from app.users.dao import UserDAO
from app.users.rb import RBUser
from app.users.schemas import SUser, SUserAdd

router = APIRouter(prefix='/users', tags=['Работа с пользователями'])

@router.get("/", summary="Получить список всех пользователей")
async def get_all_users(request_body: RBUser = Depends()) -> list[SUser]:
    return await UserDAO.find_all(**request_body.to_dict())
    
@router.get("/{id}", summary="Получить одного пользователя по id")
async def get_user_by_id(user_id: int) -> SUser | dict:
    rez = await UserDAO.find_full_data(user_id)
    if rez is None:
        return {'message': f'Пользователь с ID {user_id} не найден!'}
    return rez

@router.post("/add/")
async def add_user(user: SUserAdd) -> dict:
    check = await UserDAO.add_user(**user.dict())
    if check:
        return {"message": "Студент успешно добавлен!", "user": user}
    else:
        return {"message": "Ошибка при добавлении студента!"}


@router.delete("/dell/{user_id}")
async def dell_user_by_id(user_id: int) -> dict:
    check = await UserDAO.delete_user_by_id(user_id=user_id)
    if check:
        return {"message": f"Студент с ID {user_id} удален!"}
    else:
        return {"message": "Ошибка при удалении студента!"}