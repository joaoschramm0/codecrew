import pytest

from backend.app.schemas.preparation import PreparationSession


@pytest.fixture
def preparation_session():
    return PreparationSession(
        job={"titulo": "Backend", "pre_requisitos": "Python", "responsabilidades": "APIs"},
        candidate={"nome": None, "resumo": "Dev", "habilidades": ["Python"], "experiencias": [], "formacao": []},
        match={"aderencia": 80, "resumo": "Boa aderência", "pontos_fortes": ["Python"], "lacunas": [], "focos_de_preparacao": ["APIs"]},
        algorithm_profile={"tags": ["array", "hash-table", "string"], "difficulty": "Medium"},
        diagnostic_questions=[
            {"id": "q1", "ordem": 1, "origem": "lacuna_presumida", "texto": "P1", "competencia": "Python", "categoria": "competência da vaga", "nivel_esperado": "adequado", "importancia": "crítica", "rubrica": {"sinais_esperados": ["a", "b", "c"], "erros_conceituais": [], "nivel_esperado": "adequado"}},
            {"id": "q2", "ordem": 2, "origem": "lacuna_presumida", "texto": "P2", "competencia": "APIs", "categoria": "competência da vaga", "nivel_esperado": "adequado", "importancia": "importante", "rubrica": {"sinais_esperados": ["a", "b", "c"], "erros_conceituais": [], "nivel_esperado": "adequado"}},
            {"id": "q3", "ordem": 3, "origem": "competencia_declarada", "texto": "P3", "competencia": "Testes", "categoria": "competência da vaga", "nivel_esperado": "adequado", "importancia": "importante", "rubrica": {"sinais_esperados": ["a", "b", "c"], "erros_conceituais": [], "nivel_esperado": "adequado"}},
            {"id": "q4", "ordem": 4, "origem": "algoritmica", "texto": "P4", "competencia": "Algoritmos", "categoria": "raciocínio algorítmico", "nivel_esperado": "adequado", "importancia": "crítica", "rubrica": {"sinais_esperados": ["a", "b", "c"], "erros_conceituais": [], "nivel_esperado": "adequado"}},
        ],
    )
