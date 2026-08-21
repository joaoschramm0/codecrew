from sqlalchemy import create_engine

from backend.app.repositories.sessions import SqlSessionRepository
from backend.app.schemas.preparation import PreparationSession


def test_sql_repository_persists_complete_journey(tmp_path):
    repository = SqlSessionRepository(create_engine(f"sqlite:///{tmp_path / 'journey.db'}"))
    session = PreparationSession(
        job={"titulo": "Backend", "pre_requisitos": "Python", "responsabilidades": "APIs"},
        candidate={"nome": None, "resumo": "Dev", "habilidades": ["Python"], "experiencias": [], "formacao": []},
        match={"aderencia": 80, "resumo": "Boa aderência", "pontos_fortes": ["Python"], "lacunas": [], "focos_de_preparacao": ["APIs"]},
        algorithm_profile={"tags": ["array", "hash-table", "string"], "difficulty": "Medium"},
        diagnostic_questions=[
            {"id": "q1", "ordem": 1, "origem": "lacuna_presumida", "texto": "P1", "competencia": "A", "categoria": "competência da vaga", "nivel_esperado": "adequado", "importancia": "crítica", "rubrica": {"sinais_esperados": ["a", "b", "c"], "erros_conceituais": [], "nivel_esperado": "adequado"}},
            {"id": "q2", "ordem": 2, "origem": "lacuna_presumida", "texto": "P2", "competencia": "B", "categoria": "competência da vaga", "nivel_esperado": "adequado", "importancia": "importante", "rubrica": {"sinais_esperados": ["a", "b", "c"], "erros_conceituais": [], "nivel_esperado": "adequado"}},
            {"id": "q3", "ordem": 3, "origem": "competencia_declarada", "texto": "P3", "competencia": "C", "categoria": "competência da vaga", "nivel_esperado": "adequado", "importancia": "importante", "rubrica": {"sinais_esperados": ["a", "b", "c"], "erros_conceituais": [], "nivel_esperado": "adequado"}},
            {"id": "q4", "ordem": 4, "origem": "algoritmica", "texto": "P4", "competencia": "Algoritmos", "categoria": "raciocínio algorítmico", "nivel_esperado": "adequado", "importancia": "crítica", "rubrica": {"sinais_esperados": ["a", "b", "c"], "erros_conceituais": [], "nivel_esperado": "adequado"}},
        ],
    )
    repository.save(session)

    restored = repository.get(session.id)
    assert restored.id == session.id
    assert restored.diagnostic_questions[0].rubrica.sinais_esperados == ["a", "b", "c"]
