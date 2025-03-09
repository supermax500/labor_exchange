from dependency_injector import containers, providers

from interfaces.i_sqlalchemy import ISQLAlchemy
from repositories import JobRepository, UserRepository
from repositories.response_repository import ResponseRepository


class RepositoriesContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["web.routers", "dependencies"])

    db = providers.AbstractFactory(ISQLAlchemy)

    user_repository = providers.Factory(
        UserRepository,
        session=db.provided.get_db,
    )

    job_repository = providers.Factory(
        JobRepository,
        session=db.provided.get_db,
    )

    response_repository = providers.Factory(
        ResponseRepository,
        session=db.provided.get_db,
    )
