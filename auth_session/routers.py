from typing import Annotated

from fastapi import APIRouter, status, Depends

from dependencies import get_user_service, get_session_service, check_service_user
from auth_session.schemas import TokenModelResponse, RefreshTokenRequest
from users.schemas import UserFromTg, UserFilter, UserModelResponse
from auth_session.service import SessionService
from users.service import UserService


router = APIRouter(prefix="/auth", tags=["Authentication"])
UserService_ = Annotated[UserService, Depends(get_user_service)]
SessionService_ = Annotated[SessionService, Depends(get_session_service)]
ServiceTokenValidation = Annotated[UserModelResponse, Depends(check_service_user)]


@router.post(
    path="/register/tg",
    response_model=TokenModelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_tg(
        new_user_data: UserFromTg,
        user_service: UserService_,
        session_service: SessionService_,
        _: ServiceTokenValidation,
):
    new_user = await user_service.register_user_from_tg(new_user_data)
    users_tokens = await session_service.create_session_tokens(new_user)
    return users_tokens


@router.post(
    path="/login/tg",
    response_model=TokenModelResponse,
    status_code=status.HTTP_200_OK,
)
async def login_tg(
        user_data: UserFromTg,
        user_service: UserService_,
        session_service: SessionService_,
        _: ServiceTokenValidation,
):
    user = await user_service.get_user_by(UserFilter(tg_id=user_data.tg_id))
    if user.username != user_data.username:
        pass  # todo raise or what? what to do if tg username is diff
    users_tokens = await session_service.create_session_tokens(user)
    return users_tokens


@router.post(
    path="/refresh",
    response_model=TokenModelResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_tokens(
        token: RefreshTokenRequest,
        session_service: SessionService_,
        user_service: UserService_,
        _: ServiceTokenValidation,
):
    refreshed_tokens = await session_service.refresh_tokens(token.refresh_token, user_service)
    return refreshed_tokens
