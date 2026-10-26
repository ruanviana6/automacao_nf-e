# Guia de desenvolvimento

Este arquivo define a ordem sugerida para você escrever o projeto.

## Etapa 1 — Entender o fluxo

Antes de usar API, vamos trabalhar com dados fictícios em Python.

Você vai praticar:

- listas;
- dicionários;
- funções;
- condicionais;
- loops.

Primeiro objetivo:

```text
pegar venda fictícia
→ validar
→ mostrar resultado
```

## Etapa 2 — Validações

Arquivo principal:

`services/validacao.py`

Você escreverá funções como:

```python
validar_cliente()
validar_produtos()
validar_valores()
validar_venda()
```

A ideia é aprender a quebrar um problema grande em funções menores.

## Etapa 3 — Banco SQLite

Arquivo:

`database/database.py`

Objetivo:

- criar tabela;
- registrar nota;
- verificar se uma venda já foi processada.

Aqui você começa a praticar SQL dentro do Python.

## Etapa 4 — Arquivos

Arquivo:

`services/arquivos.py`

Objetivo:

- criar pastas;
- salvar XML/PDF;
- calcular idade do arquivo;
- apagar apenas arquivos locais vencidos.

## Etapa 5 — Logs

Arquivo:

`utils/logger.py`

Objetivo:

registrar coisas como:

```text
Venda 105 encontrada
Venda validada
NF autorizada
Erro ao processar venda 108
```

## Etapa 6 — Relatório

Arquivo:

`services/relatorio.py`

Primeiro podemos usar CSV.

Depois evoluímos para:

- pandas;
- openpyxl;
- Excel.

## Etapa 7 — E-mail

Arquivo:

`services/email_service.py`

Só entra quando relatório estiver funcionando.

## Etapa 8 — API GestãoClick

Arquivo:

`api/gestaoclick.py`

Somente aqui entraremos com:

- URL;
- autenticação;
- GET;
- POST;
- endpoints reais.

A lógica restante do projeto deve continuar funcionando sem grandes mudanças.

## Regra de estudo

Não tente terminar um arquivo inteiro de uma vez.

Vamos trabalhar assim:

1. entender o problema;
2. escrever uma função;
3. testar;
4. corrigir;
5. só então seguir para a próxima.
