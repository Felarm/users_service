from enum import Enum
from typing import Optional, Literal

from pydantic import BaseModel


class TokenTypes(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    SERVICE = "service"


class AccessTokenPayload(BaseModel):
    sub: str
    username: str
    tg_id: Optional[int] = None
    exp: int  # timestamp expires
    iat: int  # timestamp issued at
    type: str = TokenTypes.ACCESS


class ServiceTokenPayload(BaseModel):
    sub: str
    username: str
    type: str = TokenTypes.SERVICE


class TokenModelResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenErrors(str, Enum):
    EXPIRED = "expired token"
    INVALID_DATA = "invalid token"
    WRONG_TOKEN_TYPE = "wrong token type"


class TokenErrorContent(BaseModel):
    detail: str
    token_type: Literal[TokenTypes.ACCESS, TokenTypes.REFRESH, TokenTypes.SERVICE]
    error_type: Literal[TokenErrors.EXPIRED, TokenErrors.WRONG_TOKEN_TYPE, TokenErrors.INVALID_DATA]
