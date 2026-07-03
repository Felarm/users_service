import pytest

from users.repository import UserRepository


@pytest.fixture(scope="function")
def user_repo(db_session) -> UserRepository:
    return UserRepository(db_session)
