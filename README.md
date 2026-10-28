# Automação NF-e

Projeto em Python para automatizar e organizar etapas do processo de emissão, acompanhamento e controle de NF-e, com preparação para futura integração com a API do GestãoClick.

O projeto nasceu a partir de um processo real: pedidos precisam ser analisados antes da emissão da nota, algumas situações exigem autorização, os arquivos precisam ser organizados e o histórico deve continuar disponível para consulta.

> Status: **em desenvolvimento**.  
> A lógica principal está sendo construída e testada com dados fictícios antes da conexão com o ambiente real.

---

## Objetivo

A primeira versão do sistema tem como objetivo:

- analisar pedidos antes da emissão da NF-e;
- aplicar regras de negócio automaticamente;
- registrar autorizações e histórico de processamento;
- salvar XML e PDF temporariamente;
- remover arquivos locais antigos de forma automática ou manual;
- manter informações importantes no banco de dados;
- preparar a base para integração com o GestãoClick;
- futuramente gerar relatórios e notificações por e-mail.

A proposta não é substituir o GestãoClick. O sistema funciona como uma camada de automação e controle em torno dos processos que hoje exigem trabalho manual.

---

## Regras atuais de emissão

Neste momento, o sistema considera as seguintes regras:

- apenas pedidos de clientes do Ceará seguem para este fluxo de NF-e;
- pedidos com status **Em separação** podem ser liberados;
- pedidos com status **Concretizada** podem ser liberados;
- pedidos com status **Em andamento** precisam de autorização;
- a autorização registra quem autorizou e quando isso aconteceu;
- situações fora das regras conhecidas são bloqueadas.

Essas regras estão separadas da futura integração com a API, facilitando alterações sem precisar refazer o sistema inteiro.

---

## Fluxo atual

```text
Pedido
  ↓
Identificação do cliente e status
  ↓
Validação das regras
  ↓
Autorização, quando necessária
  ↓
Liberado ou bloqueado
  ↓
Registro do processamento
  ↓
SQLite
```

Na evolução do projeto, o fluxo deve chegar a:

```text
GestãoClick
  ↓
Buscar pedido
  ↓
Validar regras
  ↓
Verificar emissão anterior
  ↓
Gerar NF-e
  ↓
Consultar resultado
  ↓
Salvar XML/PDF localmente
  ↓
Registrar histórico
  ↓
Limpeza local após 45 dias
  ↓
Relatório quinzenal
  ↓
E-mail
```

---

## O que já funciona

Até o momento, o projeto já possui:

- pedidos fictícios para desenvolvimento e testes;
- validação por estado do cliente;
- validação por status do pedido;
- autorização manual para pedidos em andamento;
- identificação de quem autorizou;
- registro de data e hora da autorização;
- uso de horário UTC internamente e horário local na exibição;
- banco SQLite para histórico dos processamentos;
- consulta dos registros salvos;
- criação automática das pastas de XML e PDF;
- salvamento de XML e PDF;
- identificação de arquivos expirados;
- limpeza automática de arquivos após **45 dias**;
- exclusão manual de arquivos locais;
- proteção para impedir que a exclusão manual atinja arquivos fora das pastas controladas;
- configurações centralizadas;
- separação entre conexão com o banco e operações relacionadas à NF-e.

---

## Armazenamento dos arquivos

Os XMLs e PDFs serão mantidos localmente por **45 dias**.

Após esse período:

```text
Arquivo local
  ↓
Limpeza automática
  ↓
Arquivo removido do computador
```

Essa remoção é somente local.

Ela **não cancela nem exclui a NF-e armazenada no GestãoClick**.

Também existe uma opção de exclusão manual para arquivos locais quando necessário.

---

## Organização do projeto

A estrutura foi separada por responsabilidade para permitir que o sistema cresça sem concentrar tudo em um único arquivo.

```text
automacao_nf-e/
│
├── api/
│   └── integração futura com o GestãoClick
│
├── config/
│   └── configurações compartilhadas
│
├── database/
│   ├── conexão com o banco
│   └── operações relacionadas à NF-e
│
├── services/
│   ├── pedidos e regras de negócio
│   ├── arquivos XML/PDF
│   ├── notas
│   ├── relatórios
│   └── e-mail
│
├── utils/
│   ├── data e hora
│   └── logs
│
├── data/
│   ├── xml/
│   └── pdf/
│
├── logs/
│
└── main.py
```

---

## Tecnologias utilizadas

O projeto utiliza principalmente:

- **Python** para a automação e regras de negócio;
- **SQLite** para histórico e controle local;
- **Pathlib** para gerenciamento de arquivos e pastas;
- **Datetime / ZoneInfo** para datas, horários e fuso;
- **Requests** para a futura comunicação com APIs.

Outras bibliotecas serão adicionadas conforme a necessidade real do projeto.

---

## Próximas etapas

As próximas evoluções previstas são:

1. integrar os caminhos dos XMLs e PDFs ao banco;
2. implementar logs com retenção de 45 dias;
3. melhorar o controle de duplicidade de NF-e;
4. implementar a camada de emissão de notas;
5. conectar o sistema à API oficial do GestãoClick;
6. substituir os pedidos fictícios por dados reais;
7. registrar quem efetivamente gerou cada NF-e;
8. criar relatório quinzenal;
9. automatizar o envio por e-mail;
10. ampliar testes e tratamento de erros;
11. realizar uma revisão específica de segurança antes do uso em produção.

---

## Visão de evolução

Este projeto começa pela automação de NF-e, mas foi estruturado para poder fazer parte de uma solução operacional maior no futuro.

Uma das possíveis evoluções é a integração com um **Gerente de Estoque Inteligente**, desenvolvido separadamente, capaz de utilizar dados de vendas e estoque para oferecer informações como:

- produtos com estoque baixo;
- risco de ruptura;
- excesso de estoque;
- previsão de vendas;
- cobertura em dias;
- sugestões de reposição;
- quanto comprar e quando comprar;
- mudanças no comportamento de venda;
- alertas e apoio à tomada de decisão;
- futuramente, apoio simples à expedição.

A ideia é que cada módulo possa evoluir separadamente e, quando fizer sentido, compartilhar a mesma base de integrações e dados.

---

## Desenvolvimento e aprendizado

Além de resolver um problema real, este projeto também faz parte de um processo de aprendizado prático.

Durante o desenvolvimento são trabalhados conceitos como:

- lógica de programação;
- funções;
- módulos e imports;
- organização de projetos;
- regras de negócio;
- APIs;
- JSON;
- banco de dados;
- arquivos;
- datas e horários;
- tratamento de erros;
- logs;
- testes;
- segurança;
- escalabilidade e manutenção de código.

A construção está sendo feita por etapas: primeiro a lógica é entendida e testada com dados fictícios, depois é integrada ao ambiente real.

---

## Observação

A integração real com o GestãoClick ainda será implementada e validada com a documentação oficial da API.

Antes de qualquer uso em produção, o projeto ainda passará por revisão de segurança, credenciais, permissões, dados sensíveis, prevenção de duplicidade e tratamento de falhas.

---

Consulte também o arquivo `GUIA_DESENVOLVIMENTO.md` para acompanhar a sequência de construção do projeto.
