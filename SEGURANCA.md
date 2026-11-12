> REGRA VIGENTE de 12/11/2026: API única, origem FLT Comércio, cadastro da NF-e na loja Flagship - Flatter, emissão exclusivamente manual no ERP. Menções anteriores a duas contas/APIs ou emissão automatizada estão superadas. Consulte README.md e docs/CHECKLIST_ATIVACAO_API_GESTAOCLICK.md.

# Segurança fiscal Flatter

- Somente DEMO, sem comunicação com GestãoClick e sem credenciais reais.
- Frete e contribuinte manuais, confirmação consciente e aprovação Auth.
- Permissões no backend e banco; nenhuma autorização por nome digitado.
- RLS, isolamento por organização, unicidade e locks no PostgreSQL operacional.
- Sessões e permissões revalidadas antes da concessão e do resultado.
- Journal antes da operação; timeout não libera criação e não recebe retry.
- Resultado e identidade vêm do servidor, sem aprovação forjada pelo navegador.
- Ausência de download/salvamento automático de XML/PDF e limpeza histórica.
- Cliente genérico legado desativado; referência Python recusa provedor real.
- CI com dados fictícios, bloqueio de rede e auditoria de dependências.
- Nenhum token ou documento em Git, logs, URLs ou mensagens de erro.

A futura ativação exige OpenAPI das duas contas, mapeamento fiscal e avaliação
do efeito sobre a emissão automática da loja. Não configure APIs em produção
sem concluir [o checklist](docs/CHECKLIST_ATIVACAO_API_GESTAOCLICK.md).
Os registros de segurança da V1 em `docs/historico/` não são instruções vigentes.
