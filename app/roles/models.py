
from sqlalchemy import text, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base, str_uniq, int_pk, str_null_true
from app.users.models import User

# Константы для ID ролей
class RoleTypes:
    SUPER_ADMIN = 1
    ADMIN = 2
    MODERATOR = 3
    USER = 4
    GUEST = 5

# создаем модель таблицы групп пользователей (Role)
class Role(Base):
    id: Mapped[int_pk] #= mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name: Mapped[str_uniq] #= mapped_column(String, unique=True, nullable=False)
    role_description: Mapped[str_null_true]#[str] = mapped_column(String, nullable=True)
    count_users: Mapped[int] = mapped_column(server_default=text('0'))

    # Определяем отношения: одна группа может иметь много пользователей
    users: Mapped[list["User"]] = relationship("User", back_populates="role")
    
    #back_populates="role": указывает, что обратная связь идет через атрибут role в модели User.

    @property
    def is_admin_role(self) -> bool:
        """Проверяет, является ли роль административной"""
        return self.id in [1, 2]
    
    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, role_name={self.role_name!r})"

    def __repr__(self):
        return str(self)