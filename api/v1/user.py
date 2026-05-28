from fastapi import APIRouter, status, Depends

from dependencies import get_user_service, get_service_user_id
from schemas.user import UserModelResponse
from services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/all", response_model=list[UserModelResponse], status_code=status.HTTP_200_OK)
async def get_all_users(user_service: UserService = Depends(get_user_service), _: str = Depends(get_service_user_id)):
    return await user_service.get_all_users()
