import asyncio

from loguru import logger

from database import async_session_maker
from repositories.session import SessionRepository


async def delete_expired_user_sessions() -> None:
    try:
        sleep_time_seconds = 60 * 60
        while True:
            logger.info("Task clear started")
            await asyncio.sleep(sleep_time_seconds)
            async with async_session_maker as db:
                session_repo = SessionRepository(db)
                await session_repo.delete_expired_sessions()
    except asyncio.CancelledError as e:
        logger.info("Task clear stopped")
        raise e