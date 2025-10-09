
from sqlalchemy import Integer, ForeignKey, Text, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.database import Base, str_uniq, int_pk, str_null_true
from datetime import date
#from app.roles.models import Role

# создаем модель таблицы Пользователей
class User(Base):
    id: Mapped[int_pk] #= mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_phone: Mapped[str_uniq] #= mapped_column(String, unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(index=True, nullable=True)
    last_name: Mapped[str] = mapped_column(index=True, nullable=True)
    user_nick: Mapped[str_uniq] = mapped_column(index=True, nullable=True)
    user_pass: Mapped[str] #= mapped_column(String, index=True, nullable=False)
    user_email: Mapped[str_uniq] #= mapped_column(String, unique=True, nullable=False)
    two_fa_auth: Mapped[int] = mapped_column(default=0, nullable=True, server_default=text('0'))
    email_verified: Mapped[int] = mapped_column(default=0, nullable=True, server_default=text('0'))
    phone_verified: Mapped[int] = mapped_column(default=0, nullable=True, server_default=text('0'))
    user_status: Mapped[int] = mapped_column(Integer, nullable=True)
    # verification_codes: Mapped[list["VerificationCode"]] = relationship(back_populates="user")
    special_notes: Mapped[str_null_true] #= mapped_column(String, nullable=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True, default=4)
    tg_chat_id: Mapped[Optional[str]] = mapped_column(nullable=True)

    # Определяем отношения: один пользователь имеет одну группу
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="joined")

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"first_name={self.first_name!r}, "
                f"last_name={self.last_name!r})")

    def __repr__(self):
        return str(self)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_phone": self.user_phone,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "user_nick": self.first_name,
            # "user_pass": self.user_pass,
            "user_email": self.user_email,
            "two_fa_auth": self.two_fa_auth,
            "email_verified": self.email_verified,
            "phone_verified": self.phone_verified,
            "user_status": self.user_status,
            # "verification_codes": self.verification_codes,
            "special_notes": self.special_notes,
            "role_id": self.role_id,
            "tg_chat_id": self.tg_chat_id
        }

    @property
    def is_admin(self) -> bool:
        """Проверяет, является ли пользователь администратором"""
        return self.role_id in [1, 2]  # Предполагая, что 1=SuperAdmin, 2=Admin
    
    @property
    def is_super_admin(self) -> bool:
        """Проверяет, является ли пользователь суперадмином"""
        return self.role_id == 1  # Предполагая, что 1=SuperAdmin
    @property
    def is_moderator(self) -> bool:
        """Проверяет, является ли пользователь администратором"""
        return self.role_id in [1, 2, 3]  # Предполагая, что 1=SuperAdmin, 2=Admin, 3=Moderator