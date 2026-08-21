from backend.app.schemas.preparation import (
    Confidence,
    DiagnosticAssessment,
    DiagnosticQuestion,
    Importance,
    ObservedLevel,
)
from backend.app.services.diagnostic import calculate_readiness


def assessment(level, expected, confidence="alta", importance="crítica"):
    return DiagnosticAssessment(
        question_id="q1",
        competencia="Python",
        nivel_observado=level,
        nivel_esperado=expected,
        confianca=confidence,
        importancia=importance,
        evidencia_resumida="Evidência.",
        classificacao="força observada",
        proximo_foco="Praticar.",
    )


def test_readiness_uses_weighted_capped_attainment():
    result = calculate_readiness([
        assessment("forte", "adequado"),
        assessment("básico", "adequado", importance="importante"),
        assessment("adequado", "adequado", importance="de apoio"),
    ], curriculum_fit=70)

    assert result.prontidao_tecnica == 83
    assert result.indice_preparacao == 77
    assert result.evidencias_validas == 3


def test_readiness_is_not_published_with_fewer_than_three_reliable_answers():
    result = calculate_readiness([
        assessment("forte", "adequado"),
        assessment("adequado", "adequado", confidence="baixa"),
    ], curriculum_fit=90)

    assert result.prontidao_tecnica is None
    assert result.indice_preparacao is None


def test_public_question_does_not_expose_rubric():
    question = DiagnosticQuestion(
        id="q1", ordem=1, texto="Como você faria?", competencia="Python",
        origem="lacuna_presumida",
        categoria="competência da vaga", nivel_esperado="adequado",
        importancia="crítica", rubrica={"sinais_esperados": ["x", "y", "z"],
        "erros_conceituais": ["w"], "nivel_esperado": "adequado"},
    )

    assert "rubrica" not in question.to_public().model_dump()
