import json
import re
import unicodedata

from backend.app.integrations.gupy import get_job
from backend.app.integrations.openrouter import request_json

TAGS = [
    "array", "string", "hash-table", "two-pointers", "sliding-window",
    "prefix-sum", "sorting", "binary-search", "recursion", "math", "greedy",
    "counting", "stack", "queue", "linked-list", "tree", "binary-tree",
    "graph", "heap-priority-queue", "matrix", "dynamic-programming",
    "backtracking", "depth-first-search", "breadth-first-search",
    "bit-manipulation", "design", "trie", "union-find", "database",
    "concurrency", "simulation", "string-matching",
]

SCHEMA = {
    "type": "object",
    "properties": {
        "tags": {
            "type": "array",
            "minItems": 3,
            "maxItems": 5,
            "items": {"type": "string", "enum": TAGS},
        },
        "difficulty": {"type": "string", "enum": ["Easy", "Medium", "Hard"]},
    },
    "required": ["tags", "difficulty"],
    "additionalProperties": False,
}

PROMPT = """
Você analisa uma vaga de tecnologia e decide quais tópicos de algoritmos e
estruturas de dados provavelmente apareceriam na entrevista técnica dela.

Não procure as tecnologias citadas na vaga (frameworks, bancos, ferramentas) —
elas não estão na lista de tópicos. Pense no tipo de problema que a pessoa
resolve no dia a dia e traduza isso para os tópicos disponíveis.

Exemplo: backend com muita manipulação de dados e otimização de consultas
sugere hash-table, string e array. Não sugere "django" nem "postgresql".

Escolha de 3 a 5 tópicos e a dificuldade adequada à senioridade da vaga.
Quando houver um diagnóstico do candidato, priorize as lacunas encontradas.

VAGA
título: {titulo}
pré-requisitos: {pre_requisitos}
responsabilidades: {responsabilidades}

DIAGNÓSTICO DO CANDIDATO
{match}
"""


def _plain_text(value: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", value.lower())
        if not unicodedata.combining(character)
    )


def set_difficulty(title: str, suggestion: str) -> str:
    normalized = _plain_text(title)
    words = set(re.findall(r"[a-z0-9]+", normalized))
    junior_terms = {"junior", "jr", "estagiario", "intern", "estagio"}
    senior_terms = {"senior", "sr", "especialista", "specialist", "lead"}

    if words & junior_terms:
        return "Easy"
    if words & senior_terms:
        return "Hard"
    if suggestion not in {"Easy", "Medium", "Hard"}:
        raise ValueError(f"Dificuldade inválida retornada pela LLM: {suggestion!r}")
    return suggestion


def llm_question(prompt: str, schema: dict) -> dict:
    return request_json(
        messages=[{"role": "user", "content": prompt}],
        schema=schema,
        schema_name="tags_vaga",
    )


def analyze_job(job: dict, match: dict | None = None) -> dict:
    missing = [field for field in ("titulo", "pre_requisitos", "responsabilidades")
               if field not in job]
    if missing:
        raise ValueError(f"Campos ausentes na vaga: {', '.join(missing)}")

    match_context = (
        json.dumps(match, indent=2, ensure_ascii=False)
        if match
        else "Não fornecido. Analise somente a vaga."
    )
    response = llm_question(PROMPT.format(**job, match=match_context), SCHEMA)
    raw_tags = response.get("tags")
    if not isinstance(raw_tags, list):
        raise ValueError("A LLM não retornou uma lista de tópicos.")

    tags = list(dict.fromkeys(tag for tag in raw_tags if tag in TAGS))
    if len(tags) < 3:
        raise ValueError("A LLM não retornou tópicos válidos suficientes.")

    return {
        "tags": tags,
        "difficulty": set_difficulty(job["titulo"], response.get("difficulty", "")),
    }


def job_analysis(url: str, match: dict | None = None) -> dict:
    job = get_job(url)
    return {"job": job, **analyze_job(job, match)}


if __name__ == "__main__":
    job_url = input("URL da vaga na Gupy: ").strip()
    print(json.dumps(job_analysis(job_url), indent=2, ensure_ascii=False))
