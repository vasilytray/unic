from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr
from app3.config import get_db_url


DATABASE_URL = get_db_url()

engine = create_async_engine(DATABASE_URL) # создаёт асинхронное подключение к базе данных PostgreSQL, используя драйвер asyncpg
async_session_maker = async_sessionmaker(engine, expire_on_commit=False) # создаёт фабрику асинхронных сессий, используя созданный движок. 
                                                                         # Сессии используются для выполнения транзакций в базе данных


class Base(AsyncAttrs, DeclarativeBase): # абстрактный класс, от которого наследуются все модели.
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"