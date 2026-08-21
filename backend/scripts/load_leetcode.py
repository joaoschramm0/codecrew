import os
import time

import requests
from dotenv import load_dotenv
from markdownify import markdownify
from sqlalchemy import Column, MetaData, String, Table, create_engine
from sqlalchemy.dialects.postgresql import ARRAY, insert
from sqlalchemy.engine import Engine


LEETCODE = "https://leetcode.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
    ),
    "Content-Type": "application/json",
    "Referer": LEETCODE,
}

LIST_QUERY = """
query problemList($filters: QuestionListFilterInput, $limit: Int, $skip: Int) {
    problemsetQuestionList: questionList(
        categorySlug: ""
        filters: $filters
        limit: $limit
        skip: $skip
    ) {
        total: totalNum
        questions: data {
            title
            titleSlug
            difficulty
            isPaidOnly
        }
    }
}
"""

QUESTION_QUERY = """
query getQuestion($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        questionId
        title
        difficulty
        content
        topicTags { slug }
    }
}
"""


def create_questions_table(engine: Engine) -> Table:
    metadata = MetaData()
    questions = Table(
        "questions",
        metadata,
        Column("id", String, primary_key=True),
        Column("slug", String, unique=True),
        Column("title", String),
        Column("difficulty", String),
        Column("tags", ARRAY(String)),
        Column("content_md", String),
    )
    metadata.create_all(engine)
    return questions


def fetch_leetcode(query: str, variables: dict) -> dict | None:
    response = requests.post(
        f"{LEETCODE}/graphql",
        json={"query": query, "variables": variables},
        headers=HEADERS,
        timeout=30,
    )
    time.sleep(0.2)
    if response.ok:
        return response.json()
    print("HTTP", response.status_code, response.text[:500])
    return None


def list_free_question_slugs() -> list[str]:
    all_questions: list[dict] = []
    skip = 0
    total: int | None = None

    while total is None or skip < total:
        result = fetch_leetcode(
            LIST_QUERY,
            {"filters": {}, "limit": 100, "skip": skip},
        )
        if result is None:
            print("Falha ao carregar a página", skip)
            break

        page = result["data"]["problemsetQuestionList"]
        total = page["total"]
        all_questions.extend(page["questions"])
        skip += 100

    return [
        question["titleSlug"]
        for question in all_questions
        if not question["isPaidOnly"]
    ]


def load_questions(engine: Engine, questions_table: Table) -> None:
    for slug in list_free_question_slugs():
        result = fetch_leetcode(QUESTION_QUERY, {"titleSlug": slug})
        if result is None:
            print("Falha ao carregar a questão", slug)
            continue

        question = result["data"]["question"]
        if question is None or question["content"] is None:
            print("Questão sem conteúdo, ignorada:", slug)
            continue

        record = {
            "id": question["questionId"],
            "slug": slug,
            "title": question["title"],
            "difficulty": question["difficulty"],
            "tags": [tag["slug"] for tag in question["topicTags"]],
            "content_md": markdownify(question["content"]),
        }
        statement = insert(questions_table).values(**record).on_conflict_do_nothing(
            index_elements=["id"]
        )
        with engine.begin() as connection:
            connection.execute(statement)
        print("Inserido:", slug)


def main() -> None:
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("Defina DATABASE_URL para carregar os desafios.")

    engine = create_engine(database_url, pool_pre_ping=True)
    questions = create_questions_table(engine)
    load_questions(engine, questions)


if __name__ == "__main__":
    main()
