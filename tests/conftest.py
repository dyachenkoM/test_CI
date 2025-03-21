import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.database import Base
from src.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/test_db"
engine = create_async_engine(TEST_DATABASE_URL, echo=True, poolclass=NullPool)
async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture(scope="session")
async def init_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def client(init_test_db):
    from src.main import get_db, init_db

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[init_db] = init_test_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
