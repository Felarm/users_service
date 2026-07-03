from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from auth_session.tests.conftest import session_service
from config import settings
from database import Base
from dependencies import get_db_session
from main import app
from auth_session.schemas import TokenModelResponse
from users.schemas import UserModelResponse, UserCreate
from users.service import UserService


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, Any]:
    engine = create_async_engine(url=settings.test_db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, Any]:
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        await session.begin()
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="session")
async def redis_client() -> AsyncGenerator[Redis, Any]:
    redis_client = Redis.from_url(settings.redis_url)
    yield redis_client
    await redis_client.aclose()


@pytest.fixture(scope="function")
def user_service(db_session) -> UserService:
    return UserService(db_session)


@pytest_asyncio.fixture(scope="function")
async def single_user(user_service) -> UserModelResponse:
    return await user_service.register_new_user(UserCreate(username="single_user", password="pwd", tg_id=1111))


@pytest_asyncio.fixture(scope="function")
async def single_users_tokens(single_user, session_service) -> TokenModelResponse:
    return await session_service.create_session_tokens(single_user)


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session) -> AsyncGenerator[AsyncClient, Any]:
    async def _get_db_override():
        yield db_session
    app.dependency_overrides[get_db_session] = _get_db_override
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
