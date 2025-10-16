from sqlalchemy import select, and_, or_
from app.dao.base import BaseDAO
from app.chat.models import Message
from app.database import async_session_maker


class MessagesDAO(BaseDAO):
    model = Ticket