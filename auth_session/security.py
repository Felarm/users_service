import secrets

from pwdlib import PasswordHash


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
        random_chars = secrets.token_hex(16)
        return cls.pwd_context.hash(random_chars)

    @classmethod
    def generate_service_password(cls) -> tuple[str, str]:
        random_long_password = secrets.token_hex(32)
        hashed_long_password = cls.pwd_context.hash(random_long_password)
        return random_long_password, hashed_long_password
