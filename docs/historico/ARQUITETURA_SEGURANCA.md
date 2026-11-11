> DOCUMENTO HISTÓRICO DA V1. Não executar estas instruções. Substituído pela arquitetura DEMO de 11/11/2026 descrita no README atual.

# Arquitetura e Segurança

Este documento registra as decisões de arquitetura e segurança da Automação NF-e.

As decisões foram guiadas por documentação oficial e boas práticas do NIST, OWASP, Python, SQLite, Requests, GitHub e GestãoClick.

## Princípios

1. O GestãoClick continua sendo a fonte principal dos dados fiscais.
2. A automação não repete automaticamente operações de escrita críticas, como criar ou emitir NF-e.
3. Uma única instância da automação pode executar por vez na mesma máquina.
4. Dados vindos de API são tratados como entrada externa e precisam ser validados.
5. Segredos não ficam no código, no GitHub nem nos logs.
6. Integrações externas não podem derrubar o fluxo principal de NF-e.
7. Eventos de integração precisam ser idempotentes.
8. Dependências e CI fazem parte da superfície de ataque.

## Limites de confiança

```text
GestãoClick
    │
    │ HTTPS + tokens
    ▼
Automação NF-e
    │
    ├── SQLite local
    ├── XML/PDF local
    ├── logs estruturados
    └── fila de eventos
              │
              │ HTTPS + HMAC
              ▼
       Gerente de Estoque
```

Cada passagem entre sistemas é tratada como fronteira de confiança.

## GestãoClick

A integração real deve usar:

- HTTPS;
- Access Token e Secret Access Token;
- uma chave exclusiva da automação;
- validade definida;
- menor privilégio possível;
- usuário e loja corretos;
- restrição de horário e IP quando aplicável;
- paginação e limites de requisição definidos no OpenAPI da conta.

A criação e a emissão de NF-e são operações críticas e não recebem retry automático.

Se a criação funcionar e a emissão falhar ou der timeout, o ID externo da nota permanece salvo para consulta antes de qualquer nova tentativa.

## SQLite

A V1 usa SQLite porque a automação roda localmente em uma máquina.

Aplicamos:

- foreign keys;
- busy timeout;
- synchronous FULL;
- consultas parametrizadas;
- bloqueio de execução concorrente.

O modo WAL não é ativado nesta V1.

Além de não ser necessário para uma automação de um único processo, a documentação do SQLite registra um problema de concorrência em WAL corrigido nas versões mais recentes. Caso a arquitetura passe a ter múltiplos processos ou máquinas, a decisão correta será reavaliar o banco, e não simplesmente compartilhar o arquivo SQLite.

SQLite nunca deve ser colocado em uma pasta de rede para múltiplas máquinas escreverem nele.

## Execução única

A aplicação usa um lock de arquivo local.

Se o Agendador de Tarefas iniciar uma segunda execução antes da primeira terminar:

```text
execução A → continua
execução B → bloqueada
```

Isso reduz risco de duas chamadas simultâneas tentando emitir a mesma NF-e.

## HTTP

Chamadas externas possuem:

- timeout de conexão;
- timeout de leitura;
- validação TLS padrão do Requests;
- HTTPS obrigatório;
- redirects bloqueados;
- nenhum retry automático em POST fiscal.

Bloquear redirects é especialmente importante porque a autenticação do GestãoClick usa cabeçalhos customizados.

## Webhook do Gerente de Estoque

A integração futura usa:

- HTTPS obrigatório;
- HMAC-SHA256;
- timestamp assinado;
- event ID;
- idempotência;
- fila local de reenvio;
- token Bearer opcional como camada adicional.

O Gerente deverá verificar a assinatura usando comparação em tempo constante, rejeitar timestamps antigos e ignorar event IDs já processados.

O payload não contém CPF/CNPJ, XML, PDF, tokens ou senhas.

## Logs

Os logs são estruturados em JSON.

São registrados eventos operacionais relevantes, sem gravar:

- tokens;
- senhas;
- conteúdo completo de requisições;
- XML/PDF;
- dados pessoais desnecessários.

Entradas de texto são limitadas e quebras de linha são neutralizadas para reduzir risco de log injection.

## Supply chain e CI

O workflow do GitHub possui:

- permissão somente de leitura;
- actions fixadas em commit SHA;
- dependências Python fixadas por versão;
- auditoria de vulnerabilidades com pip-audit;
- testes automatizados;
- limite de tempo da execução.

Dependabot monitora:

- pacotes Python;
- GitHub Actions.

## Quando deixar de usar SQLite

Migrar para PostgreSQL ou outro banco central quando ocorrer um destes cenários:

- mais de uma máquina executando a automação;
- vários usuários escrevendo diretamente;
- aplicação web central;
- necessidade de alta disponibilidade;
- volume/concor­rência incompatível com o modelo local.

Nesse estágio, a emissão deve continuar centralizada em um único serviço responsável pela NF-e.

## Controles do computador de produção

Antes de produção:

- usar uma conta Windows exclusiva ou com privilégio mínimo;
- aplicar permissões NTFS apenas aos usuários necessários;
- manter Windows e Python atualizados;
- habilitar criptografia de disco, como BitLocker, quando disponível;
- proteger o arquivo `.env`;
- impedir sincronização pública das pastas `data/` e `logs/`;
- manter antivírus/EDR ativo;
- configurar backup do histórico;
- revisar periodicamente logs e falhas.

## Referências oficiais

- NIST SSDF: https://csrc.nist.gov/projects/ssdf
- NIST SP 800-218: https://csrc.nist.gov/pubs/sp/800/218/final
- OWASP Webhook Security Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Webhook_Security_Cheat_Sheet.html
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- OWASP Input Validation Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- SQLite WAL: https://sqlite.org/wal.html
- SQLite PRAGMA: https://sqlite.org/pragma.html
- Requests: https://requests.readthedocs.io/en/stable/
- GitHub Actions secure use: https://docs.github.com/en/actions/reference/security/secure-use
- GestãoClick API: https://gestaoclick.com.br/integracoes/api/
