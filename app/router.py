from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.analyzer import extract_summary
from app.repo_utils import clone_repo, load_all_code
from app.reviewer import review_code
from app.test_generator import generate_tests

router = APIRouter()


class RepoRequest(BaseModel):
    repo_url: str


@router.post("/analyze")
async def analyze_repo(req: RepoRequest):
    try:
        repo_path = clone_repo(req.repo_url)
        code_map = load_all_code(repo_path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not clone repository from provided URL. "
                "Please pass a direct git clone URL accessible from the service."
            ),
        ) from exc

    summary = extract_summary(code_map)
    tests = generate_tests(code_map)
    review = review_code(code_map)
    return {
        "summary": summary,
        "generated_tests": tests,
        "review": review,
    }
