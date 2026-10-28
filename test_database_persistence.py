from fastapi.testclient import TestClient

from main import create_app


def test_volunteer_persists_across_app_restarts(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'volunteers.db'}"
    payload = {
        "name": "Persistência Voluntário",
        "email": "persistencia@example.com",
        "telefone": "21999999999",
        "cargo_pretendido": "Apoio",
        "disponibilidade": "manha",
    }

    with TestClient(create_app(database_url)) as first_client:
        created_response = first_client.post("/voluntarios", json=payload)
        assert created_response.status_code == 201
        volunteer_id = created_response.json()["id"]

    with TestClient(create_app(database_url)) as restarted_client:
        response = restarted_client.get(f"/voluntarios/{volunteer_id}")

    assert response.status_code == 200
    assert response.json()["email"] == payload["email"]
