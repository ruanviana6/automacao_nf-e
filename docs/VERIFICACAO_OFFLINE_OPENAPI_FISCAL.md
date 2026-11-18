# Pré-verificação offline do contrato fiscal GestãoClick

Este verificador é **somente diagnóstico de documentação**, não um cliente da API. Não faz requisições, não cadastra notas, não lê credenciais e não habilita a automação real.

## Como obter o contrato

1. No ERP, abra **Meus aplicativos → API → Documentação → Referência** e use **Baixar em OpenAPI 3**. Verifique a documentação da conta e sua data/versão.
2. Confirme que o arquivo é **JSON** e não contém tokens, cabeçalhos preenchidos, URLs com segredos, dados de clientes ou outros dados privados. Se contiver, retire-os antes de compartilhar.
3. Sem cadastrar nada no ERP, inspecione localmente:

   ```bash
   python scripts/verificar_contrato_fiscal.py /caminho/seguro/openapi.json
   ```

4. O resultado identifica **apenas candidatos** para consultar lojas, pedidos/vendas, NF-e e cadastrar nota. Não prova que o recurso esteja habilitado na sua conta, que o cadastro não tenha efeitos colaterais ou que o payload esteja fiscalmente correto.

## Verificações pendentes após identificar as rotas

- Confirmar por GET autorizado os IDs distintos da origem **FLT Comércio** e do destino **Flagship - Flatter**; o ID 416023 do painel de estoque não identifica por si só qual das duas é a loja fiscal.
- Confirmar permissão e escopo da chave. O GestãoClick pode retornar HTTP 200 com um subconjunto de registros filtrados por usuário/loja.
- Mapear o pedido da origem, cliente, itens, unidades, identificação fiscal e nota anterior. Cadastro de NF-e no destino deve ser **direto, sem criar venda/pedido**.
- Separar **cadastrar** (cria nota em aberto) de **emitir** (envia à SEFAZ). Emissão permanece exclusivamente manual no ERP, conforme regra de 12/11/2026.
- Não definir campo de envio automático como verdadeiro e validar na conta se cadastro pode afetar estoque, venda, configuração ou agendamento.
- Antes de um POST homologado: exigir validação fiscal, confirmação Master, idempotência, consulta de duplicidade, gravação de diário, reconciliação de timeout e prova de não emitir.
- Nenhuma resposta deste script remove o bloqueio produtivo.

## Fontes oficiais

- https://gestaoclick.com.br/integracoes/api/
- https://central.gestaoclick.com.br/hc/pt-br/articles/4131-api-onde-esta-a-documentacao-como-pesquisar-nela-e-baixar-o-arquivo-openapi
- https://central.gestaoclick.com.br/hc/pt-br/articles/1874-emitir-e-cancelar-nota-fiscal-pela-api-linha-fis
- https://central.gestaoclick.com.br/hc/pt-br/articles/1867-api-quem-o-token-e-quando-entra-usuario-loja-e-permissoes

A publicação deste código não é homologação nem autorização de cadastro real. A aplicação web atual e sua Edge Function DEMO não mudam com este PR.
