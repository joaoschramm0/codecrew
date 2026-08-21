from backend.app.schemas.preparation import ChallengeRecommendation, Question

DIFFICULTIES = ["Easy", "Medium", "Hard"]

def recommend_challenges(catalog: list[dict], tags: list[str], target: str, priority: str) -> list[ChallengeRecommendation]:
    target_index = DIFFICULTIES.index(target)
    desired = [DIFFICULTIES[max(0, target_index - 1)], target, DIFFICULTIES[min(2, target_index + 1)]]
    roles = ["aquecimento", "nível-alvo", "extensão"]
    remaining = [Question.model_validate(item) for item in catalog]
    selected = []
    tag_set = set(tags)
    for role, difficulty in zip(roles, desired):
        ranked = sorted(remaining, key=lambda item: (item.difficulty != difficulty, -len(tag_set.intersection(item.tags)), abs(DIFFICULTIES.index(item.difficulty) - DIFFICULTIES.index(difficulty)), item.slug))
        if not ranked:
            break
        challenge = ranked[0]
        remaining.remove(challenge)
        selected.append(ChallengeRecommendation(papel=role, prioridade_atendida=priority, justificativa=f"{role.capitalize()} para praticar {priority} com foco em {', '.join(challenge.tags)}.", desafio=challenge))
    return selected
