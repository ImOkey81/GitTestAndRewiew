from pathlib import Path

import pytest

from app.prompting import build_repo_prompt
from app.repo_utils import _build_clone_candidates, clone_repo, load_all_code


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


def test_build_clone_candidates_adds_git_suffix_for_web_urls():
    candidates = _build_clone_candidates("https://gitverse.ru/IAmOkey/WebAntTest")

    assert candidates == [
        "https://gitverse.ru/IAmOkey/WebAntTest",
        "https://gitverse.ru/IAmOkey/WebAntTest.git",
    ]


def test_clone_repo_retries_with_git_suffix(monkeypatch, tmp_path: Path):
    attempts: list[str] = []

    def fake_clone_from(url: str, path: str):
        attempts.append(url)
        if len(attempts) == 1:
            raise RuntimeError("first attempt failed")
        (Path(path) / "dummy").write_text("ok", encoding="utf-8")

    monkeypatch.setattr("app.repo_utils.Repo.clone_from", fake_clone_from)
    monkeypatch.setenv("TEMP_DIR", str(tmp_path))

    repo_path = clone_repo("https://gitverse.ru/IAmOkey/WebAntTest")

    assert Path(repo_path).exists()
    assert attempts == [
        "https://gitverse.ru/IAmOkey/WebAntTest",
        "https://gitverse.ru/IAmOkey/WebAntTest.git",
    ]


def test_clone_repo_raises_clear_error_when_all_attempts_fail(monkeypatch):
    def fake_clone_from(url: str, path: str):
        raise RuntimeError("fail")

    monkeypatch.setattr("app.repo_utils.Repo.clone_from", fake_clone_from)

    with pytest.raises(RuntimeError, match="Failed to clone repository"):
        clone_repo("https://example.com/org/repo")
