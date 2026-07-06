from fastapi import APIRouter, status, Depends

from dependencies import get_user_service, check_service_user
from users.schemas import UserModelResponse
from users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/all", response_model=list[UserModelResponse], status_code=status.HTTP_200_OK)
async def get_all_users(user_service: UserService = Depends(get_user_service), _: UserModelResponse = Depends(check_service_user)):
    return await user_service.get_all_users()
