from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    tg_id: Optional[int] = None


class UserFromTg(BaseModel):
    username: str
    tg_id: int


class UserLogin(BaseModel):
    username: str
    password: str


class UserFilter(BaseModel):
    id: Optional[int] = None
    tg_id: Optional[int] = None
    username: Optional[str] = None

    def __str__(self):
        return " ".join([f"{k}: {v}" for k, v in self.model_dump(exclude_none=True).items()])


class UserModelResponse(UserBase):
    id: int
    is_service: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    tg_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
