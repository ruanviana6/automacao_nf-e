"""Envio opcional de eventos para o futuro Gerente de Estoque."""

import json

import requests

from config.settings import (
    GERENTE_ESTOQUE_TIMEOUT,
    GERENTE_ESTOQUE_WEBHOOK_TOKEN,
    GERENTE_ESTOQUE_WEBHOOK_URL,
    INTEGRACAO_GERENTE_ATIVA
)


def integracao_configurada():
    return (
        INTEGRACAO_GERENTE_ATIVA
        and bool(GERENTE_ESTOQUE_WEBHOOK_URL)
    )


def enviar_evento(evento):
    if not integracao_configurada():
        return False

    payload = json.loads(evento["payload_json"])

    envelope = {
        "evento_id": evento["evento_id"],
        "tipo": evento["tipo"],
        "versao": evento["versao"],
        "ocorrido_em": evento["criado_em"],
        "origem": "automacao_nfe",
        "dados": payload
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    if GERENTE_ESTOQUE_WEBHOOK_TOKEN:
        headers["Authorization"] = (
            f"Bearer {GERENTE_ESTOQUE_WEBHOOK_TOKEN}"
        )

    resposta = requests.post(
        GERENTE_ESTOQUE_WEBHOOK_URL,
        json=envelope,
        headers=headers,
        timeout=GERENTE_ESTOQUE_TIMEOUT
    )

    resposta.raise_for_status()
    return True
