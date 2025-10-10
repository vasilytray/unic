
from sqlalchemy import Integer, ForeignKey, Text, text, event, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.database import Base, str_uniq, int_pk, str_null_true
from datetime import date, datetime, timezone
#from app.roles.models import Role

class UserLog(Base):
    __tablename__ = "users_logs"
    
    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(nullable=False)  # 'role_change', 'profile_update', etc.
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Связи
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="logs")
    changer: Mapped["User"] = relationship("User", foreign_keys=[changed_by], back_populates="changes_made")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, user_id={self.user_id}, action={self.action_type})"

    def __repr__(self):
        return str(self)

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

    logs: Mapped[list["UserLog"]] = relationship("UserLog", foreign_keys=[UserLog.user_id], back_populates="user")
    changes_made: Mapped[list["UserLog"]] = relationship("UserLog", foreign_keys=[UserLog.changed_by], back_populates="changer")

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
    
