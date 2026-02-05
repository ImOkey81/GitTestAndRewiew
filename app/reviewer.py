from app.prompting import build_repo_prompt


def review_code(code_map: dict[str, str]) -> str:
    prompt = build_repo_prompt(
        task_description=(
            "Проведи code review: найди потенциальные баги, проблемы надежности, "
            "безопасности, читаемости и производительности. Для каждого пункта укажи "
            "серьезность и предложи конкретное исправление."
        ),
        code_map=code_map,
    )
    from app.mistral_client import mistral_chat

    return mistral_chat(prompt)
