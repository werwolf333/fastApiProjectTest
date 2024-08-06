from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Настройка подключения к базе данных
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Функция для создания всех таблиц
def init_db():
    Base.metadata.create_all(bind=engine)

# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
