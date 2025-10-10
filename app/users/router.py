from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import Optional
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UsersDAO, UserLogsDAO
from app.roles.dao import RolesDAO
from app.users.rb import RBUser
from app.users.models import User
from app.users.schemas import SUserBase, SUserAdd, SUserResponse, SUserListResponse, SUserAuth
from app.users.schemas import SUserRegister, SUserByEmailResponse
from app.users.schemas import SUserUpdateRole, SUserUpdateRoleResponse, SUserUpdateRoleByEmail, SUserRoleInfo
from app.users.schemas import SUserLogResponse, SUserLogsList, SRoleChangeLog
from app.users.dependencies import get_current_user, get_current_admin, get_current_moderator, get_current_super_admin, validate_role_change, log_role_change

router = APIRouter(prefix='/users', tags=['Работа с пользователями'])

@router.post("/register/")
async def register_user(user_data: SUserRegister) -> dict:
    # Проверяем существование пользователя по email
    user_by_email = await UsersDAO.find_by_email(user_data.user_email)
    if user_by_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь с таким email уже существует'
        )
    
    # Проверяем существование пользователя по телефону
    user_by_phone = await UsersDAO.find_by_phone(user_data.user_phone)
    if user_by_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь с таким телефоном уже существует'
        )

    user_dict = user_data.model_dump()
    user_dict['user_pass'] = get_password_hash(user_data.user_pass)
    await UsersDAO.add_user(**user_dict)
    return {'message': 'Вы успешно зарегистрированы!'}

@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth):
    check = await authenticate_user(user_email=user_data.user_email, user_pass=user_data.user_pass)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверно указаны почта или пароль')
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'access_token': access_token, 'refresh_token': None}

@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data

@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}

@router.get("/", summary="Получить список всех пользователей", response_model=SUserListResponse)
async def get_all_users(
    current_user: User = Depends(get_current_admin),
    request_body: RBUser = Depends()
    ) -> SUserListResponse:
    # Используем метод с загрузкой ролей
    users = await UsersDAO.find_all_with_roles(**request_body.to_dict())
    
    # Преобразуем пользователей в схему ответа
    user_responses = []
    for user in users:
        user_response = SUserResponse(
            id=user.id,
            user_phone=user.user_phone,
            first_name=user.first_name,
            last_name=user.last_name,
            user_nick=user.user_nick,
            user_email=user.user_email,
            user_status=user.user_status,
            role_id=user.role_id,
            special_notes=user.special_notes,
            role=user.role  # объект Role автоматически преобразуется в RoleResponse
        )
        user_responses.append(user_response)
    
    return SUserListResponse(users=user_responses, total=len(user_responses))

@router.get("/all_users/")
async def get_all_users(user_data: User = Depends(get_current_super_admin)):
    return await UsersDAO.find_all()

@router.get("/all_users/")
async def get_all_users(user_data: User = Depends(get_current_super_admin)):
    return await UsersDAO.find_all()

@router.get("/{user_id}", summary="Получить одного пользователя по id", response_model=SUserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_moderator)
    ) -> SUserResponse:
    user_data = await UsersDAO.find_full_data(user_id)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Пользователь с ID {user_id} не найден!'
        )
    
    # return SUserResponse(**user_data)
    return SUserResponse.model_validate(user_data)

@router.get("/by-email/", 
           summary="Получить пользователя по email", 
           response_model=SUserByEmailResponse)
async def get_user_by_email(
    email: str,
    current_user: User = Depends(get_current_user)
) -> SUserByEmailResponse:
    """
    Получить информацию о пользователе по email.
    
    Правила доступа:
    - Админы и суперадмины: могут видеть любого пользователя
    - Обычные пользователи: могут видеть только свою информацию
    """
    # Проверяем права доступа
    if current_user.role_id not in [1, 2] and current_user.user_email != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете просматривать только свою информацию"
        )
    
    user_data = await UsersDAO.find_by_email_with_role(email)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Пользователь с email {email} не найден!'
        )
    
    return SUserByEmailResponse.model_validate(user_data)


@router.post("/add/")
async def add_user(
    user: SUserAdd,
    current_user: User = Depends(get_current_admin)
    ) -> dict:
    """Добавить пользователя (только для админов)"""
    # Проверяем уникальность email и телефона
    # existing_user = await UsersDAO.find_one_or_none(user_email=user.user_email)
    existing_user = await UsersDAO.find_by_email(user.user_email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь с таким email уже существует'
        )
    
    # existing_user = await UsersDAO.find_one_or_none(user_phone=user.user_phone)
    existing_user = await UsersDAO.find_by_phone(user.user_phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь с таким телефоном уже существует'
        )

    user_data = user.model_dump()
    user_data['user_pass'] = get_password_hash(user_data['user_pass'])
    
    user_id = await UsersDAO.add_user(**user_data)
    if user_id:
        return {"message": "Пользователь успешно добавлен!", "user_id": user_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при добавлении пользователя!"
        )
    
@router.put("/update-role/", 
           summary="Изменить роль пользователя по ID", 
           response_model=SUserUpdateRoleResponse)
async def update_user_role(
    role_data: SUserUpdateRole,
    super_admin: User = Depends(get_current_super_admin)
) -> SUserUpdateRoleResponse:
    """
    Изменить роль пользователя по ID (только для суперадминистратора).
    """
    # Валидация изменения роли
    target_user = await validate_role_change(super_admin, role_data.user_id, role_data.new_role_id)
    
    # Проверяем существование новой роли
    new_role = await RolesDAO.find_by_id(role_data.new_role_id)
    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Роль с ID {role_data.new_role_id} не найдена"
        )
    
    # Сохраняем старую роль
    old_role_id = target_user.role_id
    old_role_name = await RolesDAO.get_role_name_by_id(old_role_id)
    
    # Обновляем роль (используем обновленный метод с счетчиками)
    success = await UsersDAO.update_user_role(role_data.user_id, role_data.new_role_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении роли пользователя"
        )
    
    # Логируем изменение роли
    await log_role_change(
        user_id=role_data.user_id,
        old_role_id=old_role_id,
        new_role_id=role_data.new_role_id,
        changed_by=super_admin.id,
        description=f"Роль изменена суперадминистратором {super_admin.user_email}"
    )
    
    return SUserUpdateRoleResponse(
        message="Роль пользователя успешно обновлена",
        user_id=role_data.user_id,
        old_role_id=old_role_id,
        new_role_id=role_data.new_role_id,
        user_email=target_user.user_email,
        role_name=new_role.role_name
    )

@router.put("/update-role-by-email/", 
           summary="Изменить роль пользователя по email", 
           response_model=SUserUpdateRoleResponse)
async def update_user_role_by_email(
    role_data: SUserUpdateRoleByEmail,
    super_admin: User = Depends(get_current_super_admin)
) -> SUserUpdateRoleResponse:
    """
    Изменить роль пользователя по email (только для суперадминистратора).
    """
    # Находим пользователя по email
    target_user = await UsersDAO.find_by_email_with_role(role_data.user_email)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с email {role_data.user_email} не найден"
        )
    
    # Валидация изменения роли
    await validate_role_change(super_admin, target_user.id, role_data.new_role_id)
    
    # Проверяем существование новой роли
    new_role = await RolesDAO.find_by_id(role_data.new_role_id)
    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Роль с ID {role_data.new_role_id} не найдена"
        )
    
    # Сохраняем старую роль
    old_role_id = target_user.role_id
    old_role_name = await RolesDAO.get_role_name_by_id(old_role_id)
    
    # Обновляем роль
    success = await UsersDAO.update_user_role_by_email(role_data.user_email, role_data.new_role_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении роли пользователя"
        )
    
    # Логируем изменение роли
    await log_role_change(
        user_id=target_user.id,
        old_role_id=old_role_id,
        new_role_id=role_data.new_role_id,
        changed_by=super_admin.id,
        description=f"Роль изменена по email суперадминистратором {super_admin.user_email}"
    )
    
    return SUserUpdateRoleResponse(
        message="Роль пользователя успешно обновлена",
        user_id=target_user.id,
        old_role_id=old_role_id,
        new_role_id=role_data.new_role_id,
        user_email=target_user.user_email,
        role_name=new_role.role_name
    )

# Новые роутеры для работы с логами
@router.get("/logs/", 
           summary="Получить логи пользователей", 
           response_model=SUserLogsList)
async def get_users_logs(
    user_id: Optional[int] = None,
    action_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    admin_user: User = Depends(get_current_super_admin)
) -> SUserLogsList:
    """
    Получить логи пользователей (только для администраторов).
    """
    # Собираем фильтры
    filters = {}
    if user_id:
        filters['user_id'] = user_id
    if action_type:
        filters['action_type'] = action_type
    
    # Получаем логи с помощью BaseDAO
    logs = await UserLogsDAO.find_all(**filters)
    
    # Сортируем и ограничиваем результат (так как BaseDAO не поддерживает сортировку и пагинацию напрямую)
    sorted_logs = sorted(logs, key=lambda x: x.created_at, reverse=True)
    paginated_logs = sorted_logs[offset:offset + limit]
    
    # Преобразуем в схему ответа
    log_responses = []
    for log in paginated_logs:
        # Получаем связанные данные пользователей
        user = await UsersDAO.find_one_or_none_by_id(log.user_id) if log.user_id else None
        changer = await UsersDAO.find_one_or_none_by_id(log.changed_by) if log.changed_by else None
        
        log_response = SUserLogResponse(
            id=log.id,
            user_id=log.user_id,
            changed_by=log.changed_by,
            action_type=log.action_type,
            old_value=log.old_value,
            new_value=log.new_value,
            description=log.description,
            created_at=log.created_at,
            user_email=user.user_email if user else None,
            changer_email=changer.user_email if changer else None,
            user_name=f"{user.first_name} {user.last_name}" if user else None,
            changer_name=f"{changer.first_name} {changer.last_name}" if changer else None
        )
        log_responses.append(log_response)
    
    return SUserLogsList(logs=log_responses, total=len(sorted_logs))

@router.get("/logs/role-changes/", 
           summary="Получить логи изменений ролей", 
           response_model=list[SRoleChangeLog])
async def get_role_change_logs(
    user_id: Optional[int] = None,
    days: int = 30,
    admin_user: User = Depends(get_current_super_admin)
) -> list[SRoleChangeLog]:
    """
    Получить логи изменений ролей (только для администраторов).
    """
    logs = await UserLogsDAO.get_recent_role_changes(days=days)
    
    # Если нужна фильтрация по конкретному пользователю
    if user_id:
        logs = [log for log in logs if log.user_id == user_id]
    
    role_change_logs = []
    for log in logs:
        if log.action_type == 'role_change':
            # Парсим old_value и new_value
            old_role_info = log.old_value.split(':') if log.old_value else ['', '', '']
            new_role_info = log.new_value.split(':') if log.new_value else ['', '', '']
            
            role_change_log = SRoleChangeLog(
                id=log.id,
                user_id=log.user_id,
                user_email=log.user.user_email if log.user else "Unknown",
                user_name=f"{log.user.first_name} {log.user.last_name}" if log.user else "Unknown User",
                old_role=old_role_info[2] if len(old_role_info) > 2 else "Unknown",
                new_role=new_role_info[2] if len(new_role_info) > 2 else "Unknown",
                changed_by=f"{log.changer.first_name} {log.changer.last_name}" if log.changer else "Unknown",
                changer_email=log.changer.user_email if log.changer else "Unknown",
                created_at=log.created_at
            )
            role_change_logs.append(role_change_log)
    
    return role_change_logs

@router.get("/{user_id}/logs/", 
           summary="Получить логи конкретного пользователя", 
           response_model=SUserLogsList)
async def get_user_logs(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    admin_user: User = Depends(get_current_super_admin)
) -> SUserLogsList:
    """
    Получить логи конкретного пользователя (только для администраторов).
    """
    logs = await UserLogsDAO.get_user_logs(user_id, limit=limit, offset=offset)
    
    log_responses = []
    for log in logs:
        log_response = SUserLogResponse(
            id=log.id,
            user_id=log.user_id,
            changed_by=log.changed_by,
            action_type=log.action_type,
            old_value=log.old_value,
            new_value=log.new_value,
            description=log.description,
            created_at=log.created_at,
            user_email=log.user.user_email if log.user else None,
            changer_email=log.changer.user_email if log.changer else None,
            user_name=f"{log.user.first_name} {log.user.last_name}" if log.user else None,
            changer_name=f"{log.changer.first_name} {log.changer.last_name}" if log.changer else None
        )
        log_responses.append(log_response)
    
    return SUserLogsList(logs=log_responses, total=len(log_responses))

@router.get("/available-roles/", 
           summary="Получить список доступных ролей для назначения")
async def get_available_roles(
    super_admin: User = Depends(get_current_super_admin)
) -> list[dict]:
    """
    Получить список ролей, которые можно назначать пользователям.
    Исключает роль суперадминистратора.
    """
    roles = await RolesDAO.get_available_roles(exclude_super_admin=True)
    return [
        {
            "id": role.id,
            "name": role.role_name,
            "description": role.role_description,
            "user_count": role.count_users
        }
        for role in roles
    ]

@router.get("/{user_id}/role-info", 
           summary="Получить информацию о роли пользователя", 
           response_model=SUserRoleInfo)
async def get_user_role_info(
    user_id: int,
    super_admin: User = Depends(get_current_super_admin)
) -> SUserRoleInfo:
    """
    Получить подробную информацию о роли пользователя.
    """
    user = await UsersDAO.get_user_with_role_info(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    
    return SUserRoleInfo(
        id=user.id,
        user_email=user.user_email,
        first_name=user.first_name,
        last_name=user.last_name,
        current_role_id=user.role_id,
        current_role_name=user.role.role_name,
        new_role_id=user.role_id,  # Текущая роль как новая (по умолчанию)
        new_role_name=user.role.role_name
    )

@router.delete("/dell/{user_id}")
async def dell_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_super_admin)
    ) -> dict:
    """Удалить пользователя (только для суперадминов)"""
    # Проверяем существование пользователя
    existing_user = await UsersDAO.find_one_or_none_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Пользователь с ID {user_id} не найден!'
        )

    check = await UsersDAO.delete_user_by_id(user_id=user_id)
    if check:
        return {"message": f"Пользователь с ID {user_id} удален!"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении пользователя!"
        )