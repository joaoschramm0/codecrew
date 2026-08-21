from backend.app.services.recommendations import recommend_challenges


CATALOG = [
    {"slug": "hard", "title": "Hard", "difficulty": "Hard", "tags": ["array", "hash-table"], "content_md": "H"},
    {"slug": "target", "title": "Target", "difficulty": "Medium", "tags": ["array", "hash-table"], "content_md": "T"},
    {"slug": "warm", "title": "Warm", "difficulty": "Easy", "tags": ["array"], "content_md": "W"},
    {"slug": "other", "title": "Other", "difficulty": "Medium", "tags": ["tree"], "content_md": "O"},
]


def test_recommendations_are_unique_deterministic_and_ordered_by_role():
    first = recommend_challenges(CATALOG, ["array", "hash-table"], "Medium", "Estruturas de dados")
    second = recommend_challenges(list(reversed(CATALOG)), ["array", "hash-table"], "Medium", "Estruturas de dados")

    assert [item.papel for item in first] == ["aquecimento", "nível-alvo", "extensão"]
    assert [item.desafio.slug for item in first] == ["warm", "target", "hard"]
    assert [item.desafio.slug for item in first] == [item.desafio.slug for item in second]
    assert len({item.desafio.slug for item in first}) == 3
