from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UsersDAO
from app.users.rb import RBUser
from app.users.models import User
from app.users.schemas import SUserBase, SUserAdd, SUserResponse, SUserListResponse, SUserAuth
from app.users.schemas import SUserRegister
from app.users.dependencies import get_current_user, get_current_admin, get_current_moderator, get_current_super_admin

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