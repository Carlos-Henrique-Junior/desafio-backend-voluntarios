from fastapi.testclient import TestClient
from main import app
from crud import reset_database

client = TestClient(app)

def setup_function():
    reset_database()

def payload_base(**overrides):
    payload = {
        "name": "Tester Silva",
        "email": "teste@exemplo.com",
        "telefone": "11999999999",
        "cargo_pretendido": "Analista de Dados",
        "disponibilidade": "manha"
    }
    payload.update(overrides)
    return payload

def test_criar_voluntario_valido():
    payload = {
        "name": "Tester Silva",
        "email": "teste@exemplo.com",
        "telefone": "11999999999",
        "cargo_pretendido": "Analista de Dados",
        "disponibilidade": "manha"
    }
    response = client.post("/voluntarios", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "teste@exemplo.com"

def test_nao_permitir_email_duplicado():
    payload = {
        "name": "Tester Duplicado",
        "email": "duplicado@exemplo.com",
        "telefone": "11999999999",
        "cargo_pretendido": "QA",
        "disponibilidade": "tarde"
    }
    # Cria o primeiro
    client.post("/voluntarios", json=payload)
    
    # Tenta criar o segundo igual
    response = client.post("/voluntarios", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email já registado."

def test_email_duplicado_ignora_maiusculas():
    client.post("/voluntarios", json=payload_base())
    response = client.post("/voluntarios", json=payload_base(email="TESTE@exemplo.com"))
    assert response.status_code == 400

def test_campos_invalidos_retorna_422():
    response = client.post("/voluntarios", json=payload_base(name=""))
    assert response.status_code == 422

    response = client.post("/voluntarios", json=payload_base(telefone="12345"))
    assert response.status_code == 422

    response = client.post("/voluntarios", json=payload_base(disponibilidade="integral"))
    assert response.status_code == 422

def test_get_voluntario_inexistente_retorna_404():
    response = client.get("/voluntarios/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Voluntário não encontrado"

def test_listar_com_filtros():
    client.post("/voluntarios", json=payload_base())
    client.post(
        "/voluntarios",
        json=payload_base(email="outro@exemplo.com", cargo_pretendido="QA", disponibilidade="tarde"),
    )

    response = client.get("/voluntarios", params={"disponibilidade": "manha"})
    assert response.status_code == 200
    assert [v["email"] for v in response.json()] == ["teste@exemplo.com"]

    response = client.get("/voluntarios", params={"cargo": "QA"})
    assert [v["email"] for v in response.json()] == ["outro@exemplo.com"]

    response = client.get("/voluntarios", params={"disponibilidade": "tarde", "cargo": "QA"})
    assert [v["email"] for v in response.json()] == ["outro@exemplo.com"]

def test_atualizar_voluntario():
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

def test_atualizar_proprio_email_permitido():
    created = client.post("/voluntarios", json=payload_base()).json()

    response = client.put(
        f"/voluntarios/{created['id']}",
        json=payload_base(name="Tester Silva Jr"),
    )
    assert response.status_code == 200

def test_atualizar_email_duplicado_retorna_400():
    client.post("/voluntarios", json=payload_base())
    other = client.post("/voluntarios", json=payload_base(email="outro@exemplo.com")).json()

    response = client.put(
        f"/voluntarios/{other['id']}",
        json=payload_base(email="teste@exemplo.com"),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email já registado."

def test_remover_voluntario():
    created = client.post("/voluntarios", json=payload_base()).json()

    response = client.delete(f"/voluntarios/{created['id']}")
    assert response.status_code == 204

    assert client.get(f"/voluntarios/{created['id']}").status_code == 404
    assert client.get("/voluntarios").json() == []
    assert client.put(f"/voluntarios/{created['id']}", json=payload_base()).status_code == 404
    assert client.delete(f"/voluntarios/{created['id']}").status_code == 404

def test_email_deletado_pode_ser_reutilizado():
    created = client.post("/voluntarios", json=payload_base(email="reuso@exemplo.com")).json()
    client.delete(f"/voluntarios/{created['id']}")

    response = client.post("/voluntarios", json=payload_base(email="reuso@exemplo.com"))
    assert response.status_code == 201
