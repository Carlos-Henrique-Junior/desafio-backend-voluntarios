import pytest
from fastapi.testclient import TestClient

from main import create_app


TEST_API_TOKEN = "test-only-volunteer-api-token"


@pytest.fixture
def client(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    app = create_app(database_url, api_token=TEST_API_TOKEN)
    headers = {"Authorization": f"Bearer {TEST_API_TOKEN}"}
    with TestClient(app, headers=headers) as test_client:
        yield test_client


def payload_base(**overrides):
    payload = {
        "name": "Tester Silva",
        "email": "teste@exemplo.com",
        "telefone": "11999999999",
        "cargo_pretendido": "Analista de Dados",
        "disponibilidade": "manha",
    }
    payload.update(overrides)
    return payload


def test_criar_voluntario_valido(client):
    response = client.post("/voluntarios", json=payload_base())
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "teste@exemplo.com"


def test_nao_permitir_email_duplicado(client):
    payload = payload_base(email="duplicado@exemplo.com", cargo_pretendido="QA", disponibilidade="tarde")
    client.post("/voluntarios", json=payload)

    response = client.post("/voluntarios", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email já registado."


def test_email_duplicado_ignora_maiusculas(client):
    client.post("/voluntarios", json=payload_base())
    response = client.post("/voluntarios", json=payload_base(email="TESTE@exemplo.com"))
    assert response.status_code == 400


def test_campos_invalidos_retorna_422(client):
    response = client.post("/voluntarios", json=payload_base(name=""))
    assert response.status_code == 422

    response = client.post("/voluntarios", json=payload_base(telefone="12345"))
    assert response.status_code == 422

    response = client.post("/voluntarios", json=payload_base(disponibilidade="integral"))
    assert response.status_code == 422


def test_get_voluntario_inexistente_retorna_404(client):
    response = client.get("/voluntarios/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Voluntário não encontrado"


def test_listar_com_filtros(client):
    client.post("/voluntarios", json=payload_base())
    client.post(
        "/voluntarios",
        json=payload_base(
            email="outro@exemplo.com",
            cargo_pretendido="QA",
            disponibilidade="tarde",
        ),
    )

    response = client.get("/voluntarios", params={"disponibilidade": "manha"})
    assert response.status_code == 200
    assert [v["email"] for v in response.json()] == ["teste@exemplo.com"]

    response = client.get("/voluntarios", params={"cargo": "QA"})
    assert [v["email"] for v in response.json()] == ["outro@exemplo.com"]

    response = client.get("/voluntarios", params={"disponibilidade": "tarde", "cargo": "QA"})
    assert [v["email"] for v in response.json()] == ["outro@exemplo.com"]


def test_atualizar_voluntario(client):
    created = client.post("/voluntarios", json=payload_base()).json()

    response = client.put(
        f"/voluntarios/{created['id']}",
        json=payload_base(name="Tester Atualizado", cargo_pretendido="QA"),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["name"] == "Tester Atualizado"
    assert data["cargo_pretendido"] == "QA"
    assert data["created_at"] == created["created_at"]


def test_atualizar_proprio_email_permitido(client):
    created = client.post("/voluntarios", json=payload_base()).json()

    response = client.put(
        f"/voluntarios/{created['id']}",
        json=payload_base(name="Tester Silva Jr"),
    )
    assert response.status_code == 200


def test_atualizar_email_duplicado_retorna_400(client):
    client.post("/voluntarios", json=payload_base())
    other = client.post("/voluntarios", json=payload_base(email="outro@exemplo.com")).json()

    response = client.put(
        f"/voluntarios/{other['id']}",
        json=payload_base(email="teste@exemplo.com"),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email já registado."


def test_remover_voluntario(client):
    created = client.post("/voluntarios", json=payload_base()).json()

    response = client.delete(f"/voluntarios/{created['id']}")
    assert response.status_code == 204

    assert client.get(f"/voluntarios/{created['id']}").status_code == 404
    assert client.get("/voluntarios").json() == []
    assert client.put(f"/voluntarios/{created['id']}", json=payload_base()).status_code == 404
    assert client.delete(f"/voluntarios/{created['id']}").status_code == 404


def test_email_deletado_pode_ser_reutilizado(client):
    created = client.post("/voluntarios", json=payload_base(email="reuso@exemplo.com")).json()
    client.delete(f"/voluntarios/{created['id']}")

    response = client.post("/voluntarios", json=payload_base(email="reuso@exemplo.com"))
    assert response.status_code == 201
