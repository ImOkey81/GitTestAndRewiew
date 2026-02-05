from fastapi.testclient import TestClient

from app.main import app


def test_analyze_returns_400_when_clone_fails(monkeypatch):
    monkeypatch.setattr("app.router.clone_repo", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("clone failed")))

    client = TestClient(app)
    response = client.post("/analyze", json={"repo_url": "https://example.com/repo"})

    assert response.status_code == 400
    assert "Could not clone repository" in response.json()["detail"]
