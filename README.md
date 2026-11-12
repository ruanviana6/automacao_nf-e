# Automação NF-e Flatter

Criei este projeto para reduzir etapas repetitivas na conferência de pedidos e
notas. Ele agora participa da aplicação única
[Gerente Flatter](https://estoqueinteligente-flatter.streamlit.app/), sem manter
outro banco operacional ou outro serviço fiscal em Python.

O desenvolvimento usa IA e Vibe Coding. As regras vêm da rotina do proprietário;
a IA auxilia no código, na revisão e nos testes. Nenhuma simulação comprova
homologação tributária ou funcionamento da API real.

## Responsabilidade atual

O Gerente fornece interface, Supabase Auth e permissões. O Supabase existente
guarda solicitações, prévias, aprovações, identidade, resultados e auditoria.
Uma Edge Function Deno sob demanda é o único executor operacional **DEMO**.
Seu código fica em `supabase/functions/fiscal-demo` no repositório do Gerente,
junto às migrações e aos testes de autorização.

Este repositório fornece regras, adaptadores futuros bloqueados, o contrato
compartilhado `contratos/fiscal_demo_v1.json` e uma referência Python testável.
`database/referencia_repository.py` usa SQLite apenas em testes descartáveis;
nunca deve ser ligado como uma segunda persistência fiscal de produção.

O PR #1 original foi aproveitado: contas separadas em `api/duas_contas.py`,
regras fiscais e bloqueios da integração real foram preservados e reforçados.
O cliente genérico legado `api/gestaoclick.py` está desativado.

## Fluxo disponível na aplicação

1. Usuário autenticado consulta um número de pedido DEMO.
2. Confere destinatário, UF, situação, produtos, quantidades e valores fictícios.
3. Seleciona manualmente frete e tipo de contribuinte, sem valores padrão.
4. Confere a prévia imutável e confirma explicitamente a simulação.
5. Supabase registra uma solicitação única; Em andamento aguarda aprovação.
6. Executor simula autorização, rejeição ou timeout e preserva o histórico.

Somente CE/Ceará/Ceara são elegíveis. Em separação e Concretizada podem seguir;
Em andamento exige `fiscal.approve_pending`, identidade Auth e horário.
Outras situações e qualquer nota existente impedem uma nova criação automática.

Fretes disponíveis: 0, 1, 2, 3, 4 e 9. Contribuintes: 1, 2 e 9.
Isento (2) e não contribuinte (9) são distintos. A falta de inscrição estadual
não escolhe o código. Nenhum imposto, CFOP, CST/CSOSN ou NCM é inferido.

A identidade combina organização, conta de origem, ID do pedido, destino e
ambiente. O diário é gravado antes da criação. Timeout mantém bloqueio para
conferência; POST nunca é repetido automaticamente. Nenhum XML/PDF é baixado,
gerado ou salvo pelo fluxo operacional. Arquivos antigos são preservados.

## Limites da integração real

**Nenhuma consulta ou emissão real está habilitada.**
Atacado será sempre somente leitura. Somente o executor isolado poderá,
futuramente e com nova autorização, criar e emitir NF-e diretamente no Varejo.
Não poderá criar pedido, modificar cliente/produto/estoque, cancelar, corrigir,
inutilizar ou excluir notas. Se a API exigir pedido no Varejo, a ativação ficará
bloqueada. Não se inventam rotas, parâmetros ou códigos de status da API.

Consulte [o checklist de ativação](docs/CHECKLIST_ATIVACAO_API_GESTAOCLICK.md)
e [a comunicação com o Gerente](INTEGRACAO_GERENTE_ESTOQUE.md).

## Desenvolvimento e testes

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
pip-audit -r requirements.txt
```

Os testes usam pedidos fictícios, bloqueiam rede e isolam SQLite temporário.
Cobrem concorrência, todos os estados existentes, timeout antes/depois da criação,
escolhas manuais, ausência de downloads e bloqueio do cliente legado.
Os testes de Auth/PostgREST, RLS e Edge Functions ficam no Gerente, pois são
parte da mesma implantação. Consulte os respectivos GitHub Actions para as
versões efetivamente executadas e os resultados.

`python main.py` informa o endereço da aplicação única e encerra. Não inicia
um segundo motor, downloads, limpeza, webhook ou rotina de e-mail.
Módulos antigos continuam disponíveis para regressão e inspeção histórica;
as instruções anteriores estão marcadas em `docs/historico/` e não são um
procedimento de operação. Não execute limpeza de documentos antigos.

Segredos ficam fora do Git e do navegador. Não configure credenciais reais
antes de concluir o checklist e receber autorização explícita.
