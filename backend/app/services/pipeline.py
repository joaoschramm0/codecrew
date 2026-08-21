import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Integer, String, bindparam, create_engine, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.engine import Engine

from backend.app.integrations.gupy import get_job
from backend.app.services.algorithm_profile import analyze_job
from backend.app.services.cv_parser import process_cv
from backend.app.services.profile_matcher import analyze_match


load_dotenv()

QUESTION_QUERY = text(
    """
    SELECT slug, title, difficulty, tags, content_md
    FROM questions
    WHERE tags && :tags
      AND difficulty = :difficulty
    ORDER BY random()
    LIMIT :limit
    """
).bindparams(
    bindparam("tags", type_=ARRAY(String)),
    bindparam("difficulty", type_=String),
    bindparam("limit", type_=Integer),
)


def create_database_engine(database_url: str | None = None) -> Engine:
    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Defina DATABASE_URL para consultar os desafios.")
    return create_engine(url, pool_pre_ping=True)


def query_questions(
    tags: list[str],
    difficulty: str,
    limit: int = 10,
    *,
    db_engine: Engine | None = None,
) -> list[dict]:
    if not tags:
        raise ValueError("Informe ao menos um tópico para buscar desafios.")
    if difficulty not in {"Easy", "Medium", "Hard"}:
        raise ValueError(f"Dificuldade inválida: {difficulty!r}")
    if limit < 1 or limit > 100:
        raise ValueError("O limite deve estar entre 1 e 100.")

    active_engine = db_engine or create_database_engine()
    with active_engine.connect() as connection:
        result = connection.execute(
            QUESTION_QUERY,
            {"tags": tags, "difficulty": difficulty, "limit": limit},
        )
        return [dict(row._mapping) for row in result]


def build_preparation(
    job_url: str,
    *,
    cv_path: str | Path,
    question_limit: int = 10,
    db_engine: Engine | None = None,
) -> dict:
    job = get_job(job_url)
    candidate = process_cv(cv_path)
    match = analyze_match(candidate, job)
    algorithm_profile = analyze_job(job, match)
    questions = query_questions(
        algorithm_profile["tags"],
        algorithm_profile["difficulty"],
        question_limit,
        db_engine=db_engine,
    )

    return {
        "job": job,
        "candidate": candidate,
        "match": match,
        "algorithm_profile": algorithm_profile,
        "questions": questions,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monta uma preparação para a vaga.")
    parser.add_argument("job_url", nargs="?", help="URL pública da vaga na Gupy")
    parser.add_argument(
        "--cv", type=Path, required=True, help="Caminho para o currículo em PDF"
    )
    parser.add_argument("--limit", type=int, default=10, help="Quantidade de desafios")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    url = args.job_url or input("URL da vaga na Gupy: ").strip()
    result = build_preparation(url, cv_path=args.cv, question_limit=args.limit)
    print(json.dumps(result, indent=2, ensure_ascii=False))
