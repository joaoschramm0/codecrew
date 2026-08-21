import json

from backend.app.integrations.openrouter import request_json

MATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "aderencia": {"type": "integer", "minimum": 0, "maximum": 100},
        "resumo": {"type": "string"},
        "pontos_fortes": {"type": "array", "items": {"type": "string"}},
        "lacunas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "requisito": {"type": "string"},
                    "evidencia": {"type": "string"},
                    "prioridade": {
                        "type": "string",
                        "enum": ["alta", "media", "baixa"],
                    },
                },
                "required": ["requisito", "evidencia", "prioridade"],
                "additionalProperties": False,
            },
        },
        "focos_de_preparacao": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "aderencia", "resumo", "pontos_fortes", "lacunas",
        "focos_de_preparacao",
    ],
    "additionalProperties": False,
}

MATCH_PROMPT = """
Compare o currículo estruturado do candidato com a vaga. Use apenas evidências
presentes nos dados. A ausência de uma habilidade no currículo é uma lacuna de
evidência, não prova de que o candidato não a possui.

Produza uma avaliação prática para orientar a preparação da entrevista:
- aderência geral de 0 a 100;
- pontos fortes sustentados pelo currículo;
- lacunas ligadas a requisitos da vaga, com prioridade;
- focos de preparação específicos e acionáveis.

CURRÍCULO
{candidate}

VAGA
{job}
"""


def analyze_match(candidate: dict, job: dict) -> dict:
    if not candidate:
        raise ValueError("O perfil do candidato está vazio.")
    if not job:
        raise ValueError("Os dados da vaga estão vazios.")

    prompt = MATCH_PROMPT.format(
        candidate=json.dumps(candidate, indent=2, ensure_ascii=False),
        job=json.dumps(job, indent=2, ensure_ascii=False),
    )
    return request_json(
        messages=[{"role": "user", "content": prompt}],
        schema=MATCH_SCHEMA,
        schema_name="aderencia_candidato_vaga",
    )
