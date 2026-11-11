# Preparação da integração NF-e: Atacado → Varejo → Gerente Flatter

## Estado atual (sem conexão real)
Esta branch prepara a separação operacional das contas. **Não cria nem emite
NF-e no GestãoClick**; todas as rotas de negócio continuam bloqueadas até
validação da documentação OpenAPI e das regras fiscais finais.

- **GestãoClick Atacado:** origem dos pedidos (consulta somente GET).
- **GestãoClick Varejo:** destino exclusivo de criar e emitir NF-e de pedidos
  elegíveis do Ceará, depois de autorização e conferências fiscais.
- **Gerente Flatter:** estoque, vendas e ML usando apenas a leitura do Atacado;
  não recebe credenciais do Varejo nem pode emitir notas por conta própria.

O próprio ERP Atacado emite as notas de outros estados. A automação **não**
emite no Atacado e jamais cria pedidos duplicados no Varejo.

## Fluxo a implementar após a validação da API

1. O funcionário autenticado solicita a geração de NF-e pelo painel fiscal.
2. O backend consulta o pedido no Atacado usando a credencial de leitura.
3. Aplica os critérios: destino CE (aceitando CE/Ceará/Ceara), status Em
   separação ou Concretizada; Em andamento somente com autorização
   identificada de usuário habilitado.
4. Valida autorização, campos obrigatórios, cadastro do cliente, tributação e
   correspondência de produtos entre contas. **Não inferir CFOP, CST/CSOSN,
   NCM, origem, alíquotas, natureza da operação nem outras regras fiscais.**
   Informações fiscais precisam ser fornecidas e conferidas por responsável.
5. Consulta o Atacado/Varejo para verificar NF-e já emitida e estados
   pendentes, além da trava local/Supabase por origem+pedido+destino+ambiente.
6. Prévia fiscal com os campos mapeados: o usuário confirma antes de enviar
   qualquer criação/emissão.
7. Cria NF-e diretamente no Varejo SOMENTE se o OpenAPI documentar que
   isso é possível sem pedido anterior. Se não suportar, **bloquear e
   apresentar incompatibilidade**, sem criar pedido como contorno.
8. Registra ID externo assim que recebido, consulta resultado após timeout
   ou erro ambíguo e **nunca repete automaticamente um POST fiscal**.
9. Mantém no Gerente apenas estado técnico mínimo de acompanhamento
   (pedido, referência de NF-e, status, timestamps, autor), sem XML/PDF,
   dados fiscais pessoais ou cópia da nota; o ERP é a fonte oficial.
10. Publica evento de conclusão/falha por mecanismo autenticado e idempotente
    depois de implementado o receptor seguro; falhas desse mecanismo não
    autorizam nova emissão.

## Integração na aplicação Streamlit
Hoje o projeto NF-e é uma aplicação local Python/SQLite, e o Gerente é uma
aplicação Streamlit com Supabase. Não compartilhar o arquivo SQLite entre
máquinas. Streamlit **não é um servidor HTTP de webhooks arbitrários**.
O webhook existente é apenas o **emissor**, e ainda não há receptor validado no
Gerente. Não apontar URL fictícia ou ativar INTEGRACAO_GERENTE_ATIVA.

A implementação final deve oferecer uma tela fiscal sob permissão explícita
no Gerente e transportar comandos de forma segura ao processo emissor, usando
um mecanismo de fila/execução controlado e auditado com o Supabase ou um
serviço existente compatível com custo zero. Nunca habilitar emissão
por operações de GET, parâmetros de URL ou rotina de navegação.

## Segurança
- MODO_SIMULACAO=true, NFE_EMISSAO_REAL_HABILITADA=false e
  INTEGRACAO_GERENTE_ATIVA=false até a liberação formal.
- Não armazenar credenciais em repositório, .env versionado, prints, logs,
  browser, frontend ou payload de eventos.
- Duas credenciais separadas: ATACADO leitura, VAREJO emissão; nunca usar
  credenciais de emissão do Varejo no Gerente analítico.
- O Gerente e sua integração GestãoClick continuam permanentemente GET-only.
- Nenhum módulo apaga, cancela ou modifica notas/pedidos/estoque no ERP,
  além da eventual criação e emissão de NF-e autorizada no Varejo.
- Chave de idempotência: organização + fonte Atacado + numero_pedido +
  destino Varejo + ambiente. Em caso de dúvida, consultar no ERP antes.
- Autorização por usuário, trilha de auditoria e confirmação para cada nota;
  sem promoção de acesso público, sem chave de serviço exposta.
- Testar multiusuário, concorrência, queda de rede, timeout após POST,
  autorização revogada e nota preexistente.

## Dependências antes de ativar
1. Contratos OpenAPI reais dos dois GestãoClick e permissões por usuário/loja;
   não compartilhar os tokens no chat ou GitHub.
2. Regras finais de preenchimento fiscal validadas pelo responsável.
3. Validação documentada de criação sem pedido no Varejo.
4. Contrato de botão/serviço fiscal e receptor de eventos seguros no Supabase,
   com RLS e auditoria.
5. Testes em homologação com dados fictícios e autorização específica
   antes de qualquer emissão fiscal real.

Este PR prepara os pontos de integração; **não habilita produção nem altera
o aplicativo Flatter publicado**.
