import pytest
from fastapi.testclient import TestClient

from main import create_app


TEST_API_TOKEN = "test-only-volunteer-api-token"
VOLUNTEER_PAYLOAD = {
    "name": "Pessoa de Teste",
    "email": "pessoa@example.com",
    "telefone": "21999999999",
    "cargo_pretendido": "Apoio",
    "disponibilidade": "manha",
}


def test_volunteer_crud_requires_bearer_token(tmp_path):
    app = create_app(
        database_url=f"sqlite:///{tmp_path / 'protected.db'}",
        api_token=TEST_API_TOKEN,
    )
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        responses = [
            client.get("/voluntarios"),
            client.get("/voluntarios/1"),
            client.post("/voluntarios", json=VOLUNTEER_PAYLOAD),
            client.put("/voluntarios/1", json=VOLUNTEER_PAYLOAD),
            client.delete("/voluntarios/1"),
        ]

    assert all(response.status_code == 401 for response in responses)
    assert all(response.headers["www-authenticate"] == "Bearer" for response in responses)


def test_valid_bearer_token_allows_volunteer_crud(tmp_path):
    app = create_app(
        database_url=f"sqlite:///{tmp_path / 'authorized.db'}",
        api_token=TEST_API_TOKEN,
    )
    headers = {"Authorization": f"Bearer {TEST_API_TOKEN}"}
    with TestClient(app, headers=headers) as client:
        created = client.post("/voluntarios", json=VOLUNTEER_PAYLOAD)
        assert created.status_code == 201
        assert client.get("/voluntarios").status_code == 200


def test_missing_api_token_fails_closed_at_startup(tmp_path, monkeypatch):
    monkeypatch.delenv("VOLUNTEER_API_TOKEN", raising=False)
    app = create_app(database_url=f"sqlite:///{tmp_path / 'missing-token.db'}")

    with pytest.raises(RuntimeError, match="VOLUNTEER_API_TOKEN"):
        with TestClient(app) as client:
            client.get("/")


def test_invalid_bearer_token_is_rejected(tmp_path):
    app = create_app(
        database_url=f"sqlite:///{tmp_path / 'invalid-token.db'}",
        api_token=TEST_API_TOKEN,
    )
    with TestClient(app, headers={"Authorization": "Bearer wrong-token"}) as client:
        response = client.get("/voluntarios")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
