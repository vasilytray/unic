from fastapi import APIRouter, Depends
from app.roles.dao import RolesDAO
from app.roles.schemas import SRolesAdd, SRolesUpdDesc, SRoles
from app.roles.models import Role
from app.users.dependencies import get_current_user, get_current_admin, get_current_moderator, get_current_superadmin

router = APIRouter(prefix='/roles', tags=['Работа с ролями'])

@router.get("/", summary="Список Ролей")
async def get_all_roles(request_body: Role = Depends(get_current_admin)) -> list[SRoles]:
    return await RolesDAO.find_all(**request_body.to_dict())
    
@router.post("/add/")
async def add_role(role: SRolesAdd) -> dict:
    check = await RolesDAO.add(**role.model_dump())
    if check:
        return {"message": "Роль успешно добавлена!", "role": role}
    else:
        return {"message": "Ошибка при добавлении роли!"}
    
@router.put("/update_description/")
async def update_role_description(role: SRolesUpdDesc) -> dict:
    check = await RolesDAO.update(filter_by={'role_name': role.role_name},
                                   role_description=role.role_description)
    if check:
        return {"message": "Роль успешно обновлена!", "role": role}
    else:
        return {"message": "Ошибка при обновления роли!"}