import secrets
import string

from jose import jwt, JWTError, ExpiredSignatureError
from pwdlib import PasswordHash

from config import settings
from exceptions import TokenException
from auth_session.schemas import TokenTypes, ServiceTokenPayload, TokenErrors
from users.schemas import UserModelResponse


class SecurityService:
    pwd_context = PasswordHash.recommended()

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

    @staticmethod
    def create_service_token(user: UserModelResponse) -> str:
        payload = ServiceTokenPayload(
            sub=str(user.id),
            username=user.username,
        )
        return jwt.encode(payload.model_dump(), settings.SECRET_KEY, settings.ALGORITHM)

    @staticmethod
    def get_service_token_payload(encoded_token: str) -> ServiceTokenPayload:
        try:
            payload = ServiceTokenPayload(**jwt.decode(encoded_token, settings.SECRET_KEY, settings.ALGORITHM))
            if payload.type != TokenTypes.SERVICE:
                raise TokenException(payload.type, TokenErrors.WRONG_TOKEN_TYPE)
            return payload
        except ExpiredSignatureError:
            raise TokenException(TokenTypes.SERVICE, TokenErrors.EXPIRED)
        except JWTError as e:
            raise TokenException(TokenTypes.SERVICE, TokenErrors.INVALID_DATA) from e
