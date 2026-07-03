from typing import AsyncGenerator, Any

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session_maker, redis_client
from auth_session.security import SecurityService
from auth_session.service import SessionService
from users.service import UserService


token_bearer = HTTPBearer(description="Only for service users or apps")


async def get_db_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with async_session_maker() as session:
        yield session


async def get_redis_client() -> AsyncGenerator[Redis, Any]:
    yield redis_client


def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(session)


def get_session_service(client: Redis = Depends(get_redis_client)) -> SessionService:
    return SessionService(client)


async def get_service_user_id(service_token: HTTPAuthorizationCredentials = Depends(token_bearer)) -> str:
    payload = SecurityService.get_service_token_payload(service_token.credentials)
    return payload.sub