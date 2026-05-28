from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TokenPayloadBase(BaseModel):
    sub: str
    username: str
    tg_id: Optional[int] = None
    exp: int  # timestamp expires
    iat: int  # timestamp issued at
    jti: str = Field(default_factory=lambda: str(uuid4()))


class RefreshTokenPayload(TokenPayloadBase):
    type: str = "refresh"


class AccessTokenPayload(TokenPayloadBase):
    type: str = "access"


class ServiceTokenPayload(BaseModel):
    sub: str
    username: str
    type: str = "service"


class TokenModelResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str