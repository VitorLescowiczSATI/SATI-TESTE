# SATI Frontend

Frontend inicial da SATI IA em `React + Vite + TypeScript`.

## Estado atual

Esta base nasceu da exploracao da `central de configuracao por cliente`.
Ela ainda funciona como painel conceitual, mas agora faz parte do app real e vai evoluir para:

- login autenticado
- leads
- inbox
- configuracoes por tenant
- operacao SATI

## Proximo passo recomendado

1. manter esta tela como referencia de configuracao/runtime
2. adicionar layout autenticado
3. criar paginas reais:
   - `Login`
   - `Leads`
   - `Inbox`
   - `Settings`
4. ligar o frontend ao `backend` da pasta vizinha

## Rodando com Docker

Da raiz do repositorio:

```powershell
docker compose up --build frontend
```

O frontend sobe em `http://localhost:3000`.
