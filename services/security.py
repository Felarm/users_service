import secrets
import string
from datetime import datetime, UTC, timedelta
from typing import Union

from jose import jwt, JWTError, ExpiredSignatureError
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from config import settings
from exceptions import TokenException
from schemas.auth_token import AccessTokenPayload, RefreshTokenPayload, ServiceTokenPayload, TokenModelResponse, TokenTypes, \
    TokenErrors
from schemas.user import UserModelResponse


class PasswordService:
    pwd_context = PasswordHash(hashers=[Argon2Hasher(), BcryptHasher()])

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
    def get_token_payload(
            encoded_token: str, token_type: str) -> Union[AccessTokenPayload, RefreshTokenPayload, ServiceTokenPayload]:
        payload_types_map = {
            TokenTypes.ACCESS: AccessTokenPayload,
            TokenTypes.REFRESH: RefreshTokenPayload,
            TokenTypes.SERVICE: ServiceTokenPayload,
        }
        if token_type not in payload_types_map:
            raise TokenException(token_type, TokenErrors.WRONG_TOKEN_TYPE)
        try:
            payload = payload_types_map[token_type](
                **jwt.decode(encoded_token, settings.SECRET_KEY, settings.ALGORITHM)
            )
            if payload.type != token_type:
                raise TokenException(payload.type, TokenErrors.WRONG_TOKEN_TYPE)
            return payload
        except ExpiredSignatureError:
            raise TokenException(token_type, TokenErrors.EXPIRED)
        except JWTError as e:
            raise TokenException(token_type, TokenErrors.INVALID_DATA) from e

    def get_service_token_payload(self, encoded_token: str) -> ServiceTokenPayload:
        return self.get_token_payload(encoded_token, TokenTypes.SERVICE)

    def get_refresh_token_payload(self, encoded_token: str) -> RefreshTokenPayload:
        return self.get_token_payload(encoded_token, TokenTypes.REFRESH)

    def get_access_token_payload(self, encoded_token: str) -> AccessTokenPayload:
        return self.get_token_payload(encoded_token, TokenTypes.ACCESS)
