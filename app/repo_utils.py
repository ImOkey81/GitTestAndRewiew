import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from git import Repo

SUPPORTED_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".c",
    ".cs",
    ".go",
    ".rs",
    ".php",
)


def _build_clone_candidates(url: str) -> list[str]:
    trimmed_url = url.strip().rstrip("/")
    parsed = urlparse(trimmed_url)

    candidates = [trimmed_url]

    if parsed.scheme in {"http", "https"} and parsed.netloc and not parsed.path.endswith(".git"):
        candidates.append(f"{trimmed_url}.git")

    deduped: list[str] = []
    for candidate in candidates:
        if candidate not in deduped:
            deduped.append(candidate)
    return deduped


def clone_repo(url: str) -> str:
    last_error = None
    for candidate_url in _build_clone_candidates(url):
        temp_dir = tempfile.mkdtemp(dir=os.getenv("TEMP_DIR"))
        try:
            Repo.clone_from(candidate_url, temp_dir)
            return temp_dir
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    raise RuntimeError(f"Failed to clone repository from URL: {url}") from last_error


def _max_file_size() -> int:
    return int(os.getenv("MAX_FILE_SIZE", 100_000))


def _max_files_to_analyze() -> int:
    return int(os.getenv("MAX_FILES_TO_ANALYZE", 200))


def load_all_code(path: str) -> dict[str, str]:
    base_path = Path(path)
    file_payloads: list[tuple[str, str]] = []
    max_file_size = _max_file_size()
    max_files = _max_files_to_analyze()

    for root, _, files in os.walk(path):
        for file_name in files:
            if not file_name.endswith(SUPPORTED_EXTENSIONS):
                continue

            full_path = Path(root) / file_name
            try:
                if full_path.stat().st_size > max_file_size:
                    continue

                content = full_path.read_text(encoding="utf-8", errors="ignore")
                relative_path = str(full_path.relative_to(base_path))
                file_payloads.append((relative_path, content))
            except (OSError, ValueError):
                continue

    file_payloads.sort(key=lambda item: item[0])
    limited_payloads = file_payloads[:max_files]
    return {file_path: content for file_path, content in limited_payloads}
