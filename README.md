# SATI IA

Monorepo inicial da plataforma SATI IA.

## Estrutura

- `frontend/`
  App web em `React + Vite + TypeScript`. Por enquanto ele nasceu da tela de exploracao do runtime/configuracao por cliente e vai virar a base do painel autenticado.
- `backend/`
  API em `FastAPI`, com auth propria, multi-tenant simples e modelos centrais do produto.
- `docs/`
  Notas tecnicas de apoio ao desenvolvimento, incluindo o plano de migracao `NicoChat -> SATI`.
- `Sati Design System/`
  Referencia visual local, fora do escopo do app versionado.

## Decisoes ja refletidas no codigo

- `Render` como provedor inicial
- `React + Vite` no frontend
- `FastAPI` no backend
- `Postgres` como banco principal
- auth propria com sessao em `cookie httpOnly`
- multi-tenant por `tenant + membership`
- estados e runtime ficam no backend, nao em builder visual

## O que esta pronto nesta base

- semente real do `frontend`
- esqueleto do `backend`
- auth base:
  - `users`
  - `tenants`
  - `memberships`
  - `user_sessions`
- modelos iniciais do produto:
  - `leads`
  - `lead_profiles`
  - `conversations`
  - `messages`
  - `scheduled_jobs`
  - `crm_dispatches`
- estrutura de migrations com `Alembic`

## Proximo foco de produto

Em paralelo ao codigo, a proxima frente funcional continua sendo:

1. mapear a `Tenda RJ` no NicoChat
2. completar a matriz `NicoChat -> SATI`
3. transformar esse comportamento validado em:
   - `steps`
   - `policies`
   - `actions`
   - `lead profile`

Referencia de trabalho:

- `docs/mapeamento-nicochat-tenda.md`

## Docker local

O projeto agora tambem pode subir com Docker:

```powershell
docker compose up --build
```

Servicos previstos:

- `frontend`: [http://localhost:3000](http://localhost:3000)
- `backend`: [http://localhost:8000/health](http://localhost:8000/health)
- `postgres`: porta `5432`

## Deploy de teste no Render Free

O projeto esta preparado com Blueprint em:

- `render.yaml`

Esse deploy cria:

- `sati-frontend`: Static Site gratuito
- `sati-backend`: Web Service gratuito com Docker
- `sati-postgres`: Postgres gratuito

Importante:

- Render Free e bom para teste, nao producao.
- O Web Service gratuito dorme apos 15 minutos sem trafego.
- O Postgres gratuito expira apos 30 dias e nao tem backup.
- A senha do usuario inicial nao fica no codigo. Configure `SEED_ADMIN_PASSWORD` no Render.

Usuario inicial:

- Email: `vitor.lesco@satiia.com.br`
- Nome: `Vitor Lescowicz`
- Senha: configurar manualmente em `SEED_ADMIN_PASSWORD`

Fluxo:

1. criar um repositorio no GitHub
2. subir este monorepo
3. no Render, usar `New > Blueprint`
4. selecionar o repo
5. preencher `SEED_ADMIN_PASSWORD`
6. aplicar o Blueprint

## GitHub Actions

Pipeline inicial em:

- `.github/workflows/ci.yml`

Ela valida:

- build do frontend
- install + compile do backend
- build das imagens Docker de frontend e backend

## Setup sugerido

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .
alembic revision --autogenerate -m "init schema"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## Ordem pratica para amanha

1. fechar a traducao `NicoChat -> SATI`
2. completar `docs/mapeamento-nicochat-tenda.md` com os subfluxos reais
3. subir stack local com `docker compose up --build`
4. validar login/sessao
5. criar entidades do fluxo de entrada WhatsApp
6. so depois entrar no runtime conversacional
