import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from auth_session.repository import SessionRepository, SessionStatus
from config import settings
from users.schemas import UserModelResponse


class TestSessionRepository:
    @pytest.mark.asyncio
    async def test_create_session_w_cooldown(
            self, session_repo: SessionRepository, single_user: UserModelResponse,
    ):
        old_refresh_token = "123"
        expiration_timestamp = int((datetime.now(UTC) + timedelta(minutes=2)).timestamp())
        await session_repo.create_session(single_user.id, old_refresh_token, expiration_timestamp)
        new_refresh_token = "234"
        await session_repo.create_session_w_cooldown(old_refresh_token, new_refresh_token, single_user.id, expiration_timestamp)
        old_session_data = await session_repo.get_session(old_refresh_token)
        assert old_session_data.status == SessionStatus.grace_period
        assert old_session_data.new_token == new_refresh_token
        await asyncio.sleep(settings.COOLDOWN_REFRESH_TIME)
        cooldowned_session = await session_repo.get_session(old_refresh_token)
        assert cooldowned_session is None
