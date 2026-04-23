# Frontend slices

Esta pasta existe para a gente nao deixar o app crescer tudo dentro de `App.tsx`.

## Fatias previstas

- `auth/`
  login, sessao, guards de rota
- `leads/`
  lista, ficha e pipeline do lead
- `inbox/`
  conversa, takeover humano, timeline
- `runtime/`
  configuracoes por tenant, strategies e policies visiveis
- `settings/`
  tenant, CRM, assets, usuarios

## Regra pratica

Enquanto o produto ainda esta sendo descoberto, o `frontend` pode continuar com componentes compartilhados.
Quando uma tela ficar real, ela migra para uma dessas fatias.
