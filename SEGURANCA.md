# Segurança da Automação NF-e

Esta revisão registra as proteções já adotadas e os pontos que precisam ser conferidos antes de ativar a API real.

## Proteções já aplicadas

- credenciais ficam no arquivo `.env`, fora do Git;
- tokens, senhas, XML e PDF não são escritos nos logs;
- logs são estruturados em JSON e limitam entrada não confiável;
- SQL usa parâmetros;
- SQLite usa foreign keys, busy timeout e synchronous FULL;
- duas execuções simultâneas na mesma máquina são bloqueadas;
- o modo WAL não é habilitado na V1;
- HTTPS é obrigatório para GestãoClick e webhook;
- verificação TLS do Requests permanece habilitada;
- redirects HTTP são bloqueados nas integrações;
- conexão e leitura possuem timeouts separados;
- operações POST de criação/emissão não recebem retry automático;
- uma nota criada é persistida antes da emissão;
- emissão duplicada é bloqueada;
- integração com o Gerente usa HMAC-SHA256, timestamp e event ID;
- eventos são idempotentes e ficam persistidos para reenvio;
- falha no Gerente de Estoque não bloqueia NF-e;
- GitHub Actions usa permissões mínimas;
- actions do CI são fixadas por SHA;
- dependências Python são fixadas por versão;
- pip-audit verifica vulnerabilidades;
- Dependabot monitora dependências e GitHub Actions;
- XML/PDF e logs possuem retenção local de 45 dias.

## Antes de produção

1. Baixar e validar o OpenAPI da própria conta do GestãoClick.
2. Criar uma chave exclusiva da automação, com validade definida.
3. Usar usuário/loja com menor privilégio possível.
4. Aplicar restrição de IP, horário e permissões no GestãoClick quando aplicável.
5. Confirmar paginação, limites por segundo/dia e todos os status oficiais.
6. Manter `MODO_SIMULACAO=true` até concluir testes reais controlados.
7. Configurar `USUARIO_EXECUCAO`.
8. Aplicar permissões NTFS nas pastas da aplicação e no `.env`.
9. Usar criptografia de disco quando disponível.
10. Definir backup do SQLite e testar restauração.
11. Confirmar política interna de armazenamento de XML/PDF e envio de e-mail.
12. Testar timeout entre criação e emissão, rejeição e respostas 401/403/429/5xx.
13. Testar primeiro com poucos pedidos e conferir manualmente no GestãoClick.
14. Não automatizar cancelamento/reemissão até mapear os estados oficiais.
15. No Gerente de Estoque, validar HMAC com comparação constante, janela de timestamp e deduplicação por event ID.

## Limites atuais

- SQLite continua sendo banco local e não deve ser compartilhado entre máquinas;
- o arquivo SQLite não possui criptografia própria;
- a identificação de usuário ainda é simples;
- a integração real depende do OpenAPI da conta;
- cancelamento de NF-e não faz parte da V1;
- segurança do endpoint do Gerente também dependerá da infraestrutura escolhida para ele.

Consulte também `ARQUITETURA_SEGURANCA.md`.
