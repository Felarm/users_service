import pytest
from sqlalchemy.exc import IntegrityError

from users.repository import UserRepository


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
            username="test_user_for_get_by",
            tg_id=10101,
        )
        user_by_id = await user_repo.get_user_by_id(new_user.id)
        assert new_user == user_by_id
        user_by_username = await user_repo.get_user_by_username("test_user_for_get_by")
        assert new_user == user_by_username
        user_by_tg_id = await user_repo.get_user_by_tg_id(10101)
        assert new_user == user_by_tg_id
