from threading import Lock
from typing import Protocol
from uuid import UUID

from backend.app.exceptions import PreparationNotFoundError
from backend.app.schemas import PreparationSession


class SessionRepository(Protocol):
    def save(self, session: PreparationSession) -> PreparationSession: ...

    def get(self, session_id: UUID) -> PreparationSession: ...


class InMemorySessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[UUID, PreparationSession] = {}
        self._lock = Lock()

    def save(self, session: PreparationSession) -> PreparationSession:
        with self._lock:
            self._sessions[session.id] = session
        return session

    def get(self, session_id: UUID) -> PreparationSession:
        with self._lock:
            session = self._sessions.get(session_id)

        if session is None:
            raise PreparationNotFoundError(
                f"Preparação {session_id} não encontrada."
            )
        return session
