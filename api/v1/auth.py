from typing import Annotated

from fastapi import APIRouter, status, Depends

from dependencies import get_user_service, get_session_service, get_service_user_id
from schemas.token import TokenModelResponse, RefreshTokenRequest, TokenExceptionContent
from schemas.user import UserFromTg, UserCreate, UserFilter, UserLogin
from services.security import JWTService
from services.session import SessionService
from services.user import UserService


router = APIRouter(prefix="/auth", tags=["Authentication"])
UserService_ = Annotated[UserService, Depends(get_user_service)]
SessionService_ = Annotated[SessionService, Depends(get_session_service)]
ServiceTokenValidation = Annotated[str, Depends(get_service_user_id)]


@router.post(
    path="/register/tg",
    response_model=TokenModelResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": TokenExceptionContent}
    }
)
async def register_tg(
        new_user_data: UserFromTg,
        user_service: UserService_,
        session_service: SessionService_,
        _: ServiceTokenValidation,
):
    new_user = await user_service.register_user_from_tg(new_user_data)
    users_tokens = JWTService().create_tokens_for_user(new_user)
    await session_service.create_session_for_user(new_user.id, users_tokens.refresh_token)
    return users_tokens


@router.post(path="/register/web", response_model=TokenModelResponse, status_code=status.HTTP_201_CREATED)
async def register_web(
        new_user_data: UserCreate,
        user_service: UserService_,
        session_service: SessionService_,
):
    new_user = await user_service.register_new_user(new_user_data)
    users_tokens = JWTService().create_tokens_for_user(new_user)
    await session_service.create_session_for_user(new_user.id, users_tokens.refresh_token)
    return users_tokens


@router.post(
    path="/login/tg",
    response_model=TokenModelResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": TokenExceptionContent}
    }
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
    users_tokens = JWTService().create_tokens_for_user(user)
    await session_service.create_session_for_user(user.id, users_tokens.refresh_token)
    return users_tokens


@router.post(path="/login/web", response_model=TokenModelResponse, status_code=status.HTTP_200_OK)
async def login_web(
        login_data: UserLogin,
        user_service: UserService_,
        session_service: SessionService_,
):
    user = await user_service.login_user_by_password(login_data)
    users_tokens = JWTService().create_tokens_for_user(user)
    await session_service.create_session_for_user(user.id, users_tokens.refresh_token)
    return users_tokens


@router.post(
    path="/refresh",
    response_model=TokenModelResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": TokenExceptionContent}
    }
)
async def refresh_tokens(
        token: RefreshTokenRequest,
        session_service: SessionService_,
        user_service: UserService_,
):
    jwt_service = JWTService()
    refresh_token_payload = jwt_service.get_refresh_token_payload(token.refresh_token)
    active_session = await session_service.get_user_session_by_token(token.refresh_token)
    user = await user_service.get_user_by(UserFilter(id=int(refresh_token_payload.sub)))
    await session_service.revoke_user_session(active_session.id)
    new_tokens = jwt_service.create_tokens_for_user(user)
    await session_service.create_session_for_user(user.id, new_tokens.refresh_token)
    return new_tokens

