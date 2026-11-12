# Cadastro de NF-e Flatter

Criei este projeto para reduzir etapas repetitivas na conferência de pedidos e
notas. Ele participa da aplicação única
[Gerente Flatter](https://estoqueinteligente-flatter.streamlit.app/), sem outro
banco operacional ou serviço fiscal Python independente.

Uso IA e Vibe Coding no desenvolvimento. Eu defino as necessidades da rotina;
a IA auxilia no código, na revisão e nos testes. Simulação não é homologação
fiscal nem comprovação de funcionamento da API real.

## Regra atual

Uma API GestãoClick, com lojas distintas. A origem é FLT Comércio, nosso atacado;
a Flagship - Flatter, varejo, recebe somente o cadastro da NF-e. A emissão é
manual no GestãoClick. A automação nunca emite e nunca cria venda/pedido no
varejo, edita cadastros/saldos, cancela, corrige, inutiliza ou exclui notas.

A regra informada em 12/11/2026 substitui o modelo anterior de duas APIs e a
ideia de emissão automática. api/duas_contas.py permanece apenas para rejeitar
uso legado. api/provider.py utiliza api/lojas.py, com uma credencial e dois IDs
de lojas explícitos. Nome, posição na tela e CNPJ não são usados como IDs da API.

## Aplicação e responsabilidades

O Gerente oferece a aba Automação / Notas Fiscais, autenticação e permissões.
Supabase centraliza prévias, escolhas, solicitante/aprovador, unicidade, estados
e auditoria. A única Edge Function operacional é DEMO e fica no repositório do
Gerente. Este projeto fornece regras, adaptadores bloqueados e contratos de
referência. SQLite existe somente em testes descartáveis, sem segunda produção.

O funcionário confere o pedido, escolhe frete e contribuinte manualmente e
confirma o cadastro. CE/Ceará/Ceara são aceitos. Em separação/Concretizada são
elegíveis; Em andamento exige aprovação Auth identificada. Nota existente e
resultado incerto bloqueiam novo cadastro até conferência/reconciliação.

Frete: 0, 1, 2, 3, 4 e 9, sem padrão. Contribuinte: 1, 2 e 9, sem inferir pela
falta de IE. Isento (2) e não contribuinte (9) são diferentes. CFOP, NCM,
CST/CSOSN, impostos, natureza e demais campos reais dependem de validação.

O diário precede cadastro. A identidade inclui organização, conexão, loja de
origem, ID estável do pedido, loja de destino e ambiente. Nenhum POST recebe
retry automático. O resultado DEMO é cadastrada_demo, sem chave, número de
nota autorizada ou data de emissão. Não há download/salvamento automático de
XML/PDF nem limpeza histórica. Arquivos antigos são preservados.

O contrato atual é contratos/fiscal_demo_v2.json, idêntico ao contrato v2 do
Gerente. A versão anterior é histórica. services/notas.py é uma referência
simulada e não chama emitir_nota, nem em testes. Não é um segundo executor.

## Desenvolvimento

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
pip-audit -r requirements.txt
```

Os testes usam dados fictícios, bloqueiam rede e isolam SQLite temporário.
Cobrem unicidade, concorrência, escolhas, timeout, preservação de IDs, ausência
de documentos e proibição de emissão, inclusive por flags/métodos antigos.
Auth/PostgREST/RLS e o executor Edge são testados no repositório do Gerente.

python main.py apenas informa o endereço da aplicação única e encerra.
Componentes antigos de arquivos, limpeza e webhook ficam fora da operação.
Documentos históricos estão marcados em docs/historico e não são instruções
vigentes. Nenhum arquivo antigo é apagado pelo fluxo.

## API real

Ainda está bloqueada por construção. Precisamos do OpenAPI único, IDs de lojas,
credencial protegida e mapeamento fiscal, seguidos de autorização de homologação.
O cadastro direto precisa ocorrer sem venda/pedido e sem envio/emissão automática.
Se o contrato não oferecer isso, a integração não será ativada.

Consulte [o checklist](docs/CHECKLIST_ATIVACAO_API_GESTAOCLICK.md).
Não envie credenciais no chat, no navegador ou no Git. Não há opção para habilitar
emissão automática. Ela permanece manual no ERP.
