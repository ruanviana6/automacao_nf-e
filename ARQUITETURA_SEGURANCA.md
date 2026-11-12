> REGRA VIGENTE de 12/11/2026: API única, origem FLT Comércio, cadastro da NF-e na loja Flagship - Flatter, emissão exclusivamente manual no ERP. Menções anteriores a duas contas/APIs ou emissão automatizada estão superadas. Consulte README.md e docs/CHECKLIST_ATIVACAO_API_GESTAOCLICK.md.

# Arquitetura atual

Streamlit autenticado → RPCs Supabase → solicitações e auditoria PostgreSQL.
Uma Edge Function DEMO sob demanda processa exclusivamente concessões válidas.
Não existe worker permanente, Redis, banco fiscal local ou webhook no Streamlit.
Python fornece regras, contratos e referência de teste.

Há três limites de confiança: navegador, backend autenticado e executor isolado.
Organização, solicitante e aprovador vêm do Auth/banco, nunca do corpo HTTP.
Permissões fiscais começam negadas para nãoMaster. `fiscal.manage` é exclusivo
do Master. RLS e grants impedem ler ou alterar tabelas fiscais diretamente.

O executor revalida solicitante e aprovador, sessão, revogações e modo DEMO.
O cliente não escolhe resultados. A chave de plataforma só conclui a RPC do
executor, após uma concessão com nonce, prazo e identidade validados.

O cliente analítico do Gerente continua GET-only. O adaptador fiscal real
permanece bloqueado, com credenciais futuras distintas Atacado/Varejo. Não
há rotas fiscais presumidas. SQLite e utilitários antigos são somente referência
ou testes; não fazem parte da implantação web.

Veja [o checklist](docs/CHECKLIST_ATIVACAO_API_GESTAOCLICK.md) para riscos fiscais,
limites, validação do OpenAPI e homologação. A arquitetura anterior foi preservada
com marcação histórica em `docs/historico/`.
