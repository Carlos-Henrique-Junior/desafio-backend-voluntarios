# API de Voluntários

Documentação funcional da API REST para cadastro e gerenciamento de voluntários.

## Acesso local

- Base URL: `http://localhost:8001`
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`
- OpenAPI: `http://localhost:8001/openapi.json`

## Modelo de dados

```json
{
  "name": "Ana Souza",
  "email": "ana@example.com",
  "telefone": "21999999999",
  "cargo_pretendido": "Desenvolvedora",
  "disponibilidade": "manha"
}
```

Valores permitidos para `disponibilidade`: `manha`, `tarde` ou `noite`.

Regras de validação dos campos:

- `name` e `cargo_pretendido`: 1 a 100 caracteres.
- `telefone`: 10 ou 11 dígitos numéricos.
- `email`: formato válido e exclusivo entre voluntários ativos (a comparação ignora maiúsculas).

## Endpoints

### GET `/`

Health check simples da aplicação.

Resposta `200`:

```json
{"message":"API funcionando!"}
```

### POST `/voluntarios`

Cadastra um voluntário. O e-mail deve ser válido e não pode pertencer a outro voluntário ativo; caso pertença, retorna `400`.

```bash
curl -X POST http://localhost:8001/voluntarios \
  -H 'Content-Type: application/json' \
  -d '{
    "name":"Ana Souza",
    "email":"ana@example.com",
    "telefone":"21999999999",
    "cargo_pretendido":"Desenvolvedora",
    "disponibilidade":"manha"
  }'
```

Resposta de sucesso: `201 Created`.

### GET `/voluntarios`

Lista voluntários ativos.

Filtros opcionais:

```text
GET /voluntarios?disponibilidade=manha&cargo=desenvolvedora
```

- `disponibilidade`: `manha`, `tarde` ou `noite`.
- `cargo`: filtra pelo cargo pretendido.

### GET `/voluntarios/{vol_id}`

Consulta um voluntário pelo identificador.

### PUT `/voluntarios/{vol_id}`

Atualiza os dados completos do voluntário. Use o mesmo corpo do POST. O e-mail informado não pode pertencer a outro voluntário ativo (`400`).

### DELETE `/voluntarios/{vol_id}`

Realiza a exclusão lógica do voluntário. O registro deixa de aparecer na listagem de ativos.

## Status HTTP

- `200`: consulta ou atualização concluída.
- `201`: voluntário criado.
- `204`: exclusão lógica concluída sem corpo de resposta.
- `400`: e-mail já registrado por outro voluntário ativo.
- `404`: voluntário não encontrado.
- `422`: e-mail, enum ou corpo inválido.
- `500`: erro interno; investigar logs do serviço.

## Execução

```bash
poetry install
poetry run uvicorn main:app --reload --port 8001
```

Testes automatizados:

```bash
poetry run pytest -q
```

## Segurança e operação

Valide todos os dados no servidor, mantenha os segredos fora do repositório, configure CORS com origens explícitas e adicione HTTPS, rate limiting e headers de segurança antes de publicar a API na internet.
