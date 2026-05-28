from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user_by_id(self, id_: int) -> Optional[User]:
        result = await self.db_session.execute(select(User).where(User.id == id_))
        return result.scalar_one_or_none()

    async def get_user_by_tg_id(self, tg_id: int) -> Optional[User]:
        result = await self.db_session.execute(select(User).where(User.tg_id == tg_id))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db_session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_all_users(self) -> Sequence[User]:
        result = await self.db_session.execute(select(User))
        return result.scalars().all()

    async def create_user(self, hashed_password: str, **kwargs) -> User:
        new_user = User(hashed_password=hashed_password, **kwargs)
        self.db_session.add(new_user)
        await self.db_session.commit()
        return new_user