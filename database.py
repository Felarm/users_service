from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from config import settings


engine = create_async_engine(url=settings.db_url)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    def to_dict(self, exclude_none: bool = False) -> dict[str, Any]:
        """does not append NULL fields to result if exclude_none = True"""
        result = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, UUID):
                value = str(value)
            if not exclude_none or value is not None:
                result[column.key] = value
        return result