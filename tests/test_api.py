import asyncio

import pytest
from fastapi import status
from httpx import AsyncClient

from exceptions import SessionNotFoundException
from main import app
from schemas.session import SessionModel
from schemas.token import TokenModelResponse, RefreshTokenRequest
from schemas.user import UserFromTg, UserCreate, UserLogin, UserModelResponse
from services.security import JWTService
from services.session import SessionService


class TestAuthSuccess:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames=["endpoint_name", "request_data"],
        argvalues=[
            ("register_tg", UserFromTg(username="tg_user", tg_id=1)),
            ("register_web", UserCreate(username="web_user", password="pwd", tg_id=1)),
        ]
    )
    async def test_register_endpoints(
            self,
            async_client: AsyncClient,
            service_token: str,
            endpoint_name: str,
            request_data: UserCreate | UserFromTg,
            jwt_service: JWTService,
    ):
        response = await async_client.post(
            url=app.url_path_for(endpoint_name),
            json=request_data.model_dump(),
            headers={"Authorization": f"Bearer {service_token}"} if endpoint_name == "register_tg" else None,
        )
        assert response.status_code == status.HTTP_201_CREATED
        user_tokens = TokenModelResponse.model_validate(response.json())
        access_token_payload = jwt_service.get_access_token_payload(user_tokens.access_token)
        assert access_token_payload.username == request_data.username
        assert access_token_payload.tg_id == request_data.tg_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames=["endpoint_name", "request_data"],
        argvalues=[
            ("login_tg", UserFromTg(username="single_user", tg_id=1111)),
            ("login_web", UserLogin(username="single_user", password="pwd")),
        ]
    )
    async def test_login_endpoints(
            self,
            async_client: AsyncClient,
            service_token: str,
            endpoint_name: str,
            request_data: UserCreate | UserFromTg,
            single_user: UserModelResponse,
            jwt_service:JWTService,
    ):
        response = await async_client.post(
            url=app.url_path_for(endpoint_name),
            json=request_data.model_dump(),
            headers={"Authorization": f"Bearer {service_token}"} if endpoint_name == "login_tg" else None,
        )
        assert response.status_code == status.HTTP_200_OK
        user_tokens = TokenModelResponse.model_validate(response.json())
        access_token_payload = jwt_service.get_access_token_payload(user_tokens.access_token)
        assert access_token_payload.username == single_user.username
        assert access_token_payload.tg_id == single_user.tg_id

    @pytest.mark.asyncio
    async def test_refresh_tokens(
            self,
            async_client: AsyncClient,
            single_users_tokens: TokenModelResponse,
            single_user_session: SessionModel,
            session_service: SessionService,
            jwt_service: JWTService
    ):
        previous_refresh_payload = jwt_service.get_refresh_token_payload(single_users_tokens.refresh_token)
        await asyncio.sleep(1)
        request_data = RefreshTokenRequest(refresh_token=single_users_tokens.refresh_token)
        response = await async_client.post(
            url=app.url_path_for("refresh_tokens"),
            json=request_data.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK
        new_tokens = TokenModelResponse.model_validate(response.json())
        new_refresh_payload = jwt_service.get_refresh_token_payload(new_tokens.refresh_token)
        assert new_refresh_payload.exp > previous_refresh_payload.exp
        assert new_refresh_payload.sub == previous_refresh_payload.sub
        with pytest.raises(SessionNotFoundException):
            await session_service.get_user_session_by_token(single_users_tokens.refresh_token)
