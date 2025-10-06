from fastapi import APIRouter, Depends
from app.roles.dao import RolesDAO
from app.roles.schemas import SRolesAdd, SRolesUpdDesc

router = APIRouter(prefix='/roles', tags=['Работа с ролями'])

    
@router.post("/add/")
async def register_user(role: SRolesAdd) -> dict:
    check = await RolesDAO.add(**role.model_dump())
    if check:
        return {"message": "Роль успешно добавлена!", "role": role}
    else:
        return {"message": "Ошибка при добавлении роли!"}
    
@router.put("/update_description/")
async def update_major_description(role: SRolesUpdDesc) -> dict:
    check = await RolesDAO.update(filter_by={'role_name': role.role_name},
                                   role_description=role.role_description)
    if check:
        return {"message": "Роль успешно обновлена!", "role": role}
    else:
        return {"message": "Ошибка при обновления роли!"}