
from sqlalchemy import Integer, String, Date, ForeignKey, Column, text, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base, str_uniq, int_pk, str_null_true
from datetime import date
# from app.majors.models import Major


# создаем модель таблицы студентов
class Student(Base):
    id: Mapped[int_pk] #= mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    phone_number: Mapped[str_uniq] #= mapped_column(String, unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    last_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[str_uniq] #= mapped_column(String, unique=True, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    enrollment_year: Mapped[int] = mapped_column(Integer, nullable=False)
    course: Mapped[int] = mapped_column(Integer, nullable=False)
    special_notes: Mapped[str_null_true] #= mapped_column(String, nullable=True)
    major_id: Mapped[int] = mapped_column(Integer, ForeignKey("majors.id"), nullable=False)

    # Определяем отношения: один студент имеет один факультет
    major: Mapped["Major"] = relationship("Major", back_populates="students")
    extend_existing = True

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"first_name={self.first_name!r}, "
                f"last_name={self.last_name!r})")

    def __repr__(self):
        return str(self)
    
    def to_dict(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth,
            "email": self.email,
            "address": self.address,
            "enrollment_year": self.enrollment_year,
            "course": self.course,
            "special_notes": self.special_notes,
            "major_id": self.major_id
        }
