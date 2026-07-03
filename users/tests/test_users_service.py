import pytest

from users.schemas import UserCreate, UserModelResponse, UserFromTg, UserLogin


class TestUserService:
    @pytest.mark.asyncio
    async def test_register_new_user(self, user_service):
        create_data = UserCreate(username="test_user", password="test_pwd")
        new_user = await user_service.register_new_user(create_data)
        assert isinstance(new_user, UserModelResponse)

    @pytest.mark.asyncio
    async def test_register_user_from_tg(self, user_service):
        create_data = UserFromTg(username="test_user", tg_id=1)
        new_user = await user_service.register_user_from_tg(create_data)
        assert isinstance(new_user, UserModelResponse)

    @pytest.mark.asyncio
    async def test_authenticate_user(self, user_service):
        password = "test_pwd"
        create_data = UserCreate(username="test_user", password=password)
        new_user = await user_service.register_new_user(create_data)
        login_data = UserLogin(username=new_user.username, password=password)
        user_from_db = await user_service.login_user_by_password(login_data)
        assert user_from_db == new_user
