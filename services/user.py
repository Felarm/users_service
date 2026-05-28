from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import ResourceNotFoundException, ValidationException, UnauthorizedException
from repositories.user import UserRepository
from schemas.user import UserFilter, UserModelResponse, UserCreate, UserFromTg, UserLogin
from services.security import PasswordService


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.repo = UserRepository(db_session)

    async def get_user_by(self, by_params: UserFilter) -> UserModelResponse:
        if by_params.id:
            user_obj = await self.repo.get_user_by_id(by_params.id)
        elif by_params.username:
            user_obj = await self.repo.get_user_by_username(by_params.username)
        elif by_params.tg_id:
            user_obj = await self.repo.get_user_by_tg_id(by_params.tg_id)
        else:
            raise ValidationException(f"Can't filter users with params: {by_params}")
        if not user_obj:
            raise ResourceNotFoundException(f"User not found with params: {by_params}")
        return UserModelResponse.model_validate(user_obj)

    async def get_all_users(self) -> list[UserModelResponse]:
        user_objs = await self.repo.get_all_users()
        return [UserModelResponse.model_validate(_) for _ in user_objs]

    async def register_new_user(self, create_data: UserCreate) -> UserModelResponse:
        existing_user = await self.repo.get_user_by_username(create_data.username)
        if existing_user:
            raise UnauthorizedException(f"{create_data.username} already exists")
        hashed_password = PasswordService.hash_password(create_data.password)
        new_user_obj = await self.repo.create_user(hashed_password, **create_data.model_dump(exclude={"password"}))
        return UserModelResponse.model_validate(new_user_obj)

    async def register_user_from_tg(self, create_data: UserFromTg) -> UserModelResponse:
        existing_user = await self.repo.get_user_by_tg_id(create_data.tg_id)
        if existing_user:
            raise UnauthorizedException(f"We already registered this user")
        hashed_password = PasswordService.generate_n_hash_password()
        new_user_obj = await self.repo.create_user(hashed_password, **create_data.model_dump(exclude={"password"}))
        return UserModelResponse.model_validate(new_user_obj)

    async def login_user_by_password(self, login_data: UserLogin) -> UserModelResponse:
        user_obj = await self.repo.get_user_by_username(login_data.username)
        if not user_obj:
            raise ResourceNotFoundException(f"No user with username '{login_data.username}' exists")
        if not PasswordService.verify_password(login_data.password, user_obj.hashed_password):
            raise UnauthorizedException(f"Password {login_data.password} is wrong")
        return UserModelResponse.model_validate(user_obj)
