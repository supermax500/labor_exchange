import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest
import pytest_asyncio
from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlalchemy import inspect, NullPool, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker, Session

from config import DBSettings
from dependencies.containers import RepositoriesContainer

from web.routers import auth_router, user_router, job_router, response_router
from fastapi import FastAPI

from dependency_injector import providers

from interfaces.i_sqlalchemy import ISQLAlchemy
from repositories import UserRepository, JobRepository
from repositories.response_repository import ResponseRepository

env_file_name = ".env." + os.environ.get("STAGE", "test")
env_file_path = Path(__file__).parent.parent.resolve() / env_file_name
settings = DBSettings(_env_file=env_file_path)


class StubSqlAlchemyAsync(ISQLAlchemy):
    def Session(self):  # noqa
        return None

    async def get_db(self):
        return None

    def _build_engine(self) -> AsyncEngine:
        return create_async_engine(str(settings.pg_async_dsn), echo=True)


@pytest_asyncio.fixture(scope="session")
async def client_app(sa_session):
    #di_container = TestContainer(sa_session=sa_session)

    di_container = RepositoriesContainer(db=providers.Factory(StubSqlAlchemyAsync))
    #di_container = RepositoriesContainer(db=providers.Factory(SqlAlchemyAsync, pg_settings=settings))
    print(f"conftest 62: client_app event loop id {id(asyncio.get_event_loop())}")
    di_container.user_repository.override(
        providers.Factory(
            UserRepository,
            session=sa_session,
        ),
    )
    di_container.job_repository.override(
        providers.Factory(
            JobRepository,
            session=sa_session,
        ),
    )
    di_container.response_repository.override(
        providers.Factory(
            ResponseRepository,
            session=sa_session,
        ),
    )

    app = FastAPI()
    app.container = di_container

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(job_router)
    app.include_router(response_router)

    return TestClient(app)


@pytest.fixture(scope="session")
def sa_session():
    print("test settings = " + str(settings.pg_sync_dsn))
    engine = create_engine(str(settings.pg_sync_dsn), poolclass=NullPool)
    connection = engine.connect()

    Session1 = sessionmaker(connection, expire_on_commit=False, class_=Session)  # noqa
    session = Session1()

    old_exec = session.execute
    old_flush = session.flush
    old_refresh = session.refresh
    old_delete = session.delete

    async def fake_execute(query, *args, **kwargs):
        result = old_exec(query, *args, **kwargs)
        return result

    async def fake_flush():
        previous_execute_mock = session.execute
        session.execute = old_exec
        old_flush()
        session.execute = previous_execute_mock

    async def fake_delete(obj):
        previous_execute_mock = session.execute
        session.execute = old_exec
        old_delete(obj)
        session.execute = previous_execute_mock

    async def fake_refresh(obj):
        previous_execute_mock = session.execute
        session.execute = old_exec
        old_refresh(obj)
        session.execute = previous_execute_mock


    session.refresh = MagicMock(side_effect=fake_refresh)
    session.execute = MagicMock(side_effect=fake_execute)
    session.flush = MagicMock(side_effect=fake_flush)
    session.commit = MagicMock(side_effect=session.flush)
    session.delete = MagicMock(side_effect=fake_delete)


    transaction = session.begin()

    class SessionWrapper:
        def __init__(self, session):
            self.session = session
        async def __aenter__(self):
            return self.session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return
        def __call__(self, *args, **kwargs):
            return self

    try:
        yield SessionWrapper(session)
    finally:
        transaction.rollback()
        session.close()
        connection.close()
        engine.dispose()


#@pytest_asyncio.fixture(scope="function")
# @pytest_asyncio.fixture(scope="session")
# async def sa_session():
#     print("AAAA")
#     print("test settings = " + str(settings.pg_async_dsn))
#     print("AAAA2")
#     engine = create_async_engine(str(settings.pg_async_dsn), echo=True, poolclass=NullPool)
#     connection = await engine.connect()
#     # trans = await connection.begin()
#
#     Session = sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)  # noqa
#     session = Session()
#
#     print("typeof session " + str(type(session)))
#
#     deletion = session.delete
#
#     async def mock_delete(instance):
#         insp = inspect(instance)
#         if not insp.persistent:
#             session.expunge(instance)
#         else:
#             await deletion(instance)
#
#         return await asyncio.sleep(0)
#
#     async def noop():
#         return
#     session.commit = MagicMock(side_effect=session.flush)
#     #session.commit = MagicMock(side_effect=noop)
#     #session.delete = MagicMock(side_effect=mock_delete)
#
#     # @asynccontextmanager
#     # async def get_db():
#     #     yield session
#
#     #session.commit = MagicMock(side_effect=session.flush)
#     #session.commit = MagicMock(side_effect=lambda: None)
#     #session.delete = MagicMock(side_effect=mock_delete)
#
#     transaction = await session.begin()
#     #with test_app.container.db.override(get_db):
#     #    yield
#
#     #session.rollback()
#     #session.close()
#
#     class SessionWrapper:
#         def __init__(self, session):
#             self.session = session
#         async def __aenter__(self):
#             print(f"conftest 141: A_ENTER event loop id {id(asyncio.get_event_loop())}")
#             return self.session
#         async def __aexit__(self, exc_type, exc_val, exc_tb):
#             return
#         def __call__(self, *args, **kwargs):
#             return self
#
#     print("BEFORE YIELD")
#     try:
#         #with app.container.db.override(get_db):
#         #   yield
#         #yield session
#         print(f"conftest 152: event loop id {id(asyncio.get_event_loop())}")
#         #yield Session
#         yield SessionWrapper(session)
#
#         print(f"conftest 155: event loop id {id(asyncio.get_event_loop())}")
#         #yield get_db
#     finally:
#         print("AFTER YIELD")
#
#         print(f"conftest 160: event loop id {id(asyncio.get_event_loop())}")
#         #await trans.rollback()
#         await transaction.rollback()
#         print("AFTER ROLLBACK")
#
#         await session.close()
#         await connection.close()
#         await engine.dispose()


# @pytest_asyncio.fixture(scope="function")
# async def user_repository(sa_session):
#     repository = UserRepository(session=sa_session)
#     yield repository
#
#
# @pytest_asyncio.fixture(scope="function")
# async def job_repository(sa_session):
#     repository = JobRepository(session=sa_session)
#     yield repository
#
#
# # регистрация фабрик
# @pytest_asyncio.fixture(scope="function", autouse=True)
# def setup_factories(sa_session: AsyncSession) -> None:
#     UserFactory.session = sa_session
