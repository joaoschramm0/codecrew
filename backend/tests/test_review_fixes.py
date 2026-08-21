import pytest
from pydantic import ValidationError

from backend.app.repositories import InMemorySessionRepository
from backend.app.schemas.preparation import AnswerRequest, DiagnosticAnswer
from backend.app.services import preparation as preparation_module
from backend.app.services.preparation import PreparationApplicationService, advance_help_stage


def test_model_cannot_override_question_owned_metadata(monkeypatch, preparation_session):
    preparation_session.answers["q1"] = DiagnosticAnswer(question_id="q1", tipo="texto", texto="Minha resposta")
    monkeypatch.setattr(preparation_module, "request_json", lambda **_: {"assessments": [{
        "question_id": "q1", "competencia": "Competência inventada", "nivel_observado": "forte",
        "nivel_esperado": "básico", "confianca": "alta", "importancia": "de apoio",
        "evidencia_resumida": "Evidência", "classificacao": "força observada", "proximo_foco": "Praticar",
    }]})

    result = PreparationApplicationService(InMemorySessionRepository())._evaluate(preparation_session)

    assert result[0].competencia == "Python"
    assert result[0].nivel_esperado == "adequado"
    assert result[0].importancia == "crítica"


@pytest.mark.parametrize("text", ["   ", "x" * 1001])
def test_answer_request_rejects_invalid_text_with_validation_error(text):
    with pytest.raises(ValidationError):
        AnswerRequest(tipo="texto", texto=text)


def test_socratic_help_stage_never_regresses():
    assert advance_help_stage("direcao_concreta", "esclarecimento") == "direcao_concreta"


def test_processing_evaluation_can_be_retried(monkeypatch, preparation_session):
    repository = InMemorySessionRepository()
    preparation_session.status = "avaliacao_em_processamento"
    repository.save(preparation_session)
    service = PreparationApplicationService(repository)
    monkeypatch.setattr(service, "_evaluate", lambda _: [])

    result = service.retry(preparation_session.id)

    assert result.status == "pronta"
