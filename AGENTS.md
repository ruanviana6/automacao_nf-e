# Diretrizes atuais da automação fiscal Flatter

Toda comunicação, documentação, comentários e docstrings são em pt-BR.
O pedido de 11/11/2026 autoriza consolidar o PR #1, testar, integrar e publicar
DEMO no Gerente. Supabase existente é a única base operacional. Nunca criar
outro motor ou banco fiscal de produção.

- O executor operacional DEMO fica em Supabase Edge Functions, versionado no
  Gerente. Este repositório fornece regras, contratos compartilhados, adaptadores
  bloqueados e uma referência Python para testes descartáveis.
- Atacado é estritamente leitura. Criação/emissão real de NF-e poderá existir
  somente no executor isolado Varejo após OpenAPI, homologação e nova autorização.
- Nenhuma chamada real ao ERP está autorizada nesta entrega. Não inventar rotas,
  campos, CFOP, impostos ou códigos API. Não criar pedidos no Varejo, editar
  cadastros/saldos, cancelar, corrigir, inutilizar ou excluir notas.
- Os dois campos fiscais exigem seleção manual, sem defaults. Em andamento exige
  aprovação Auth identificada; nomes digitados não concedem autorização produtiva.
- Não baixar nem salvar XML/PDF automaticamente. Não executar limpeza histórica.
- Journal precede criação. Identidade inclui organização, conta, pedido, destino
  e ambiente; timeout exige reconciliação, nunca retry automático de POST.
- Não versionar dados pessoais, credenciais, SQLite, backups ou documentos.
- Preservar componentes históricos necessários aos testes; documentar seu caráter
  não operacional. `main.py` não é outro serviço fiscal.
- Executar os testes e auditoria de dependências. Não declarar API real homologada
  com base em testes DEMO.

Consulte README.md, INTEGRACAO_GERENTE_ESTOQUE.md e
docs/CHECKLIST_ATIVACAO_API_GESTAOCLICK.md antes de implementar uma integração.
