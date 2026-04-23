# Mapeamento NicoChat -> SATI (Plano de Trabalho)

> Objetivo desta nota:
> transformar o que hoje existe na `Tenda RJ` no `NicoChat` em uma especificacao clara para o primeiro MVP da SATI.

## Resultado esperado

Ao final deste mapeamento, precisamos sair com:

- um inventario dos fluxos e subfluxos da Tenda RJ
- uma traducao de cada bloco relevante para a linguagem da SATI
- uma definicao clara do que entra no `MVP-Real`
- uma lista separando:
  - comportamento validado
  - workaround do NicoChat
  - utilitario tecnico

## Regra principal

Nao copiar o NicoChat como arquitetura.

Copiar o comportamento validado e traduzir para:

- `etapa da conversa`
- `passo atual`
- `regra do atendimento`
- `acao do sistema`
- `dado estruturado`
- `saida para CRM`

## Ordem de mapeamento

### 1. Main Flow

Mapear:

- entrada principal
- roteamento inicial
- identificacao de origem
- registro inicial do lead
- chamada do fluxo principal

Perguntas para responder:

- o que esse fluxo decide?
- o que ele so encaminha?
- o que e regra de negocio?
- o que e so infraestrutura do NicoChat?

### 2. SDR Maju

Mapear:

- persona
- objetivo
- regras de memoria
- regras de conducao
- cenarios de primeira mensagem
- ordem da simulacao
- ordem da simulacao completa
- regra de agendamento
- regra de envio de imagens

Traducao esperada:

- persona + objetivo -> `modelo base / conducao`
- memoria -> `regras de retomada`
- fluxo comercial -> `passos da conversa`
- restricoes -> `regras do atendimento`

### 3. Funcoes de IA

Mapear cada uma:

- `simula`
- `simula_completo`
- `schedule_time`
- `images`

Para cada funcao, preencher:

- o que ela faz
- quando e chamada
- quais dados recebe
- o que devolve
- equivalente SATI

### 4. Tarefas de IA

Mapear:

- follow-up 15 min
- follow-up 1 hora
- follow-up 22 horas
- IA de coerencia comercial

Traducao esperada:

- follow-up -> `tarefas assincronas`
- coerencia comercial -> `resumo / classificacao / leitura comercial`

### 5. Subfluxos tecnicos

Mapear:

- `Dividir Texto em Blocos e Esperar Resposta com Audio`
- `Resumo da Conversa`
- `Integracao Imobilead` (ou equivalente)

Aqui o foco e separar:

- o que e utilitario tecnico
- o que e regra comercial real

## Estrutura da matriz bloco por bloco

Para cada bloco relevante, preencher:

| Origem NicoChat | Tipo | O que faz | Dado coletado | Regra aplicada | Acao disparada | Equivalente SATI | Entra no MVP? |
| --- | --- | --- | --- | --- | --- | --- | --- |

Tipos sugeridos:

- `roteamento`
- `pergunta`
- `condicao`
- `acao`
- `integracao`
- `follow-up`
- `utilitario tecnico`

## Traducoes padrao

Usar esta regra para manter consistencia:

- bloco de pergunta -> `passo atual`
- variavel salva -> `dado estruturado`
- condicao -> `regra do atendimento`
- envio de mensagem/imagem -> `acao do sistema`
- fluxo auxiliar -> `tarefa assincrona` ou `utilitario tecnico`
- subfluxo comercial -> `conducao / roteiro`

## O que entra primeiro no MVP

Prioridade 1:

- entrada do lead
- identificacao de origem
- SDR Maju
- simulacao inicial
- agendamento
- simulacao completa
- follow-up basico
- resumo da conversa
- saida para CRM

Prioridade 2:

- coerencia comercial mais sofisticada
- variacoes por empreendimento
- audio
- utilitarios tecnicos mais avancados

## Checklist da sessao de mapeamento

- [ ] abrir o `Main Flow`
- [ ] listar todos os subfluxos existentes
- [ ] mapear `SDR Maju`
- [ ] mapear `simula`
- [ ] mapear `simula_completo`
- [ ] mapear `schedule_time`
- [ ] mapear `images`
- [ ] mapear os follow-ups
- [ ] mapear `Resumo da Conversa`
- [ ] validar qual CRM/integracao esta sendo usado hoje
- [ ] separar o que entra no MVP do que fica para depois

## Saida final desejada

Ao terminar esse trabalho, a proxima etapa sera:

1. fechar a `strategy` da Tenda RJ
2. fechar os `passos da conversa`
3. fechar as `regras do atendimento`
4. fechar as `acoes do sistema`
5. implementar isso no backend e refletir no frontend
