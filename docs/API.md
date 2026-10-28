# API de Voluntários

Documentação funcional da API REST para cadastro e gerenciamento de voluntários.

## Acesso local

- Base URL: `http://localhost:8001`
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`
- OpenAPI: `http://localhost:8001/openapi.json`

## Autenticação

Todas as rotas `/voluntarios` exigem o cabeçalho `Authorization: Bearer <VOLUNTEER_API_TOKEN>`. Configure o token como segredo no ambiente da aplicação; sem ele, a aplicação falha ao iniciar. O `GET /` é um health check público e não retorna dados pessoais.

Exemplo local sem revelar o token:

```bash
curl http://localhost:8001/voluntarios \
  -H "Authorization: Bearer $VOLUNTEER_API_TOKEN"
```

O token é compartilhado e dá acesso administrativo a todos os registros. Não o coloque em aplicações de navegador, repositórios, logs ou mensagens.

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
- `401`: token Bearer ausente ou inválido.
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

As rotas CRUD agora exigem um único token Bearer administrativo; não há contas individuais, papéis ou cadastro público. Qualquer pessoa com o token pode acessar todos os registros. Mantenha `DATABASE_URL` e `VOLUNTEER_API_TOKEN` fora do repositório e configure-os como segredos na plataforma.

Isso ainda não é uma implementação completa de LGPD. Antes de usar dados reais ou publicar o backend, defina e implemente base legal e consentimento versionado, retenção e eliminação, solicitações dos titulares (acesso, correção, exclusão e revogação), aviso de privacidade e contato responsável. Também configure HTTPS, origens CORS explícitas, rate limiting, backups criptografados e proteção de logs.
