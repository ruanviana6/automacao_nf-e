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


def test_webhook_recebe_envelope_sem_dados_sensiveis(
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
        def raise_for_status(self):
            return None

    def post_fake(url, json, headers, timeout):
        capturado["url"] = url
        capturado["json"] = json
        capturado["headers"] = headers
        capturado["timeout"] = timeout
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
        gerente.requests,
        "post",
        post_fake
    )

    assert gerente.enviar_evento(
        evento
    ) is True

    dados = capturado["json"]["dados"]

    assert dados["numero_pedido"] == 1001
    assert "documento" not in json.dumps(dados).lower()
    assert "xml" not in dados
    assert "pdf" not in dados
