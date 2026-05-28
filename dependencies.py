from typing import AsyncGenerator, Any

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session_maker
from services.security import JWTService
from services.session import SessionService
from services.user import UserService


token_bearer = HTTPBearer(description="Only for service users or apps")


async def get_db_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with async_session_maker() as session:
        yield session


def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(session)


def get_session_service(session: AsyncSession = Depends(get_db_session)) -> SessionService:
    return SessionService(session)


async def get_service_user_id(service_token: HTTPAuthorizationCredentials = Depends(token_bearer)) -> str:
    payload = JWTService.get_service_token_payload(service_token.credentials)
    return payload.sub