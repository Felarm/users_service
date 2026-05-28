from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionModel(BaseModel):
    id: int
    user_id: int
    jti: str
    expires_at: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
