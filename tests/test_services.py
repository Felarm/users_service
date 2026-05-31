import asyncio
from datetime import datetime, timedelta, UTC

import pytest

from config import settings
from exceptions import SessionNotFoundException, TokenException
from schemas.token import TokenTypes
from schemas.user import UserCreate, UserModelResponse, UserFromTg, UserLogin
from services.security import JWTService


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


class TestJWTService:
    @pytest.mark.asyncio
    def test_create_access_payload(self, single_user):
        access_payload = JWTService._create_access_payload(single_user)
        assert access_payload.username == single_user.username
        assert int(access_payload.sub) == single_user.id
        assert access_payload.tg_id == single_user.tg_id
        access_expected_exp_dt = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        assert int(access_expected_exp_dt.timestamp()) == access_payload.exp

    @pytest.mark.asyncio
    def test_create_refresh_payload(self, single_user):
        refresh_payload = JWTService._create_refresh_payload(single_user)
        assert refresh_payload.username == single_user.username
        assert int(refresh_payload.sub) == single_user.id
        assert refresh_payload.tg_id == single_user.tg_id
        refresh_expected_exp_dt = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        assert int(refresh_expected_exp_dt.timestamp()) == refresh_payload.exp

    @pytest.mark.asyncio
    def test_create_tokens_for_user(
            self, single_user, single_users_tokens, jwt_service
    ):
        access_payload = jwt_service.get_access_token_payload(single_users_tokens.access_token)
        refresh_payload = jwt_service.get_refresh_token_payload(single_users_tokens.refresh_token)
        assert int(access_payload.sub) == single_user.id
        assert access_payload.username == single_user.username
        assert access_payload.type == TokenTypes.ACCESS
        assert int(refresh_payload.sub) == single_user.id
        assert refresh_payload.username == single_user.username
        assert refresh_payload.type == TokenTypes.REFRESH


class TestSessionService:
    @pytest.mark.asyncio
    async def test_get_user_session_by_token(
            self,
            session_service,
            single_users_tokens,
            single_user_session,
            jwt_service,
    ):
        refresh_token_payload = jwt_service.get_refresh_token_payload(single_users_tokens.refresh_token)
        user_session = await session_service.get_user_session_by_token(single_users_tokens.refresh_token)
        assert user_session.id == single_user_session.id
        assert user_session.user_id == int(refresh_token_payload.sub)
        assert refresh_token_payload.jti == user_session.jti
        assert refresh_token_payload.exp == int(user_session.expires_at.timestamp())

    @pytest.mark.asyncio
    async def test_revoke_user_session(self, session_service, single_user_session, single_users_tokens):
        await session_service.revoke_user_session(single_user_session.id)
        with pytest.raises(SessionNotFoundException):
            await session_service.get_user_session_by_token(single_users_tokens.refresh_token)

    @pytest.mark.asyncio
    async def test_expired_session(self, session_service, single_user):
        refresh_payload = JWTService._create_refresh_payload(single_user)
        refresh_payload.exp = int(datetime.now(UTC).timestamp())
        refresh_jwt = JWTService._encode_jwt(refresh_payload)
        await session_service.create_session_for_user(single_user.id, refresh_jwt)
        await asyncio.sleep(1)
        with pytest.raises(TokenException):
            await session_service.get_user_session_by_token(refresh_jwt)
