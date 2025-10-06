
from sqlalchemy import  text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base, str_uniq, int_pk, str_null_true
from app.students.models import Student

# создаем модель таблицы факультетов (majors)
class Major(Base):
    id: Mapped[int_pk] #= mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    major_name: Mapped[str_uniq] #= mapped_column(String, unique=True, nullable=False)
    major_description: Mapped[str_null_true]#[str] = mapped_column(String, nullable=True)
    count_students: Mapped[int] = mapped_column(server_default=text('0'))
    
    students: Mapped[list["Student"]] = relationship("Student", back_populates="major")
    extend_existing = True

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, major_name={self.major_name!r})"

    def __repr__(self):
        return str(self)