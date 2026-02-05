MAX_PROMPT_CHARS = 16_000


def build_repo_prompt(task_description: str, code_map: dict[str, str]) -> str:
    if not code_map:
        return (
            f"{task_description}\n\n"
            "Репозиторий не содержит поддерживаемых исходников для анализа. "
            "Верни краткий ответ об этом и предложи какие типы файлов добавить."
        )

    sections: list[str] = []
    for file_path, content in code_map.items():
        sections.append(f"### FILE: {file_path}\n```\n{content}\n```")

    project_context = "\n\n".join(sections)
    project_context = project_context[:MAX_PROMPT_CHARS]

    return (
        "Ты анализируешь репозиторий по предоставленным ниже файлам. "
        "НЕ проси пользователя прислать код, потому что он уже дан в запросе. "
        "Ссылайся на конкретные FILE-пути из контекста.\n\n"
        f"Задача: {task_description}\n\n"
        "Файлы репозитория:\n"
        f"{project_context}"
    )
