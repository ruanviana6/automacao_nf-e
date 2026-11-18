# Integração fiscal sem arquivo OpenAPI — referência pública e validação segura

**Não é necessário fornecer OpenAPI.** O usuário já entregou o material disponível e a aplicação já fez GET autenticado de vendas e catálogo.

## Referência oficial pública (não é validação da conta)

A documentação oficial do GestãoClick atualizada em novembro de 2026 confirma:
- Para NF-e de produto modelo 55, o recurso é `notas_fiscais_produtos` (e não `notas_fiscais`).
- Cadastro e emissão são ações separadas: o cadastro cria nota **Em aberto** e a emissão é outra operação. A automação Flatter **nunca executa a emissão**.
- `envio_automatico` pode encaminhar uma nota para uma fila de emissão após a criação: **não presumir padrão nem habilitar**.
- Usuário e loja vêm da credencial ou do escopo oficial da requisição; token limitado por loja pode ignorar `loja_id`.
- Consultas publicamente descritas incluem `/lojas`, `/vendas` e `/notas_fiscais_produtos`; a existência do recurso **na conta** ainda precisa ser comprovada em leitura autenticada, sem exibir dados pessoais.

Para ver apenas esta referência offline, sem nenhum segredo e sem chamadas:

```bash
python scripts/verificar_contrato_fiscal.py
```

Se, futuramente, existir um arquivo OpenAPI 3 JSON, o mesmo script pode analisá-lo opcionalmente com um argumento, mas **isso não é condição para avançar**:

```bash
python scripts/verificar_contrato_fiscal.py contrato-opcional.json
```

## Procedimento real sem OpenAPI

1. **Já demonstrado:** auditoria `GET /vendas` na loja 416023, período 12–18/11/2026, 169 documentos em duas páginas, 155 pedidos fechados, 123/123 IDs de produtos conciliados e 3.740 UN observadas. Isso não comprova o fluxo fiscal nem qual loja é a Flagship.
2. **Próxima leitura, com confirmação Master:** conferir em `GET /lojas` os IDs exatos de **FLT Comércio** e **Flagship - Flatter**, usando a conexão já protegida no Gerente, sem publicar nomes de clientes ou tokens. Rejeitar identidade ambígua e credencial restrita à loja errada.
3. **Consultar apenas GET (sem salvar payload):** checar se `GET /notas_fiscais_produtos` está disponível **na loja de destino** e se consegue localizar nota já cadastrada para um pedido, inclusive em aberto. Se a conta negar 403 ou não permitir escopo da Flagship, **parar** e registrar apenas motivo técnico sanitizado.
4. **Conferir fiscalmente:** correspondência do cliente, dos produtos e dos impostos; fonte de quantidade/preço, CFOP, NCM, CST/CSOSN, natureza, frete, contribuinte, transporte e pagamento. Nenhum desses valores deve ser inferido do quantitativo de estoque/vendas.
5. **Antes de qualquer cadastro:** confirmar que o POST de cadastro de NF-e direta no Varejo não cria pedido/venda, não baixa estoque, não agenda envio automático e não aciona emissão; validar corpo e formato oficial na conta, inclusive efeito de `envio_automatico`. O fato de o endpoint público existir **não prova** esses detalhes.
6. **Somente após aprovação fiscal e homologação explícita:** usar o executor isolado com diário antes do POST, chave de unicidade por origem/pedido/destino/ambiente, proteção contra duplicidade e reconciliação obrigatória de timeout. Nenhum retry automático de POST.
7. **Emissão permanece manual** no GestãoClick. Proibido `emitir`, `cancelar`, criar vendas/pedidos, alterar cadastros e editar saldos.

## Estado

- Integração analítica GestãoClick: **somente GET e conferência**.
- Automação fiscal: **DEMO**. Cadastro real **BLOQUEADO**.
- Não recriar Supabase, não alterar segredos, não fazer chamada real de POST nem ativar por merge.
- Este PR é de suporte à integração e não publica alterações no ERP.

## Fontes

- https://central.gestaoclick.com.br/hc/pt-br/articles/1871-api-o-que-da-e-o-que-nao-da-para-fazer-e-os-enderecos-que-confundem
- https://central.gestaoclick.com.br/hc/pt-br/articles/1874-emitir-e-cancelar-nota-fiscal-pela-api-linha-fis
- https://central.gestaoclick.com.br/hc/pt-br/articles/1867-api-quem-o-token-e-quando-entra-usuario-loja-e-permissoes
