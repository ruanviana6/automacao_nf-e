> DOCUMENTO HISTÓRICO DA V1. Não executar estas instruções. Substituído pela arquitetura DEMO de 11/11/2026 descrita no README atual.

# Integração com o Gerente de Estoque

A automação de NF-e foi preparada para funcionar de forma independente e, no futuro, enviar eventos para o Gerente de Estoque sem compartilhar diretamente o SQLite.

## Como funciona

Quando uma NF-e é concluída, a automação registra um evento local:

```text
NF-e concluída
      ↓
eventos_integracao (SQLite)
      ↓
evento pendente
      ↓
webhook do Gerente de Estoque
```

Se o Gerente de Estoque estiver fora do ar, a NF-e não é bloqueada. O evento permanece salvo e pode ser reenviado depois.

## Evento inicial

Tipo:

```text
nfe.processada
```

Exemplo:

```json
{
  "evento_id": "uuid",
  "tipo": "nfe.processada",
  "versao": 1,
  "ocorrido_em": "data/hora UTC",
  "origem": "automacao_nfe",
  "dados": {
    "nota_id": 12,
    "numero_pedido": 4589,
    "numero_nfe": "12345",
    "status_nfe": "aprovada",
    "ambiente": "producao",
    "origem_nfe": "gestaoclick"
  }
}
```

O evento não envia CPF/CNPJ, XML, PDF, tokens ou senhas.

## Ativação futura

No `.env`:

```env
INTEGRACAO_GERENTE_ATIVA=true
GERENTE_ESTOQUE_WEBHOOK_URL=https://endereco-do-gerente/eventos
GERENTE_ESTOQUE_WEBHOOK_TOKEN=segredo-compartilhado
```

Enquanto o gerente estiver sendo desenvolvido separadamente, mantenha:

```env
INTEGRACAO_GERENTE_ATIVA=false
```

## Reenvio

Eventos que falharam permanecem no banco.

Para tentar novamente:

```bash
python main.py --reenviar-eventos
```

## Por que não compartilhar o SQLite

A automação pode continuar em uma máquina local enquanto o Gerente de Estoque pode estar hospedado em outro ambiente.

Compartilhar o arquivo SQLite entre aplicações ou computadores aumentaria risco de concorrência e corrupção. A integração por eventos mantém os projetos independentes.

## Evolução

O mesmo padrão permite acrescentar novos eventos futuramente, por exemplo:

- `pedido.processado`;
- `nfe.rejeitada`;
- `estoque.baixo`;
- `estoque.reposicao_sugerida`;
- `expedicao.iniciada`.

O Gerente de Estoque continuará responsável pelas próprias regras de estoque e previsão. A automação de NF-e apenas publica fatos relevantes.
