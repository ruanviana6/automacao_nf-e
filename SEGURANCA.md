# Segurança da Automação NF-e

Esta revisão registra as proteções já adotadas e os pontos que precisam ser conferidos antes de ativar a API real.

## Proteções já aplicadas

- credenciais ficam no arquivo `.env`, que não é enviado ao GitHub;
- tokens não são escritos nos logs;
- consultas SQL usam parâmetros em vez de montar SQL com dados externos;
- arquivos fiscais locais ficam fora do Git;
- exclusão manual é limitada às pastas de XML e PDF;
- emissão duplicada é bloqueada quando já existe nota concluída para o pedido no mesmo ambiente;
- uma nota criada fica registrada antes da etapa de emissão, evitando nova criação automática após timeout;
- o modo de simulação é separado do ambiente de produção;
- erros ficam registrados em log;
- não existe repetição automática de chamadas POST de emissão;
- XML/PDF e logs possuem retenção local de 45 dias;
- a integração com outros módulos usa eventos e não expõe diretamente o SQLite;
- eventos enviados ao Gerente de Estoque não incluem CPF/CNPJ, XML, PDF, tokens ou senhas;
- falhas na integração externa não bloqueiam o processamento da NF-e;
- eventos não entregues ficam persistidos para reenvio posterior.

## Antes de produção

1. Confirmar no OpenAPI os endpoints, campos e status oficiais do GestãoClick.
2. Usar credenciais específicas para a integração e aplicar o menor nível de acesso possível.
3. Definir `MODO_SIMULACAO=false` somente depois dos testes da API.
4. Configurar `USUARIO_EXECUCAO` para identificar quem ou qual conta executa a automação.
5. Validar se CPF/CNPJ, XML e PDF podem permanecer no computador utilizado e quais permissões de pasta serão aplicadas.
6. Criar rotina de backup do histórico SQLite ou migrar para banco central quando o uso deixar de ser individual/local.
7. Confirmar política interna para envio de relatório por e-mail e seus destinatários.
8. Fazer primeiro teste real com poucos pedidos e conferir manualmente o resultado no GestãoClick.
9. Nunca registrar tokens, senhas, conteúdo completo de documentos fiscais ou outros segredos em logs.
10. Revisar o comportamento de cancelamento, rejeição e reemissão antes de automatizar esses cenários.
11. Ao integrar o Gerente de Estoque, usar HTTPS no webhook e um token compartilhado forte.
12. Manter `INTEGRACAO_GERENTE_ATIVA=false` enquanto o endpoint do gerente ainda não estiver pronto.

## Limites atuais

- o banco SQLite local não possui criptografia própria;
- a identificação de usuário é simples e ainda não é um sistema completo de autenticação;
- a integração real com o GestãoClick ainda depende do OpenAPI da conta;
- cancelamento de NF-e não faz parte da V1;
- o webhook futuro do Gerente de Estoque ainda dependerá da autenticação e hospedagem escolhidas para esse projeto.
