from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class JobData(BaseModel):
    titulo: str
    pre_requisitos: str
    responsabilidades: str


class Experience(BaseModel):
    empresa: str | None
    cargo: str | None
    descricao: str


class CandidateProfile(BaseModel):
    nome: str | None
    resumo: str
    habilidades: list[str]
    experiencias: list[Experience]
    formacao: list[str]


class MatchGap(BaseModel):
    requisito: str
    evidencia: str
    prioridade: Literal["alta", "media", "baixa"]


class MatchAnalysis(BaseModel):
    aderencia: int = Field(ge=0, le=100)
    resumo: str
    pontos_fortes: list[str]
    lacunas: list[MatchGap]
    focos_de_preparacao: list[str]


class AlgorithmProfile(BaseModel):
    tags: list[str]
    difficulty: Literal["Easy", "Medium", "Hard"]


class Question(BaseModel):
    slug: str
    title: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    tags: list[str]
    content_md: str


class PreparationData(BaseModel):
    job: JobData
    candidate: CandidateProfile
    match: MatchAnalysis
    algorithm_profile: AlgorithmProfile
    questions: list[Question]


class PreparationSession(PreparationData):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class MentorMessage(BaseModel):
    role: Literal["assistant", "user"]
    content: str = Field(min_length=1, max_length=4000)


class MentorRequest(BaseModel):
    messages: list[MentorMessage] = Field(min_length=1, max_length=20)


class MentorResponse(BaseModel):
    message: str
