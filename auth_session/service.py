import secrets
import string
from datetime import datetime, UTC

from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import SessionNotFoundException
from auth_session.repository import SessionRepository
from auth_session.schemas import SessionModel
from jwt.service import JWTService


class SessionService:
    def __init__(self, db_session: AsyncSession):
        self.repo = SessionRepository(db_session)

    async def create_session_for_user(self, user_id: int, refresh_token: str) -> SessionModel:
        refresh_payload = JWTService().get_refresh_token_payload(refresh_token)
        new_session = await self.repo.create_user_session(user_id, refresh_payload.jti, refresh_payload.exp)
        return SessionModel.model_validate(new_session)

    async def get_user_session_by_token(self, encoded_refresh_token: str) -> SessionModel:
        refresh_payload = JWTService().get_refresh_token_payload(encoded_refresh_token)
        current_session = await self.repo.get_session_by_jti(refresh_payload.jti)
        if current_session is None:
            raise SessionNotFoundException
        if current_session.expires_at < datetime.now(UTC):
            await self.revoke_user_session(current_session.id)
        return SessionModel.model_validate(current_session)

    async def revoke_user_session(self, user_session_id: int) -> None:
        await self.repo.delete_user_session(user_session_id)


class PasswordService:
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
