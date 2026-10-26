# Automação NF-e

Projeto em Python para automatizar etapas do processo de emissão e controle de notas fiscais, preparado para futura integração com a API do GestãoClick.

## Objetivo de aprendizado

Este repositório não foi pensado apenas para "ter um código pronto".

A ideia é construir o sistema por etapas para praticar:

- funções;
- módulos e imports;
- APIs REST;
- JSON;
- tratamento de erros;
- banco SQLite;
- arquivos;
- datas;
- logs;
- automação;
- testes.

## Fluxo que queremos construir

```text
Venda
  ↓
Buscar dados
  ↓
Validar
  ↓
Verificar duplicidade
  ↓
Gerar NF-e
  ↓
Consultar status
  ↓
Salvar XML/PDF temporariamente
  ↓
Registrar histórico
  ↓
Excluir arquivo local após 30/90 dias
  ↓
Relatório a cada 15 dias
  ↓
E-mail
```

A API real do GestãoClick ficará isolada dentro da pasta `api/`. Assim podemos desenvolver a lógica principal antes de conectar o sistema real.

Consulte também: `GUIA_DESENVOLVIMENTO.md`.
