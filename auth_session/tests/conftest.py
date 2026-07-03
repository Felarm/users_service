import pytest
import pytest_asyncio

from auth_session.repository import SessionRepository
from auth_session.security import SecurityService
from auth_session.service import SessionService


@pytest.fixture(scope="function")
def session_repo(redis_client) -> SessionRepository:
    return SessionRepository(redis_client)


@pytest.fixture(scope="function")
def session_service(redis_client) -> SessionService:
    return SessionService(redis_client)


@pytest.fixture(scope="function")
def security_service() -> SecurityService:
    return SecurityService()


@pytest_asyncio.fixture(scope="function")
async def service_token(single_user) -> str:
    return SecurityService.create_service_token(single_user)
