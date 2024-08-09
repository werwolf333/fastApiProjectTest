import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from auth_module import models
from main import app


# Создание фикстуры для базы данных
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")  # Используйте вашу реальную строку подключения
    models.Base.metadata.create_all(bind=engine)  # Создаем таблицы в базе данных
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db  # Возвращаем сессию для использования в тестах

    db.close()  # Закрываем сессию после тестов
    models.Base.metadata.drop_all(bind=engine)  # Удаляем таблицы после тестов

client = TestClient(app)


@pytest.fixture
def test_user():
    return {
        "username": "existinguser",
        "email": "existing@example.com",
        "password": "testpassword"
    }


@pytest.fixture
def existing_user(db_session):
    user = models.User(username="existinguser", email="existing@example.com", hashed_password="hashedpassword")
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()


def test_register_user(test_user):
    response = client.post("/register", data=test_user)
    assert "error" not in response.text
    assert "login" in response.text


def test_register_user_with_existing_username(existing_user, test_user):
    unique_test_email = "_" + test_user["email"]
    response = client.post("/register", data={
        "username": test_user["username"],
        "email": unique_test_email,
        "password": test_user["password"]
    })
    context = response.context
    assert context["error"] == "Username already registered"


def test_register_user_with_existing_email(existing_user, test_user):
    unique_test_username = "_" + test_user["username"]
    response = client.post("/register", data={
        "username":  unique_test_username,
        "email": test_user["email"],
        "password": test_user["password"]
    })
    context = response.context
    assert context["error"] == "Email already registered"


def test_register_user_with_invalid_email(existing_user, test_user):
    unique_test_username = "_" + test_user["username"]
    bad_email = "existing@example"
    response = client.post("/register", data={
        "username":  unique_test_username,
        "email": bad_email,
        "password": test_user["password"]
    })
    context = response.context
    assert context["error"] == "Invalid email address"
