import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from redis.asyncio import Redis

from config import settings


class SessionStatus(str, Enum):
    active = "active"
    grace_period = "grace_period"


@dataclass
class SessionData:
    status: SessionStatus
    user_id: int | None = None
    new_token: str | None = None

    def to_dict(self) -> dict[str, int | str]:
        if self.user_id:
            return {"status": self.status, "user_id": self.user_id}
        elif self.new_token:
            return {"status": self.status, "new_token": self.new_token}
        else:
            raise KeyError("user_id or new_token should be specified")


class SessionRepository:
    def __init__(self, client: Redis):
        self.client = client
        self.prefix = "session:"

    async def create_session(self, user_id: int, refresh_token: str, ttl: int) -> None:
        key = f"{self.prefix}{refresh_token}"
        data = SessionData(status=SessionStatus.active, user_id=user_id).to_dict()
        await self.client.set(key, json.dumps(data), ex=ttl)

    async def get_session(self, refresh_token: str) -> Optional[SessionData]:
        key = f"{self.prefix}{refresh_token}"
        data = await self.client.get(key)
        return SessionData(**json.loads(data)) if data else None

    async def create_session_w_cooldown(
            self, old_refresh_token: str, new_refresh_token: str, user_id: int, new_ttl: int) -> None:
        old_key = f"{self.prefix}{old_refresh_token}"
        new_key = f"{self.prefix}{new_refresh_token}"
        old_data = SessionData(status=SessionStatus.grace_period, new_token=new_refresh_token).to_dict()
        new_data = SessionData(status=SessionStatus.active, user_id=user_id).to_dict()
        async with self.client.pipeline(transaction=True) as pipe:
            pipe.set(old_key, json.dumps(old_data), ex=settings.COOLDOWN_REFRESH_TIME)
            pipe.set(new_key, json.dumps(new_data), ex=new_ttl)
            await pipe.execute()
