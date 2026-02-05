from app.prompting import build_repo_prompt


def generate_tests(code_map: dict[str, str]) -> str:
    prompt = build_repo_prompt(
        task_description=(
            "Сгенерируй набор релевантных unit-тестов по этому репозиторию. "
            "Выбери подходящий фреймворк по языку проекта и дай готовые тестовые файлы "
            "с именами и кодом."
        ),
        code_map=code_map,
    )
    from app.mistral_client import mistral_chat

    return mistral_chat(prompt)
