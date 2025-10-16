from sqlalchemy import Integer, Text, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

# Константы для ID ролей
class TicketStatus:
    OPEN = 1
    INPROGRESS = 2
    AWAITURESPONSE = 3
    CLOSED = 4

class Priority:
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    URGENT = 4
    

class Ticket(Base):
    __tablename__ = 'tickets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[int] = mapped_column(default=1, nullable=True, server_default=text('0'))