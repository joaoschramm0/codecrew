from typing import Annotated
import os

from fastapi import Depends

from backend.app.repositories import InMemorySessionRepository, SqlSessionRepository
from backend.app.services.preparation import PreparationApplicationService


session_repository = SqlSessionRepository.from_url(os.environ["DATABASE_URL"]) if os.getenv("DATABASE_URL") else InMemorySessionRepository()


def get_session_repository() -> InMemorySessionRepository:
    return session_repository


def get_preparation_service(
    sessions: Annotated[
        InMemorySessionRepository,
        Depends(get_session_repository),
    ],
) -> PreparationApplicationService:
    return PreparationApplicationService(sessions)


PreparationServiceDependency = Annotated[
    PreparationApplicationService,
    Depends(get_preparation_service),
]
