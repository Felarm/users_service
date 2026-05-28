from datetime import datetime, UTC
from typing import Sequence, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.session import Session


class SessionRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user_session(self, user_id: int, jti: str, expires_timestamp: int) -> Session:
        new_obj = Session(
            user_id=user_id,
            jti=jti,
            expires_at=datetime.fromtimestamp(expires_timestamp, UTC),
        )
        self.db_session.add(new_obj)
        await self.db_session.commit()
        return new_obj

    async def get_user_sessions(self, user_id: int) -> Sequence[Session]:
        q = select(Session).where(Session.user_id == user_id)
        result = await self.db_session.execute(q)
        return result.scalars().all()

    async def get_session_by_jti(self, jti: str) -> Optional[Session]:
        q = select(Session).where(Session.jti == jti)
        result = await self.db_session.execute(q)
        return result.scalar_one_or_none()

    async def delete_user_session(self, session_id: int) -> None:
        q = delete(Session).where(Session.id == session_id)
        await self.db_session.execute(q)
        await self.db_session.commit()

    async def delete_expired_sessions(self) -> None:
        q = delete(Session).where(Session.expires_at < datetime.now(UTC))
        await self.db_session.execute(q)
        await self.db_session.commit()
