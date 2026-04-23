# Exportar Fluxo TendaRJ do Nicochat

Esta nota define o processo prático para exportar o que existe hoje no Nicochat e transformar em insumo para o mapeamento `Nicochat -> SATI`.

## Objetivo

Exportar o máximo possível da configuração real da `Tenda RJ`, principalmente:

- subfluxos
- agentes de IA
- funções de IA
- tarefas/follow-ups
- campos de usuário
- campos do bot
- tags
- templates WhatsApp
- base de conhecimento/embeddings, se disponível
- conversas reais apenas quando forem necessárias para validar comportamento

## Regra de segurança

O token da API nunca deve entrar no Git.

Os arquivos brutos exportados ficam em `exports/nicochat/`, que está ignorado no `.gitignore`, porque podem conter dados sensíveis de leads e conversas.

## Pré-requisito

Criar uma chave de API no Nicochat com escopo suficiente para ler os fluxos. A documentação pública indica autenticação por `Bearer token` e endpoints sob `https://app.nicochat.com.br/api`.

Crie um arquivo local chamado `.env.nicochat` na raiz do projeto:

```env
NICOCHAT_TOKEN=cole_o_token_aqui
```

Esse arquivo não será commitado.

## Teste seco

Antes de chamar a API:

```powershell
python tools/nicochat_export.py --dry-run
```

Isso apenas lista os endpoints que o script tentará consultar.

## Primeira exportação segura

Rodar sem PII primeiro:

```powershell
python tools/nicochat_export.py --tenant-slug tenda-rj
```

Saída esperada:

```text
exports/nicochat/tenda-rj/YYYYMMDD-HHMMSS/
```

Dentro da pasta gerada haverá:

- `manifest.json`
- `README.md`
- um `.json` por endpoint consultado

## Exportação com dados sensíveis

Só usar se precisarmos analisar leads/conversas reais:

```powershell
python tools/nicochat_export.py --tenant-slug tenda-rj --include-pii
```

Esses arquivos não devem ser enviados para GitHub, Slack ou documentação pública.

## Parâmetros globais

Se o Nicochat exigir algum identificador extra, como `bot_ns`, `flow_ns`, `workspace_id` ou similar, use:

```powershell
python tools/nicochat_export.py --tenant-slug tenda-rj --param bot_ns=VALOR
```

Também é possível combinar parâmetros:

```powershell
python tools/nicochat_export.py --tenant-slug tenda-rj --param bot_ns=VALOR --param flow_ns=VALOR
```

## Exportar uma conversa específica

Se tivermos um `user_ns` de exemplo:

```powershell
python tools/nicochat_export.py --tenant-slug tenda-rj --user-ns USER_NS_AQUI
```

Se for conversa real, tratar como PII.

## Como usar o export

Depois da exportação:

1. abrir o `README.md` gerado
2. ver quais endpoints retornaram `ok`
3. abrir `flow_sub_flows.json` ou `flow_subflows_alt.json`
4. localizar `Main Flow`, `SDR Maju`, `Dividir Texto em Blocos`, `Resumo da Conversa`, `Integração Imobilead` e demais subfluxos
5. preencher `docs/mapeamento-nicochat-tenda.md`

## O que pode dar errado

- `401/403`: token sem permissão ou inválido
- `404`: endpoint com nome diferente para esta conta/versão
- `200` com lista vazia: endpoint existe, mas não há dados ou falta parâmetro global
- campos importantes ausentes: pode ser necessário capturar chamadas via DevTools do navegador dentro do editor do Nicochat

## Plano B: DevTools

Se a API pública não retornar os blocos internos do editor visual, usamos o navegador:

1. abrir o Nicochat na tela do fluxo da Tenda RJ
2. abrir DevTools `F12`
3. aba `Network`
4. filtrar por `flow`, `sub-flow`, `node`, `step`, `agent`, `task`
5. abrir `Main Flow` e subfluxos relevantes
6. salvar as respostas JSON das chamadas
7. colocar os arquivos brutos em `exports/nicochat/tenda-rj/devtools/`

## Fontes

- Documentação pública Nicochat API: https://nicochat.atlassian.net/wiki/spaces/NicoChat/pages/57081869/API
- Postman público Nicochat API: https://www.postman.com/gold-flare-846909/nicochat/documentation/0ro7scx/nicochat-api
- Mapeamento comunitário de endpoints Nicochat: https://socket.dev/npm/package/n8n-nodes-nicochat
