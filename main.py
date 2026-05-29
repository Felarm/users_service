import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from api.v1.auth import router as auth_router
from api.v1.user import router as users_router
from exceptions import BaseAppException, TokenException
from tasks import delete_expired_user_sessions


@asynccontextmanager
async def lifespan(app: FastAPI):
    delete_task = asyncio.create_task(delete_expired_user_sessions())
    yield
    delete_task.cancel()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(users_router)


@app.exception_handler(BaseAppException)
async def base_app_exc_handler(request: Request, exc: BaseAppException):
    logger.error(exc.msg)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.msg}
    )


@app.exception_handler(TokenException)
async def token_exc_handler(request: Request, exc: TokenException):
    logger.error(exc.msg)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.msg, "token type": exc.token_type, "error type": exc.err_type}
    )
