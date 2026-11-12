> REGRA VIGENTE de 12/11/2026: API única, origem FLT Comércio, cadastro da NF-e na loja Flagship - Flatter, emissão exclusivamente manual no ERP. Menções anteriores a duas contas/APIs ou emissão automatizada estão superadas. Consulte README.md e docs/CHECKLIST_ATIVACAO_API_GESTAOCLICK.md.

# Integração atual com o Gerente Flatter

A comunicação operacional usa exclusivamente o Supabase existente. O Streamlit
não recebe webhooks nem compartilha SQLite. A fila HTTP/HMAC da V1 permanece
histórica, desativada e fora do caminho operacional.

O funcionário entra no Gerente, seleciona o pedido DEMO e ambos os códigos
manuais, confere a prévia e confirma a solicitação. RPCs usam seu JWT e verificam
sessão, conta ativa, organização e permissões no banco. Em andamento exige
aprovação identificada, também revalidada antes da execução.

O Gerente chama a função `fiscal-demo` enviando somente UUID da solicitação e
ação `execute_demo` ou `reconcile_demo`. A Edge Function verifica Auth, solicita
uma concessão no banco com o JWT individual e conclui somente essa concessão
pela RPC restrita do executor. A chave administrativa nativa da plataforma
nunca chega ao Streamlit ou navegador e não é usada para consultas comuns.

Solicitações, resultados e eventos ficam no PostgreSQL. Uma restrição única
inclui organização, origem, ID estável do pedido, destino e ambiente. Somente
uma concessão pode processar a solicitação. Concessão vencida ou resultado
incerto exigem conferência; atualização de página não repete criação.

O contrato compartilhado tem SHA256
`400ab19bf26309a7f24798da21dc09e4170acab57af8460a508247625e72f5b9`.
O catálogo SQL no Gerente e os testes Python usam os mesmos cenários fictícios.
Nenhum código XML é tratado como nome de parâmetro da API.

A referência `services/notas.py` aceita somente provedor de simulação e serve
aos testes. Não fornece autorização de funcionário em produção. Não há segundo
motor produtivo. A implementação real dependerá do checklist OpenAPI, inclusive
journal durável separado para criar/emitir e reconciliação por ID externo.

Migrações, implantação Edge, limites gratuitos, segurança e evidências ficam
em `docs/FISCAL_DEMO.md` no Gerente. A ativação real deve ocorrer em alteração
própria, revisada nos dois projetos.
