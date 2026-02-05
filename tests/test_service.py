from pathlib import Path

from app.prompting import build_repo_prompt
from app.repo_utils import load_all_code


def test_load_all_code_uses_relative_paths_and_supported_extensions(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('ok')", encoding="utf-8")
    (tmp_path / "README.md").write_text("ignored", encoding="utf-8")

    result = load_all_code(str(tmp_path))

    assert "src/main.py" in result
    assert "README.md" not in result


def test_build_repo_prompt_includes_files_and_instruction():
    code_map = {
        "app/main.py": "def run():\n    return 1",
        "tests/test_main.py": "def test_run():\n    assert True",
    }

    prompt = build_repo_prompt("Сделай ревью", code_map)

    assert "НЕ проси пользователя прислать код" in prompt
    assert "### FILE: app/main.py" in prompt
    assert "### FILE: tests/test_main.py" in prompt


def test_build_repo_prompt_when_repo_has_no_supported_files():
    prompt = build_repo_prompt("Сделай ревью", {})

    assert "не содержит поддерживаемых исходников" in prompt
