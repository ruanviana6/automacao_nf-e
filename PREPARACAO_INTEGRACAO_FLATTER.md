> REGRA VIGENTE de 12/11/2026: API única, origem FLT Comércio, cadastro da NF-e na loja Flagship - Flatter, emissão exclusivamente manual no ERP. Menções anteriores a duas contas/APIs ou emissão automatizada estão superadas. Consulte README.md e docs/CHECKLIST_ATIVACAO_API_GESTAOCLICK.md.

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


## Regras manuais já implementadas no domínio (sem emissão real)

O arquivo `services/regras_fiscais.py` valida duas escolhas obrigatórias e
imutáveis por tentativa de NF-e modelo 55. A montagem de dados em
`services/notas.py` aceita `opcoes_fiscais_manuais` e o provedor de duas
contas se recusa a criar a nota sem ambas. O fluxo simulado antigo continua
funcionando sem exigir entrada fiscal real.

- `modalidade_frete`: 0 CIF (remetente), **1 FOB (destinatário)**,
  2 terceiros, 3 transporte próprio remetente, 4 transporte próprio
  destinatário, 9 sem ocorrência de transporte.
- `tipo_contribuinte`: **9 Não contribuinte**, **2 Contribuinte isento
  de IE**, 1 Contribuinte ICMS. Não há valor padrão em nenhuma seleção.
- Os números são códigos fiscais do modelo NF-e (XML `modFrete` e
  `indIEDest`), **NÃO são ainda nomes de parâmetros confirmados para
  os endpoints da API GestãoClick**.
- Seleção humana tem de ocorrer **antes de criar/enviar** a nota.
  Após a criação, somente leitura do histórico; uma alteração exige novo
  procedimento de revisão do rascunho, nunca alterar nota autorizada.
- A tela no Gerente deverá usar dropdown/select com opção inicial vazia,
  prévia dos dados do cliente/pedido/frete, autorização e confirmação,
  guardar ambas as escolhas + usuário + data + número do pedido + estado
  fiscal/versão da prévia em trilha auditável privada.
- Conferir inscrição estadual e situação fiscal do cliente com o responsável
  antes de emitir; **isento** e **não contribuinte** não são equivalentes.
  Contribuinte ICMS normalmente exige IE válida; isento não deve ter IE no
  XML correspondente, sujeito às regras vigentes. Não alterar cadastro ERP.
- Outros campos fiscais (CFOP, NCM, CST/CSOSN, consumidor final, frete total,
  transportadora, pagamento, certificação/loja etc.) dependem do contrato
  oficial e validação fiscal; não inventar nem inferir.

### Alerta especial de integração GestãoClick
A documentação oficial GestãoClick linha FIS informa que a chamada de emissão
por API pode remover o agendamento de envio automático da loja, inclusive
quando a emissão não acontece. **Antes de habilitar POST real, verificar se
a conta Varejo utiliza essa rotina automática**. Se utilizar, bloquear
ativação até avaliar o impacto e a alternativa com o responsável. Isso é um
efeito colateral operacional incompatível com a regra de não alterar rotinas
do ERP, salvo autorização específica.

### Pendências de segurança e conciliação
- O armazenamento atual `notas_fiscais` no SQLite verifica só status
  `criada/processando/aprovada/simulada`, enquanto o ERP distingue
  `Em aberto, Aprovada, Reprovada, Denegada, Cancelada, Enviando, Corrigida`.
  Reprovação não deve gerar uma segunda nota automaticamente: consultar
  ID e reutilizar a mesma nota após correção e revisão no ERP, sem usar DELETE.
- A emissão no GestãoClick é síncrona; timeout/criação/emissão incerta precisa
  reconciliar por chave externa e estado consultado antes de qualquer POST.
- O backend de automação ainda roda em SQLite local; a tela Streamlit precisa
  de fila/serviço protegido, RLS e trilha de auditoria separada; não ligar
  webhook de saída a URL inventada e não tratar Streamlit como trabalhador
  permanente.
- Nenhuma nota, credencial ou cadastro real foi acessado nesta etapa.

Referência fiscal de campo: MOC NF-e, `modFrete` e `indIEDest`.
Referência do ERP (validar novamente com o OpenAPI da conta):
https://central.gestaoclick.com.br/hc/pt-br/articles/1874-emitir-e-cancelar-nota-fiscal-pela-api-linha-fis
