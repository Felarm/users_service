import asyncio

import pytest
from fastapi import status
from httpx import AsyncClient
from jose import jwt

from config import settings
from main import app
from auth_session.schemas import TokenModelResponse, RefreshTokenRequest, AccessTokenPayload
from users.schemas import UserFromTg, UserCreate, UserModelResponse
from auth_session.service import SessionService


class TestAuthSuccess:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames=["endpoint_name", "request_data"],
        argvalues=[
            ("register_tg", UserFromTg(username="tg_user", tg_id=1)),
        ]
    )
    async def test_register_endpoints(
            self,
            async_client: AsyncClient,
            service_user_creds: tuple[str, str],
            endpoint_name: str,
            request_data: UserCreate | UserFromTg,
    ):
        response = await async_client.post(
            url=app.url_path_for(endpoint_name),
            json=request_data.model_dump(),
            auth=service_user_creds,
        )
        assert response.status_code == status.HTTP_201_CREATED
        user_tokens = TokenModelResponse.model_validate(response.json())
        access_token_payload = AccessTokenPayload.model_validate(
            jwt.decode(user_tokens.access_token, settings.SECRET_KEY, settings.ALGORITHM))
        assert access_token_payload.username == request_data.username
        assert access_token_payload.tg_id == request_data.tg_id

    @pytest.mark.asyncio
    async def test_login_tg(
            self,
            async_client: AsyncClient,
            service_user_creds: tuple[str, str],
            single_user: UserModelResponse,
    ):
        request_data = UserFromTg(username=single_user.username, tg_id=single_user.tg_id)
        response = await async_client.post(
            url=app.url_path_for("login_tg"),
            json=request_data.model_dump(),
            auth=service_user_creds,
        )
        assert response.status_code == status.HTTP_200_OK
        user_tokens = TokenModelResponse.model_validate(response.json())
        access_token_payload = AccessTokenPayload.model_validate(
            jwt.decode(user_tokens.access_token, settings.SECRET_KEY, settings.ALGORITHM))
        assert access_token_payload.username == single_user.username
        assert access_token_payload.tg_id == single_user.tg_id

    @pytest.mark.asyncio
    async def test_refresh_tokens(
            self,
            async_client: AsyncClient,
            single_users_tokens: TokenModelResponse,
            session_service: SessionService,
            service_user_creds: tuple[str, str],
    ):
        await asyncio.sleep(settings.COOLDOWN_REFRESH_TIME)
        request_data = RefreshTokenRequest(refresh_token=single_users_tokens.refresh_token)
        response = await async_client.post(
            url=app.url_path_for("refresh_tokens"),
            json=request_data.model_dump(),
            auth=service_user_creds,
        )
        assert response.status_code == status.HTTP_200_OK
        new_tokens = TokenModelResponse.model_validate(response.json())
        assert new_tokens.access_token != single_users_tokens.access_token
        assert new_tokens.refresh_token != single_users_tokens.refresh_token
        await asyncio.sleep(settings.COOLDOWN_REFRESH_TIME)
        response = await async_client.post(
            url=app.url_path_for("refresh_tokens"),
            json=request_data.model_dump(),
            auth=service_user_creds,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAuthFails:
    @pytest.mark.asyncio
    async def test_wrong_refresh_token_request(
            self, async_client: AsyncClient, single_users_tokens: TokenModelResponse, service_user_creds: tuple[str, str]
    ):
        wrong_token_request = RefreshTokenRequest(refresh_token="wrong_token")
        refresh_response = await async_client.post(
            url=app.url_path_for("refresh_tokens"),
            json=wrong_token_request.model_dump(),
            auth=service_user_creds,
        )
        assert refresh_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames="route_name",
        argvalues=["login_tg", "register_tg", "refresh_tokens"],
    )
    async def test_missing_service_creds(self, async_client: AsyncClient, route_name: str):
        login_response = await async_client.post(
            url=app.url_path_for(route_name),
            json="some payload",
        )
        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames="route_name",
        argvalues=["login_tg", "register_tg", "refresh_tokens"],
    )
    async def test_wrong_service_creds(self, async_client: AsyncClient, route_name: str):
        response = await async_client.post(
            url=app.url_path_for(route_name),
            json="some_payload",
            auth=("some login", "some password"),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
