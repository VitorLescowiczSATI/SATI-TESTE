# SATI Backend

Backend inicial da SATI IA em `FastAPI`.

## O que esta aqui

- `app/main.py`
  Entrada da aplicacao
- `app/api/routes`
  Rotas iniciais (`health`, `auth`)
- `app/models`
  Modelos centrais da plataforma
- `app/services/auth_service.py`
  Login, criacao de sessao e logout
- `alembic/`
  Base para migrations

## Primeiro bootstrap local

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
alembic revision --autogenerate -m "init schema"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## Rodando com Docker

Da raiz do repositorio:

```powershell
docker compose up --build backend db
```

O backend sobe em `http://localhost:8000`.

## Estrategia de autenticacao

Auth propria com:

- `email + senha`
- senha com hash (`bcrypt`)
- sessao persistida em `user_sessions`
- cookie `httpOnly`
- usuario ligado a `tenant` via `membership`

Esse modelo e suficiente para:

- SATI admin
- tenant admin
- operacao
- viewer

Sem depender de provedor externo agora.
