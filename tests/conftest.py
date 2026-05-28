from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from config import settings
from database import Base
from dependencies import get_db_session
from main import app
from repositories.session import SessionRepository
from repositories.user import UserRepository
from schemas.session import SessionModel
from schemas.token import TokenModelResponse
from schemas.user import UserModelResponse, UserCreate
from services.security import JWTService
from services.session import SessionService
from services.user import UserService


@pytest_asyncio.fixture(scope="function")
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


@pytest.fixture(scope="function")
def user_repo(db_session) -> UserRepository:
    return UserRepository(db_session)


@pytest.fixture(scope="function")
def session_repo(db_session) -> SessionRepository:
    return SessionRepository(db_session)


@pytest.fixture(scope="function")
def user_service(db_session) -> UserService:
    return UserService(db_session)


@pytest.fixture(scope="function")
def session_service(db_session) -> SessionService:
    return SessionService(db_session)


@pytest_asyncio.fixture(scope="function")
async def single_user(user_service) -> UserModelResponse:
    return await user_service.register_new_user(UserCreate(username="single_user", password="pwd", tg_id=1111))


@pytest.fixture(scope="function")
def single_users_tokens(single_user) -> TokenModelResponse:
    return JWTService().create_tokens_for_user(single_user)


@pytest_asyncio.fixture(scope="function")
async def single_user_session(
        session_service, single_user, single_users_tokens
) -> SessionModel:
    return await session_service.create_session_for_user(single_user.id, single_users_tokens.refresh_token)


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


@pytest_asyncio.fixture(scope="function")
async def service_token(single_user) -> str:
    service_payload = JWTService._create_service_payload(single_user)
    return JWTService._encode_jwt(service_payload)