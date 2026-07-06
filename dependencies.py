import hashlib
from typing import AsyncGenerator, Any

from fastapi import Depends, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session_maker, redis_client
from auth_session.security import SecurityService
from auth_session.service import SessionService
from exceptions import ForbiddenException, UnauthorizedException, UserNotFoundException
from users.schemas import UserFilter, UserModelResponse
from users.service import UserService


basic_auth = HTTPBasic(description="Only for service users or apps")


async def get_db_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with async_session_maker() as session:
        yield session


async def get_redis_client() -> AsyncGenerator[Redis, Any]:
    yield redis_client


def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(session)


def get_session_service(client: Redis = Depends(get_redis_client)) -> SessionService:
    return SessionService(client)


async def check_service_user(
        credentials: HTTPBasicCredentials = Security(basic_auth),
        redis: Redis = Depends(get_redis_client),
        user_service: UserService = Depends(get_user_service)
) -> UserModelResponse:
    service_username = credentials.username
    raw_pwd = credentials.password
    redis_lookup_hash = hashlib.sha256(raw_pwd.encode()).hexdigest()
    redis_key = f"service:{service_username}:{redis_lookup_hash}"
    cached_service_user_id = await redis.get(redis_key)
    if cached_service_user_id:
        service_user = await user_service.get_user_by(UserFilter(id=cached_service_user_id))
        if service_user and service_user.is_service and service_user.is_active:
            return service_user
        raise ForbiddenException("Incorrect service credentials")
    try:
        service_user = await user_service.get_user_by(UserFilter(username=service_username))
    except UserNotFoundException:
        raise UnauthorizedException("Service user not found")
    if not service_user.is_service or not service_user.is_active:
        raise UnauthorizedException("Invalid service user right")
    if not SecurityService.verify_password(raw_pwd, service_user.hashed_password):
        raise UnauthorizedException("Invalid service user password")
    await redis.setex(redis_key, 900, str(service_user.id))
    return service_user
