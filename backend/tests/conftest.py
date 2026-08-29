import os

# Тесты API фиксируют поведение заглушки: детерминированный результат и работа
# без весов YOLO (~2 ГБ) в CI. Настоящее ядро покрыто тестами пакета
# expert_system в корне репозитория. Значение выставляется до импорта app,
# чтобы локальный ML_BACKEND=expert_system не ломал прогон.
os.environ["ML_BACKEND"] = "mock"

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.controllers.auth_controller import get_db
from app.main import app
from app.middleware.auth_middleware import get_db as get_auth_middleware_db

from app.models.user import User
from app.models.analysis_result import AnalysisResult
from app.models.action_log import ActionLog
from app.models.director_invite import DirectorInvite
from app.models.invite_acceptance import InviteAcceptance

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if TEST_DATABASE_URL is None:
    raise RuntimeError("TEST_DATABASE_URL is not set in .env")

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Не autouse: тесты, которым база не нужна (например, стыковка с ядром
# экспертной системы), должны прогоняться без поднятого PostgreSQL.
# Фикстура подтягивается через db_session, поэтому для API-тестов
# поведение не изменилось.
@pytest.fixture(scope="session")
def prepare_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(prepare_test_database):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_auth_middleware_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
