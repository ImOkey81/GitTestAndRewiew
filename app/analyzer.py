from app.prompting import build_repo_prompt


def extract_summary(code_map: dict[str, str]) -> str:
    prompt = build_repo_prompt(
        task_description=(
            "Сделай структурированный обзор проекта: назначение, стек, главные модули, "
            "потоки данных и архитектурные риски."
        ),
        code_map=code_map,
    )
    from app.mistral_client import mistral_chat

    return mistral_chat(prompt)
