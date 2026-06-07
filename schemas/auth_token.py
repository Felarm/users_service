from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TokenTypes(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    SERVICE = "service"


class TokenPayloadBase(BaseModel):
    sub: str
    username: str
    tg_id: Optional[int] = None
    exp: int  # timestamp expires
    iat: int  # timestamp issued at
    jti: str = Field(default_factory=lambda: str(uuid4()))


class RefreshTokenPayload(TokenPayloadBase):
    type: str = TokenTypes.REFRESH


class AccessTokenPayload(TokenPayloadBase):
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
