"""Criação e entrega dos eventos usados para integrar outros módulos."""

from database.integracao_repository import (
    listar_eventos_pendentes,
    marcar_evento_enviado,
    marcar_evento_erro,
    registrar_evento
)
from integrations.gerente_estoque import (
    enviar_evento,
    integracao_configurada
)


def registrar_evento_nfe_processada(resultado, ambiente, origem):
    status = str(resultado.get("status", "")).lower()

    if status not in ("aprovada", "simulada"):
        return None

    nota_id = resultado["nota_id"]

    # O payload evita dados pessoais, XML/PDF e credenciais.
    payload = {
        "nota_id": nota_id,
        "numero_pedido": resultado["numero_pedido"],
        "numero_nfe": resultado.get("numero_nfe"),
        "status_nfe": resultado["status"],
        "ambiente": ambiente,
        "origem_nfe": origem
    }

    chave = (
        f"nfe.processada:{ambiente}:"
        f"{nota_id}:{status}"
    )

    return registrar_evento(
        tipo="nfe.processada",
        payload=payload,
        chave_idempotencia=chave,
        versao=1
    )


def enviar_eventos_pendentes(logger=None, limite=100):
    if not integracao_configurada():
        return {
            "status": "desativada",
            "enviados": 0,
            "erros": 0
        }

    enviados = 0
    erros = 0

    for evento in listar_eventos_pendentes(limite):
        try:
            enviar_evento(evento)
            marcar_evento_enviado(
                evento["evento_id"]
            )
            enviados += 1
        except Exception as erro:
            marcar_evento_erro(
                evento["evento_id"],
                erro
            )
            erros += 1

            if logger:
                logger.warning(
                    "Falha ao enviar evento %s para integração: %s",
                    evento["evento_id"],
                    erro
                )

    return {
        "status": "concluida",
        "enviados": enviados,
        "erros": erros
    }
