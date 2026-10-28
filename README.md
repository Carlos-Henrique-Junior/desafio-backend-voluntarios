# API de Gerenciamento de Voluntários 🤝

API REST desenvolvida com **FastAPI** e gerenciada via **Poetry** para o cadastro e controle de voluntários.

## 🚀 Tecnologias
- Python 3.13+
- FastAPI
- Pydantic
- Poetry (Gerenciamento de dependências)
- Pytest (Testes automatizados)

## ⚙️ Como Executar

### Pré-requisitos
Certifique-se de ter o [Poetry](https://python-poetry.org/docs/) instalado e um servidor PostgreSQL disponível. Crie o banco `voluntarios` e configure a variável `DATABASE_URL` antes de iniciar a API:

```bash
export DATABASE_URL="postgresql+psycopg://USUARIO:SENHA@localhost:5432/voluntarios"
export VOLUNTEER_API_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
```

Defina ambos localmente. Não versione nem compartilhe a URL ou o token; em produção, configure-os no gerenciador de segredos da plataforma.

1. **Instale as dependências:**
   ```bash
   poetry install
   ```


2. **Execute o servidor:**
   ```bash
   poetry run uvicorn main:app --reload --port 8001
   ```


3. **Acesse a documentação interativa:**
   Swagger UI: http://127.0.0.1:8001/docs

   ReDoc: http://127.0.0.1:8001/redoc

## 📚 Documentação da API

A referência completa dos endpoints, modelos, filtros, exemplos e códigos HTTP está em [`docs/API.md`](docs/API.md). A documentação interativa fica disponível em `/docs` e `/redoc` quando o servidor está em execução.

## 🔐 Autenticação e privacidade

Todas as rotas `/voluntarios` exigem `Authorization: Bearer $VOLUNTEER_API_TOKEN`. O health check `GET /` permanece público. A aplicação recusa iniciar se o token não estiver configurado. Este é um segredo administrativo compartilhado: não o embuta em site ou cliente público; qualquer pessoa que o possua pode consultar, criar, alterar e excluir registros.

Essa proteção não completa a conformidade LGPD. Base legal, consentimento versionado, retenção, atendimento a solicitações dos titulares e aviso de privacidade ainda precisam ser definidos antes de usar dados reais ou publicar o backend.

## 🧪 Como Testar
O projeto inclui testes automatizados para garantir a integridade dos dados. Eles usam um banco SQLite temporário; não é necessário ter PostgreSQL ativo para rodar a suíte.

```bash
poetry run pytest -q
```


| Método | Rota                | Descrição                                               |
| ------ | ------------------- | ------------------------------------------------------- |
| POST   | `/voluntarios`      | Cadastra um novo voluntário (validação de e-mail único) |
| GET    | `/voluntarios`      | Lista voluntários (filtros por cargo e disponibilidade) |
| GET    | `/voluntarios/{id}` | Obtém detalhes de um voluntário específico              |
| PUT    | `/voluntarios/{id}` | Atualiza os dados de um voluntário (valida e-mail único) |
| DELETE | `/voluntarios/{id}` | Remove um voluntário (soft delete)                      |
