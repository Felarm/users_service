import secrets
from asyncio import to_thread

from pwdlib import PasswordHash


class SecurityService:
    pwd_context = PasswordHash.recommended()

    @classmethod
    async def verify_password(cls, input_password: str, hashed_password: str) -> bool:
        return await to_thread(cls.pwd_context.verify, input_password, hashed_password)

    @classmethod
    async def hash_password(cls, input_password: str) -> str:
        return await to_thread(cls.pwd_context.hash, input_password)

    @classmethod
    async def generate_n_hash_password(cls) -> str:
        random_chars = secrets.token_hex(16)
        return await to_thread(cls.pwd_context.hash,random_chars)

    @classmethod
    async def generate_service_password(cls) -> tuple[str, str]:
        random_long_password = secrets.token_hex(32)
        hashed_long_password = await to_thread(cls.pwd_context.hash, random_long_password)
        return random_long_password, hashed_long_password
