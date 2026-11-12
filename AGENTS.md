## Regra vigente de 12/11/2026: cadastro por loja, sem emissão

O usuário substituiu o modelo de duas APIs por UMA API GestãoClick com lojas.
Origem: FLT Comércio (atacado). Destino: Flagship - Flatter (varejo).
A única escrita fiscal futura permitida é CADASTRAR a NF-e diretamente na loja
de destino, sem criar venda/pedido. A emissão é SEMPRE MANUAL no ERP. Nenhuma
flag pode habilitar emissão automática. O cliente analítico continua GET-only.
Manter a aba Automação / Notas Fiscais com frete e contribuinte manuais, prévia,
confirmação de cadastro e histórico. Preservar login após F5/reabertura.
IDs reais de lojas dependem do OpenAPI; não inferir por nome, posição ou CNPJ.
Não versionar dados empresariais da imagem fornecida. Credencial única protegida.
Continuam bloqueados integração real, pedidos/vendas no varejo, alteração de
cadastros/saldos, cancelamento, exclusão, inutilização e qualquer emissão.
Esta regra substitui menções anteriores a duas APIs ou a criar E emitir notas.
Não editar migrações já aplicadas; preservar registros legados e identificá-los.
Consultar docs/CHECKLIST_ATIVACAO_API_GESTAOCLICK.md antes da integração real.

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
