> DOCUMENTO HISTÓRICO DA V1. Não executar estas instruções. Substituído pela arquitetura DEMO de 11/11/2026 descrita no README atual.

# Automação NF-e

Automação em Python criada para reduzir etapas manuais no processo de análise, emissão e controle de NF-e, preparada para integração com o GestãoClick e com outros módulos internos.

> **Status atual:** V1 funcional em modo de simulação.  
> A estrutura completa está pronta; falta conectar os endpoints e campos da API real do GestãoClick.

## O problema

Antes de uma NF-e ser emitida, o pedido precisa respeitar regras operacionais. Além disso, é necessário manter histórico, identificar autorizações, organizar XML/PDF, evitar emissão duplicada e gerar relatórios.

A proposta é automatizar esse fluxo sem substituir o GestãoClick. O ERP continua sendo a fonte principal das notas e dos dados; esta aplicação funciona como uma camada de automação e controle.

## Regras atuais

- somente clientes do Ceará seguem neste fluxo;
- **Em separação** pode gerar NF-e;
- **Concretizada** pode gerar NF-e;
- **Em andamento** exige autorização;
- a autorização registra pessoa e horário;
- pedidos com dados inválidos são bloqueados;
- uma nota já concluída para o pedido impede nova emissão automática no mesmo ambiente.

## Fluxo da V1

```text
Pedido
  ↓
Validação dos dados
  ↓
Regra de UF e status
  ↓
Autorização, quando necessária
  ↓
Proteção contra duplicidade
  ↓
Criar nota
  ↓
Emitir
  ↓
Registrar histórico
  ↓
Salvar XML/PDF
  ↓
Registrar evento de integração
  ↓
Limpeza local após 45 dias
  ↓
Relatório quinzenal
```

Hoje esse fluxo pode ser executado de ponta a ponta usando o provedor simulado. O mesmo contrato será ligado ao GestãoClick real.

## O que já está pronto

- regras de negócio dos pedidos;
- validação de cliente, produtos e valores;
- autorização de pedidos em andamento;
- registro de quem autorizou e quem executou;
- banco SQLite;
- tabelas separadas para processamentos, notas, arquivos e eventos de integração;
- proteção contra duplicidade;
- proteção contra nova criação quando uma nota ficou em estado incerto após falha/timeout;
- modo de simulação isolado do ambiente de produção;
- geração simulada de NF-e;
- salvamento de XML e PDF;
- retenção automática de 45 dias;
- exclusão manual segura;
- logs com retenção de 45 dias;
- relatório CSV;
- envio de relatório por e-mail;
- rotina quinzenal opcional;
- fila local de eventos para integração futura;
- reenvio de eventos que falharam;
- testes automatizados no GitHub Actions;
- cliente HTTP preparado para o GestãoClick;
- configurações e credenciais via `.env`.

## Estrutura

```text
automacao_nf-e/
├── api/
│   ├── gestaoclick.py
│   ├── mock_gestaoclick.py
│   └── provider.py
├── config/
│   └── settings.py
├── database/
│   ├── conexao.py
│   ├── integracao_repository.py
│   └── nfe_repository.py
├── integrations/
│   └── gerente_estoque.py
├── services/
│   ├── arquivos.py
│   ├── email_service.py
│   ├── eventos_integracao.py
│   ├── notas.py
│   ├── relatorio.py
│   ├── rotinas.py
│   ├── validacao.py
│   └── vendas.py
├── utils/
│   ├── data_hora.py
│   └── logger.py
├── tests/
├── data/
├── logs/
├── main.py
├── INTEGRACAO_GERENTE_ESTOQUE.md
└── SEGURANCA.md
```

## Instalação

```bash
pip install -r requirements.txt
```

Para desenvolvimento e testes:

```bash
pip install -r requirements-dev.txt
```

Copie o modelo de configuração:

```bash
cp .env.example .env
```

Enquanto a API real não estiver configurada:

```env
MODO_SIMULACAO=true
```

## Executar

Fluxo completo:

```bash
python main.py
```

Executar testes:

```bash
pytest
```

Listar XML/PDF locais:

```bash
python main.py --listar-arquivos
```

Forçar limpeza:

```bash
python main.py --limpar
```

Excluir um arquivo local específico:

```bash
python main.py --excluir-arquivo data/xml/nome_do_arquivo.xml
```

Gerar relatório:

```bash
python main.py --relatorio
```

Gerar e enviar relatório:

```bash
python main.py --enviar-relatorio
```

Reenviar eventos de integração pendentes:

```bash
python main.py --reenviar-eventos
```

## Retenção local

XML, PDF e logs permanecem localmente por **45 dias**.

A remoção local não cancela nem apaga a NF-e no GestãoClick.

## Relatório quinzenal

O envio automático fica desativado por padrão.

Depois de configurar o e-mail no `.env`, pode ser ativado com:

```env
EMAIL_ENVIO_AUTOMATICO=true
```

## Integração real com o GestãoClick

O arquivo `api/gestaoclick.py` já possui a base HTTP e o restante do sistema espera apenas estes métodos:

- buscar pedidos pendentes;
- criar nota;
- emitir nota;
- consultar nota;
- baixar XML;
- baixar PDF.

O provedor simulado implementa exatamente esse contrato. Por isso a conexão real pode ser feita sem reescrever o restante da aplicação.

## Pronto para integrar ao Gerente de Estoque

A automação já possui uma camada de integração separada.

Quando uma NF-e é concluída, um evento é salvo no SQLite. Se o Gerente de Estoque ainda estiver desligado, nada é perdido e a emissão continua normalmente.

Quando o gerente estiver pronto, basta configurar:

```env
INTEGRACAO_GERENTE_ATIVA=true
GERENTE_ESTOQUE_WEBHOOK_URL=
GERENTE_ESTOQUE_WEBHOOK_SECRET=
GERENTE_ESTOQUE_WEBHOOK_TOKEN=
```

O Gerente de Estoque poderá receber os eventos sem acessar o SQLite da automação e sem receber CPF/CNPJ, XML, PDF ou credenciais.

Consulte `INTEGRACAO_GERENTE_ESTOQUE.md` para o contrato inicial.

## Evolução futura

Esse mesmo padrão permite integrar futuramente outros serviços, como compras, expedição, relatórios ou notificações, sem colocar todas as regras dentro do mesmo arquivo ou banco.

## Segurança

Antes de ativar a API real, consulte `SEGURANCA.md` e `ARQUITETURA_SEGURANCA.md`.

Credenciais reais nunca devem ser enviadas para o GitHub.
