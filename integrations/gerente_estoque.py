"""Envio autenticado de eventos para o futuro Gerente de Estoque."""

import hashlib
import hmac
import json
import time
from urllib.parse import urlparse

import requests

from config.settings import (
    GERENTE_ESTOQUE_CONNECT_TIMEOUT,
    GERENTE_ESTOQUE_READ_TIMEOUT,
    GERENTE_ESTOQUE_WEBHOOK_SECRET,
    GERENTE_ESTOQUE_WEBHOOK_TOKEN,
    GERENTE_ESTOQUE_WEBHOOK_URL,
    INTEGRACAO_GERENTE_ATIVA
)


def _url_segura():
    if not GERENTE_ESTOQUE_WEBHOOK_URL:
        return False

    url = urlparse(
        GERENTE_ESTOQUE_WEBHOOK_URL
    )

    return (
        url.scheme == "https"
        and bool(url.hostname)
        and not url.username
        and not url.password
    )


def integracao_configurada():
    return (
        INTEGRACAO_GERENTE_ATIVA
        and _url_segura()
        and bool(GERENTE_ESTOQUE_WEBHOOK_SECRET)
    )


def _assinar(corpo, evento_id, timestamp):
    mensagem = (
        f"{timestamp}.{evento_id}.".encode("utf-8")
        + corpo
    )

    assinatura = hmac.new(
        GERENTE_ESTOQUE_WEBHOOK_SECRET.encode("utf-8"),
        mensagem,
        hashlib.sha256
    ).hexdigest()

    return f"sha256={assinatura}"


def enviar_evento(evento):
    if not integracao_configurada():
        return False

    payload = json.loads(
        evento["payload_json"]
    )

    envelope = {
        "evento_id": evento["evento_id"],
        "tipo": evento["tipo"],
        "versao": evento["versao"],
        "ocorrido_em": evento["criado_em"],
        "origem": "automacao_nfe",
        "dados": payload
    }

    corpo = json.dumps(
        envelope,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True
    ).encode("utf-8")

    timestamp = str(
        int(time.time())
    )

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "X-Webhook-Id": evento["evento_id"],
        "X-Webhook-Timestamp": timestamp,
        "X-Webhook-Signature": _assinar(
            corpo,
            evento["evento_id"],
            timestamp
        )
    }

    if GERENTE_ESTOQUE_WEBHOOK_TOKEN:
        headers["Authorization"] = (
            f"Bearer {GERENTE_ESTOQUE_WEBHOOK_TOKEN}"
        )

    resposta = requests.post(
        GERENTE_ESTOQUE_WEBHOOK_URL,
        data=corpo,
        headers=headers,
        timeout=(
            GERENTE_ESTOQUE_CONNECT_TIMEOUT,
            GERENTE_ESTOQUE_READ_TIMEOUT
        ),
        allow_redirects=False
    )

    if 300 <= resposta.status_code < 400:
        raise RuntimeError(
            "Redirecionamento inesperado no webhook."
        )

    resposta.raise_for_status()
    return True
