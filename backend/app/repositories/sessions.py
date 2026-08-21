from threading import Lock
from typing import Protocol
from uuid import UUID
from sqlalchemy import Column, DateTime, MetaData, String, Table, Text, create_engine, select
from sqlalchemy.engine import Engine

from backend.app.exceptions import PreparationNotFoundError
from backend.app.schemas import PreparationSession


class SessionRepository(Protocol):
    def save(self, session: PreparationSession) -> PreparationSession: ...

    def get(self, session_id: UUID) -> PreparationSession: ...

metadata = MetaData()
preparations = Table("preparations", metadata, Column("id", String(36), primary_key=True), Column("created_at", DateTime(timezone=True), nullable=False), Column("status", String(40), nullable=False, index=True), Column("payload", Text, nullable=False))

class SqlSessionRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        metadata.create_all(engine)

    @classmethod
    def from_url(cls, url: str) -> "SqlSessionRepository":
        return cls(create_engine(url, pool_pre_ping=True))

    def save(self, session: PreparationSession) -> PreparationSession:
        values = {"id": str(session.id), "created_at": session.created_at, "status": session.status, "payload": session.model_dump_json()}
        with self._engine.begin() as connection:
            current = connection.execute(select(preparations.c.id).where(preparations.c.id == str(session.id))).first()
            statement = preparations.update().where(preparations.c.id == str(session.id)).values(**values) if current else preparations.insert().values(**values)
            connection.execute(statement)
        return session

    def get(self, session_id: UUID) -> PreparationSession:
        with self._engine.connect() as connection:
            row = connection.execute(select(preparations.c.payload).where(preparations.c.id == str(session_id))).first()
        if row is None:
            raise PreparationNotFoundError(f"Preparação {session_id} não encontrada.")
        return PreparationSession.model_validate_json(row.payload)


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
