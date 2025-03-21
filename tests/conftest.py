import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.database import Base

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/test_db"


@pytest.fixture(scope="session")
async def async_db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def init_test_db(async_db_engine):
    async with async_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def async_db_session(async_db_engine):
    async_session = sessionmaker(bind=async_db_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture()
def app():
    from src.main import app
    yield app


@pytest.fixture()
async def client(async_db_session, app, init_test_db):
    from src.main import get_db, init_db

    async def override_get_db():
        yield async_db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[init_db] = init_test_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
