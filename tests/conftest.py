import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models import Base


TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/test_db"


@pytest.fixture(scope="session")
async def async_db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Очистка всех таблиц
        await conn.run_sync(Base.metadata.create_all)  # Создание таблиц
    yield engine
    await engine.dispose()


@pytest.fixture(autouse=True)
async def cleanup_metadata_and_db(async_db_engine):
    Base.metadata.clear()  # Очистка метаданных SQLAlchemy
    async with async_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Очистка всех таблиц
        await conn.run_sync(Base.metadata.create_all)  # Создание таблиц


@pytest.fixture(scope="session")
async def async_db_session(async_db_engine):
    async_session = sessionmaker(bind=async_db_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session


@pytest.fixture()
def app():
    from src.main import app

    yield app


@pytest.fixture()
async def client(async_db_session, app):
    # from src.main import get_db
    # app.dependency_overrides.update({
    #     get_db: async_db_session
    # })
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
