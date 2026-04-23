# Runtime SATI

Esta pasta vai concentrar o coracao do produto:

- `strategies/`
  ordem e logica comercial por operacao/cliente
- `policies/`
  regras puras e testaveis
- `actions/`
  verbos executaveis do runtime

O objetivo e evitar que a SATI vire outro builder de bloquinhos.
O comportamento validado da Tenda no NicoChat deve ser traduzido para essas tres camadas.
