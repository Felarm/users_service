from typing import Optional

from pydantic import BaseModel


class AccessTokenPayload(BaseModel):
    sub: str
    username: str
    tg_id: Optional[int] = None
    exp: int  # timestamp expires
    iat: int  # timestamp issued at


class TokenModelResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
