import secrets
import string
from datetime import datetime, UTC, timedelta
from typing import Union

from jose import jwt, JWTError
from passlib.context import CryptContext

from config import settings
from exceptions import UnauthorizedException
from schemas.token import AccessTokenPayload, RefreshTokenPayload, ServiceTokenPayload, TokenModelResponse
from schemas.user import UserModelResponse


class PasswordService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, input_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(input_password, hashed_password)

    @classmethod
    def hash_password(cls, input_password: str) -> str:
        return cls.pwd_context.hash(input_password)

    @classmethod
    def generate_n_hash_password(cls) -> str:
        alphabet = string.ascii_letters + string.digits
        random_chars = "".join(secrets.choice(alphabet) for _ in range(16))
        return cls.pwd_context.hash(random_chars)


class JWTService:
    def create_tokens_for_user(self, user: UserModelResponse) -> TokenModelResponse:
        access_payload = self._create_access_payload(user)
        refresh_payload = self._create_refresh_payload(user)
        access_token = self._encode_jwt(access_payload)
        refresh_token = self._encode_jwt(refresh_payload)
        return TokenModelResponse(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def _create_access_payload(user: UserModelResponse) -> AccessTokenPayload:
        now = datetime.now(UTC)
        expires = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return AccessTokenPayload(
            sub=str(user.id),
            username=user.username,
            tg_id=user.tg_id,
            exp=int(expires.timestamp()),
            iat=int(now.timestamp()),
        )

    @staticmethod
    def _create_refresh_payload(user: UserModelResponse) -> RefreshTokenPayload:
        now = datetime.now(UTC)
        expires = now + timedelta(settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return RefreshTokenPayload(
            sub=str(user.id),
            username=user.username,
            tg_id=user.tg_id,
            exp=int(expires.timestamp()),
            iat=int(now.timestamp()),
        )

    @staticmethod
    def _create_service_payload(user: UserModelResponse) -> ServiceTokenPayload:
        # now = datetime.now(UTC)
        # expires = now + timedelta(settings.SERVICE_TOKEN_EXPIRE_DAYS)
        return ServiceTokenPayload(
            sub=str(user.id),
            username=user.username,
        )

    @staticmethod
    def _encode_jwt(payload: Union[AccessTokenPayload, RefreshTokenPayload, ServiceTokenPayload]) -> str:
        return jwt.encode(payload.model_dump(), settings.SECRET_KEY, settings.ALGORITHM)

    @staticmethod
    def get_service_token_payload(encoded_token: str) -> ServiceTokenPayload:
        try:
            payload = ServiceTokenPayload(**jwt.decode(encoded_token, settings.SECRET_KEY, settings.ALGORITHM))
        except JWTError as e:
            raise UnauthorizedException("Wrong token data") from e
        if payload.type != "service":
            raise UnauthorizedException("Wrong token type")
        return payload

    @staticmethod
    def get_refresh_token_payload(encoded_token: str) -> RefreshTokenPayload:
        try:
            payload = RefreshTokenPayload(**jwt.decode(encoded_token, settings.SECRET_KEY, settings.ALGORITHM))
        except JWTError as e:
            raise UnauthorizedException("Wrong token data") from e
        if payload.type != "refresh":
            raise UnauthorizedException("Wrong token type")
        return payload

    @staticmethod
    def get_access_token_payload(encoded_token: str) -> AccessTokenPayload:
        try:
            payload = AccessTokenPayload(**jwt.decode(encoded_token, settings.SECRET_KEY, settings.ALGORITHM))
        except JWTError as e:
            raise UnauthorizedException("Wrong token data") from e
        if payload.type != "access":
            raise UnauthorizedException("Wrong token type")
        return payload
