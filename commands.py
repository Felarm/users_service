import asyncio
import json
from argparse import ArgumentParser

from loguru import logger

from database import async_session_maker
from main import app
from users.models import User
from auth_session.security import SecurityService


async def create_service_user(username: str, password: str) -> None:
    async with async_session_maker() as db_session:
        hashed_password = SecurityService.hash_password(password)
        new_service_user = User(
            username=username,
            hashed_password=hashed_password,
            is_service=True
        )
        db_session.add(new_service_user)
        await db_session.commit()
        service_token = SecurityService.create_service_token(new_service_user)
        logger.info(service_token)


def export_contracts():
    with open("openapi.json", "w") as f:
        json.dump(app.openapi(), f, indent=2)
    logger.info("exported schemas to openapi.json")



def main():
    parser = ArgumentParser(description="CLI manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    service_user_p = subparsers.add_parser("create_service_user", help="Returns service token")
    service_user_p.add_argument("--username", required=True, help="Username")
    service_user_p.add_argument("--password", required=True, help="Password")

    subparsers.add_parser("export_openapi")

    args = parser.parse_args()
    if args.command == "create_service_user":
        asyncio.run(create_service_user(args.username, args.password))
    elif args.command == "export_openapi":
        export_contracts()


if __name__ == "__main__":
    main()