import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

from config import DBSettings
from interfaces import ISQLAlchemy
from main import app
from repositories import UserRepository, JobRepository
from storage.sqlalchemy.client import SqlAlchemyAsync
from tools.fixtures.users import UserFactory

env_file_name = ".env." + os.environ.get("STAGE", "test")
env_file_path = Path(__file__).parent.parent.resolve() / env_file_name
settings = DBSettings(_env_file=env_file_path)


@pytest.fixture
def test_app():
    yield app


@pytest_asyncio.fixture(scope="function")
async def sa_session(test_app):
    print("setttings = " + str(settings.pg_async_dsn))
    engine = create_async_engine(str(settings.pg_async_dsn))
    connection = await engine.connect()
    trans = await connection.begin()

    Session = sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)  # noqa
    session = Session()

    deletion = session.delete

    async def mock_delete(instance):
        insp = inspect(instance)
        if not insp.persistent:
            session.expunge(instance)
        else:
            await deletion(instance)

        return await asyncio.sleep(0)

    session.commit = MagicMock(side_effect=session.flush)
    session.delete = MagicMock(side_effect=mock_delete)

    @asynccontextmanager
    async def get_db():
        yield session


    session.commit = MagicMock(side_effect=session.flush)
    session.delete = MagicMock(side_effect=mock_delete)

    with test_app.container.db.override(get_db):
        yield

    session.rollback()
    session.close()


    # print("BEFORE YIELD")
    # try:
    #     #with app.container.db.override(get_db):
    #     #   yield
    #     yield session
    # finally:
    #     await session.close()
    #     print("AFTER YIELD")
    #     await trans.rollback()
    #     print("AFTER ROLLBACK")
    #     await connection.close()
    #     await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def user_repository(sa_session):
    repository = UserRepository(session=sa_session)
    yield repository


@pytest_asyncio.fixture(scope="function")
async def job_repository(sa_session):
    repository = JobRepository(session=sa_session)
    yield repository


# регистрация фабрик
@pytest_asyncio.fixture(scope="function", autouse=True)
def setup_factories(sa_session: AsyncSession) -> None:
    UserFactory.session = sa_session
