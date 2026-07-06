from datetime import datetime, UTC, timedelta
from uuid import uuid4

from jose import jwt
from redis.asyncio import Redis

from config import settings
from exceptions import SessionNotFoundException
from auth_session.repository import SessionRepository, SessionStatus
from auth_session.schemas import AccessTokenPayload, TokenModelResponse
from users.schemas import UserModelResponse, UserFilter
from users.service import UserService


class SessionService:
    def __init__(self, redis_client: Redis):
        self.repo = SessionRepository(redis_client)

    async def create_session_tokens(self, user: UserModelResponse) -> TokenModelResponse:
        now = datetime.now(UTC)
        new_refresh_token = str(uuid4())
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.repo.create_session(user.id, new_refresh_token, int(expires_at.timestamp()))
        new_access_token = self.create_access_token(user, now)
        return TokenModelResponse(access_token=new_access_token, refresh_token=new_refresh_token)

    async def refresh_tokens(self, refresh_token: str, user_service: UserService) -> TokenModelResponse:
        current_session_data = await self.repo.get_session(refresh_token)
        if current_session_data is None:
            raise SessionNotFoundException
        if current_session_data.status == SessionStatus.grace_period and current_session_data.new_token is not None:
            already_created_session_data = await self.repo.get_session(current_session_data.new_token)
            if already_created_session_data is None or already_created_session_data.new_token is None:
                raise SessionNotFoundException
            user = await user_service.get_user_by(UserFilter(id=already_created_session_data.user_id))
            new_access_token = self.create_access_token(user)
            return TokenModelResponse(access_token=new_access_token, refresh_token=already_created_session_data.new_token)
        user = await user_service.get_user_by(UserFilter(id=current_session_data.user_id))
        now = datetime.now(UTC)
        new_refresh_token = str(uuid4())
        expire_delta = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.repo.create_session_w_cooldown(refresh_token, new_refresh_token, user.id, int(expire_delta.timestamp()))
        new_access_token = self.create_access_token(user, now)
        return TokenModelResponse(access_token=new_access_token, refresh_token=new_refresh_token)

    @staticmethod
    def create_access_token(user: UserModelResponse, now: datetime = datetime.now(UTC)) -> str:
        expires = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = AccessTokenPayload(
            sub=str(user.id),
            username=user.username,
            tg_id=user.tg_id,
            exp=int(expires.timestamp()),
            iat=int(now.timestamp()),
        )
        return jwt.encode(new_access_token.model_dump(), settings.SECRET_KEY, settings.ALGORITHM)
