from pydantic import BaseModel, Field


class SRolesAdd(BaseModel):
    role_name: str = Field(..., description="Название Роли")
    role_description: str = Field(None, description="Описание Роли")
    count_users: int = Field(0, description="Количество пользователей")

class SRolesUpdDesc(BaseModel):
    role_name: str = Field(..., description="Название Роли")
    role_description: str = Field(None, description="Новое описание Роли")