from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

PreparationStatus = Literal["criacao_em_processamento", "aguardando_diagnostico", "avaliacao_em_processamento", "pronta", "pronta_modo_degradado"]
ObservedLevel = Literal["não demonstrado", "básico", "adequado", "forte"]
Confidence = Literal["baixa", "média", "alta"]
Importance = Literal["de apoio", "importante", "crítica"]

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

class DiagnosticRubric(BaseModel):
    sinais_esperados: list[str] = Field(min_length=3, max_length=5)
    erros_conceituais: list[str]
    nivel_esperado: Literal["básico", "adequado", "forte"]

class PublicDiagnosticQuestion(BaseModel):
    id: str
    ordem: int = Field(ge=1, le=4)
    texto: str
    competencia: str
    categoria: Literal["competência da vaga", "raciocínio algorítmico"]

class DiagnosticQuestion(PublicDiagnosticQuestion):
    origem: Literal["lacuna_presumida", "competencia_declarada", "algoritmica"]
    nivel_esperado: Literal["básico", "adequado", "forte"]
    importancia: Importance
    rubrica: DiagnosticRubric

    def to_public(self) -> PublicDiagnosticQuestion:
        return PublicDiagnosticQuestion.model_validate(self.model_dump())

class DiagnosticAnswer(BaseModel):
    question_id: str
    tipo: Literal["texto", "nao_sei", "nao_se_aplica"]
    texto: str | None = None

    @model_validator(mode="after")
    def validate_content(self):
        if self.tipo == "texto":
            self.texto = (self.texto or "").strip()
            if not 1 <= len(self.texto) <= 1000:
                raise ValueError("A resposta deve conter entre 1 e 1.000 caracteres.")
        else:
            self.texto = None
        return self

class DiagnosticAssessment(BaseModel):
    question_id: str
    competencia: str
    nivel_observado: ObservedLevel
    nivel_esperado: Literal["básico", "adequado", "forte"]
    confianca: Confidence
    importancia: Importance
    evidencia_resumida: str
    classificacao: Literal["lacuna observada", "força observada"]
    proximo_foco: str

class ReadinessResult(BaseModel):
    aderencia_curricular: int
    prontidao_tecnica: int | None
    indice_preparacao: int | None
    evidencias_validas: int
    baseline: bool = True

class Priority(BaseModel):
    ordem: int
    competencia: str
    motivo: str
    proximo_passo: str

class ChallengeRecommendation(BaseModel):
    papel: Literal["aquecimento", "nível-alvo", "extensão"]
    prioridade_atendida: str
    justificativa: str
    desafio: Question

class MentorMessage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    role: Literal["assistant", "user"]
    content: str = Field(min_length=1, max_length=4000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Mentorship(BaseModel):
    challenge_slug: str
    help_stage: Literal["esclarecimento", "pista_conceitual", "direcao_concreta"] = "esclarecimento"
    messages: list[MentorMessage] = Field(default_factory=list)

class PreparationSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: PreparationStatus = "aguardando_diagnostico"
    job: JobData
    candidate: CandidateProfile
    match: MatchAnalysis
    algorithm_profile: AlgorithmProfile
    diagnostic_questions: list[DiagnosticQuestion] = Field(min_length=4, max_length=4)
    answers: dict[str, DiagnosticAnswer] = Field(default_factory=dict)
    assessments: list[DiagnosticAssessment] = Field(default_factory=list)
    readiness: ReadinessResult | None = None
    priorities: list[Priority] = Field(default_factory=list)
    recommendations: list[ChallengeRecommendation] = Field(default_factory=list)
    mentorships: dict[str, Mentorship] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_diagnostic_composition(self):
        origins = [item.origem for item in self.diagnostic_questions]
        if origins.count("lacuna_presumida") != 2 or origins.count("competencia_declarada") != 1 or origins.count("algoritmica") != 1:
            raise ValueError("A composição do diagnóstico deve conter duas lacunas, uma competência declarada e uma pergunta algorítmica.")
        if sorted(item.ordem for item in self.diagnostic_questions) != [1, 2, 3, 4]:
            raise ValueError("A ordem das perguntas diagnósticas é inválida.")
        return self

    def public_dump(self) -> dict:
        data = self.model_dump(exclude={"diagnostic_questions", "mentorships"})
        data["diagnostic_questions"] = [q.to_public().model_dump() for q in self.diagnostic_questions]
        return data

class PreparationPublic(BaseModel):
    id: UUID
    created_at: datetime
    status: PreparationStatus
    job: JobData
    candidate: CandidateProfile
    match: MatchAnalysis
    algorithm_profile: AlgorithmProfile
    diagnostic_questions: list[PublicDiagnosticQuestion]
    answers: dict[str, DiagnosticAnswer]
    assessments: list[DiagnosticAssessment]
    readiness: ReadinessResult | None
    priorities: list[Priority]
    recommendations: list[ChallengeRecommendation]

class AnswerRequest(BaseModel):
    tipo: Literal["texto", "nao_sei", "nao_se_aplica"]
    texto: str | None = None

    @model_validator(mode="after")
    def validate_content(self):
        validated = DiagnosticAnswer(
            question_id="request",
            tipo=self.tipo,
            texto=self.texto,
        )
        self.texto = validated.texto
        return self

class MentorRequest(BaseModel):
    challenge_slug: str
    message: str = Field(min_length=1, max_length=4000)

class MentorResponse(BaseModel):
    message: MentorMessage
    help_stage: str

class MentorshipPublic(BaseModel):
    challenge_slug: str
    help_stage: str
    messages: list[MentorMessage]
