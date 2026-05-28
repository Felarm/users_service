from datetime import datetime, UTC, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from repositories.user import UserRepository


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_create_user(self, user_repo: UserRepository):
        new_user = await user_repo.create_user(hashed_password="pwd_hash", username="test_user")
        assert new_user.id is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ["user_1", "user_2"],
        [
            ({"username": "user"}, {"username": "user"}),
            ({"username": "user_1", "tg_id": 1}, {"username": "user_2", "tg_id": 1})
        ]
    )
    async def test_fail_create_user(
            self, user_repo, user_1: dict[str, str | int], user_2: dict[str, str | int]
    ):
        with pytest.raises(IntegrityError):
            await user_repo.create_user(hashed_password="1", **user_1)
            await user_repo.create_user(hashed_password="2", **user_2)

    @pytest.mark.asyncio
    async def test_get_user_by(self, user_repo):
        new_user = await user_repo.create_user(
            hashed_password="1",
            username="test_user",
            tg_id=1,
        )
        user_by_id = await user_repo.get_user_by_id(new_user.id)
        assert new_user == user_by_id
        user_by_username = await user_repo.get_user_by_username("test_user")
        assert new_user == user_by_username
        user_by_tg_id = await user_repo.get_user_by_tg_id(1)
        assert new_user == user_by_tg_id


class TestSessionRepository:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_token_jtis", [["1", "2", "3"]])
    async def test_delete_expired_sessions(self, session_repo, single_user, test_token_jtis):
        for jti in test_token_jtis:
            expiration_timestamp = int((datetime.now(UTC) - timedelta(minutes=1)).timestamp())
            await session_repo.create_user_session(single_user.id, jti, expiration_timestamp)
        await session_repo.delete_expired_sessions()
        user_sessions = await session_repo.get_user_sessions(single_user.id)
        assert len(user_sessions) == 0
