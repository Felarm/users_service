import asyncio
from datetime import datetime, UTC, timedelta

import pytest
from jose import jwt

from auth_session.schemas import AccessTokenPayload
from auth_session.service import SessionService
from auth_session.tests.conftest import session_service
from config import settings
from exceptions import SessionNotFoundException
from users.schemas import UserModelResponse
from users.service import UserService


class TestSessionService:
    @pytest.mark.asyncio
    async def test_create_session_token(self, single_user: UserModelResponse, session_service: SessionService):
        single_user_tokens = await session_service.create_session_tokens(single_user)
        access_payload = AccessTokenPayload(
            **jwt.decode(single_user_tokens.access_token, settings.SECRET_KEY, settings.ALGORITHM))
        assert access_payload.sub == str(single_user.id)
        assert access_payload.username == single_user.username
        assert access_payload.tg_id == single_user.tg_id
        assert access_payload.exp <= int((datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
        assert single_user_tokens.refresh_token is not None
        assert isinstance(single_user_tokens.refresh_token, str)

    @pytest.mark.asyncio
    async def test_refresh_tokens(
            self, user_service: UserService, single_user: UserModelResponse, session_service: SessionService):
        old_user_tokens = await session_service.create_session_tokens(single_user)
        old_access_payload = AccessTokenPayload(
            **jwt.decode(old_user_tokens.access_token, settings.SECRET_KEY, settings.ALGORITHM)
        )
        with pytest.raises(SessionNotFoundException):
            await session_service.refresh_tokens("123", user_service)
        await asyncio.sleep(1.0)
        refreshed_user_tokens = await session_service.refresh_tokens(old_user_tokens.refresh_token, user_service)
        new_access_payload = AccessTokenPayload(
            **jwt.decode(refreshed_user_tokens.access_token, settings.SECRET_KEY, settings.ALGORITHM)
        )
        assert new_access_payload.sub == old_access_payload.sub
        assert new_access_payload.tg_id == old_access_payload.tg_id
        assert new_access_payload.username == old_access_payload.username
        assert new_access_payload.exp > old_access_payload.exp
        assert old_user_tokens.refresh_token != refreshed_user_tokens.refresh_token
        await asyncio.sleep(settings.COOLDOWN_REFRESH_TIME)
        with pytest.raises(SessionNotFoundException):
            await session_service.refresh_tokens(old_user_tokens.refresh_token, user_service)


