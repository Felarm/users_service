import asyncio
from argparse import ArgumentParser

from database import async_session_maker
from models.user import User
from services.security import PasswordService, JWTService


async def create_service_user(username: str, password: str) -> None:
    async with async_session_maker() as db_session:
        hashed_password = PasswordService.hash_password(password)
        new_service_user = User(
            username=username,
            hashed_password=hashed_password,
            is_service=True
        )
        db_session.add(new_service_user)
        await db_session.commit()
        service_token_payload = JWTService._create_service_payload(new_service_user)
        print(JWTService._encode_jwt(service_token_payload))


def main():
    parser = ArgumentParser(description="CLI manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    service_user_p = subparsers.add_parser("create_service_user", help="Returns service token")
    service_user_p.add_argument("--username", required=True, help="Username")
    service_user_p.add_argument("--password", required=True, help="Password")

    args = parser.parse_args()
    if args.command == "create_service_user":
        asyncio.run(create_service_user(args.username, args.password))


if __name__ == "__main__":
    main()