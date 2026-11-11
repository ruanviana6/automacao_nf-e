import hashlib
import hmac
import json

import database.conexao as conexao
import integrations.gerente_estoque as gerente
from database.integracao_repository import (
    inicializar_integracao,
    listar_eventos_pendentes,
    registrar_evento
)
from services.eventos_integracao import (
    enviar_eventos_pendentes
)


def preparar_banco(tmp_path, monkeypatch):
    monkeypatch.setattr(
        conexao,
        "CAMINHO_BANCO",
        tmp_path / "integracao.db"
    )
    inicializar_integracao()


def test_evento_e_idempotente(tmp_path, monkeypatch):
    preparar_banco(
        tmp_path,
        monkeypatch
    )

    primeiro = registrar_evento(
        "nfe.processada",
        {"numero_pedido": 1001},
        "nfe.processada:simulacao:1:simulada"
    )

    segundo = registrar_evento(
        "nfe.processada",
        {"numero_pedido": 1001},
        "nfe.processada:simulacao:1:simulada"
    )

    assert primeiro["evento_id"] == segundo["evento_id"]
    assert len(listar_eventos_pendentes()) == 1


def test_integracao_desativada_mantem_evento_pendente(
    tmp_path,
    monkeypatch
):
    preparar_banco(
        tmp_path,
        monkeypatch
    )

    registrar_evento(
        "nfe.processada",
        {"numero_pedido": 1001},
        "evento-desativado"
    )

    monkeypatch.setattr(
        "services.eventos_integracao.integracao_configurada",
        lambda: False
    )

    resultado = enviar_eventos_pendentes()

    assert resultado["status"] == "desativada"
    assert len(listar_eventos_pendentes()) == 1


def test_webhook_usa_https_hmac_e_nao_envia_dados_sensiveis(
    tmp_path,
    monkeypatch
):
    preparar_banco(
        tmp_path,
        monkeypatch
    )

    evento = registrar_evento(
        "nfe.processada",
        {
            "numero_pedido": 1001,
            "numero_nfe": "123",
            "status_nfe": "aprovada"
        },
        "evento-webhook"
    )

    capturado = {}

    class Resposta:
        status_code = 200

        def raise_for_status(self):
            return None

    def post_fake(
        url,
        data,
        headers,
        timeout,
        allow_redirects
    ):
        capturado["url"] = url
        capturado["data"] = data
        capturado["headers"] = headers
        capturado["timeout"] = timeout
        capturado["allow_redirects"] = allow_redirects
        return Resposta()

    monkeypatch.setattr(
        gerente,
        "INTEGRACAO_GERENTE_ATIVA",
        True
    )
    monkeypatch.setattr(
        gerente,
        "GERENTE_ESTOQUE_WEBHOOK_URL",
        "https://gerente.exemplo/eventos"
    )
    monkeypatch.setattr(
        gerente,
        "GERENTE_ESTOQUE_WEBHOOK_SECRET",
        "segredo-teste"
    )
    monkeypatch.setattr(
        gerente.requests,
        "post",
        post_fake
    )

    assert gerente.enviar_evento(
        evento
    ) is True

    corpo = capturado["data"]
    envelope = json.loads(
        corpo.decode("utf-8")
    )
    dados = envelope["dados"]

    assert dados["numero_pedido"] == 1001
    assert "documento" not in json.dumps(dados).lower()
    assert "xml" not in dados
    assert "pdf" not in dados
    assert capturado["allow_redirects"] is False

    timestamp = capturado["headers"]["X-Webhook-Timestamp"]
    evento_id = capturado["headers"]["X-Webhook-Id"]

    mensagem = (
        f"{timestamp}.{evento_id}.".encode("utf-8")
        + corpo
    )

    assinatura_esperada = (
        "sha256="
        + hmac.new(
            b"segredo-teste",
            mensagem,
            hashlib.sha256
        ).hexdigest()
    )

    assert hmac.compare_digest(
        capturado["headers"]["X-Webhook-Signature"],
        assinatura_esperada
    )


def test_webhook_http_nao_e_considerado_configurado(
    monkeypatch
):
    monkeypatch.setattr(
        gerente,
        "INTEGRACAO_GERENTE_ATIVA",
        True
    )
    monkeypatch.setattr(
        gerente,
        "GERENTE_ESTOQUE_WEBHOOK_URL",
        "http://gerente.exemplo/eventos"
    )
    monkeypatch.setattr(
        gerente,
        "GERENTE_ESTOQUE_WEBHOOK_SECRET",
        "segredo"
    )

    assert gerente.integracao_configurada() is False
