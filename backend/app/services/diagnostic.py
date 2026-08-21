from backend.app.schemas.preparation import DiagnosticAssessment, ReadinessResult

LEVELS = {"não demonstrado": 0, "básico": 1, "adequado": 2, "forte": 3}
WEIGHTS = {"de apoio": 1, "importante": 2, "crítica": 3}

def calculate_readiness(assessments: list[DiagnosticAssessment], curriculum_fit: int) -> ReadinessResult:
    reliable = [item for item in assessments if item.confianca in {"média", "alta"}]
    if len(reliable) < 3:
        return ReadinessResult(aderencia_curricular=curriculum_fit, prontidao_tecnica=None, indice_preparacao=None, evidencias_validas=len(reliable))
    total_weight = sum(WEIGHTS[item.importancia] for item in reliable)
    score = sum(min(LEVELS[item.nivel_observado] / LEVELS[item.nivel_esperado], 1) * WEIGHTS[item.importancia] for item in reliable) / total_weight
    technical = int(score * 100 + 0.5)
    return ReadinessResult(aderencia_curricular=curriculum_fit, prontidao_tecnica=technical, indice_preparacao=int((curriculum_fit + technical) / 2 + 0.5), evidencias_validas=len(reliable))
