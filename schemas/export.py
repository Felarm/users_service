import json

from pydantic import BaseModel

from main import app
from schemas.token import AccessTokenPayload, RefreshTokenPayload, TokenModelResponse, RefreshTokenRequest, \
    TokenExceptionContent
from schemas.user import UserFromTg


class ContractRegistry(BaseModel):
    access_token_payload: AccessTokenPayload
    refresh_token_payload: RefreshTokenPayload
    token_model_response: TokenModelResponse
    refresh_token_request: RefreshTokenRequest
    token_exception_content: TokenExceptionContent

    user_tg_request: UserFromTg


@app.get("/__contracts", response_model=ContractRegistry, include_in_schema=False)
def __get_contracts():
    pass


if __name__ == "__main__":
    with open("openapi.json", "w") as f:
        json.dump(app.openapi(), f, indent=2)
    print("exported schemas to openapi.json")