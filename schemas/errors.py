from enum import Enum
from typing import Literal

from pydantic import BaseModel

from schemas.auth_token import TokenTypes


class TokenErrors(str, Enum):
    EXPIRED = "expired token"
    INVALID_DATA = "invalid token"
    WRONG_TOKEN_TYPE = "wrong token type"


class TokenErrorContent(BaseModel):
    detail: str
    token_type: Literal[TokenTypes.ACCESS, TokenTypes.REFRESH, TokenTypes.SERVICE]
    error_type: Literal[TokenErrors.EXPIRED, TokenErrors.WRONG_TOKEN_TYPE, TokenErrors.INVALID_DATA]
