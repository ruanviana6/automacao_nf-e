import pytest

import api.mock_gestaoclick as mock_api
import database.conexao as conexao
import services.arquivos as arquivos

from database.nfe_repository import (
    buscar_nota_ativa_para_pedido,
    inicializar_banco
)
from services.notas import processar_nota


def preparar_ambiente(tmp_path, monkeypatch):
    monkeypatch.setattr(
        conexao,
        "CAMINHO_BANCO",
        tmp_path / "teste.db"
    )
    monkeypatch.setattr(
        arquivos,
        "PASTA_XML",
        tmp_path / "xml"
    )
    monkeypatch.setattr(
        arquivos,
        "PASTA_PDF",
        tmp_path / "pdf"
    )

    inicializar_banco()


def test_fluxo_simulado_salva_nota_e_impede_duplicidade(tmp_path, monkeypatch):
    preparar_ambiente(
        tmp_path,
        monkeypatch
    )

    provedor = mock_api.MockGestaoClickAPI()
    pedido = provedor.buscar_pedidos_pendentes()[0]

    resultado = processar_nota(
        pedido,
        provedor,
        "TESTE"
    )

    assert resultado["status"] == "simulada"
    assert resultado["caminho_xml"].exists()
    assert resultado["caminho_pdf"].exists()

    repeticao = processar_nota(
        pedido,
        provedor,
        "TESTE"
    )

    assert repeticao["status"] == "duplicada"


def test_id_criado_fica_salvo_quando_emissao_falha(tmp_path, monkeypatch):
    preparar_ambiente(
        tmp_path,
        monkeypatch
    )

    class ProvedorComFalha(mock_api.MockGestaoClickAPI):
        def emitir_nota(self, id_externo):
            raise TimeoutError(
                "Falha simulada após criação."
            )

    provedor = ProvedorComFalha()
    pedido = provedor.buscar_pedidos_pendentes()[0]

    with pytest.raises(TimeoutError):
        processar_nota(
            pedido,
            provedor,
            "TESTE"
        )

    nota = buscar_nota_ativa_para_pedido(
        pedido["numero_pedido"],
        "simulacao"
    )

    assert nota is not None
    assert nota["id_externo"] == "SIM-1001"
    assert nota["status_nfe"] == "criada"

    nova_tentativa = processar_nota(
        pedido,
        provedor,
        "TESTE"
    )

    assert nova_tentativa["status"] == "pendente_consulta"
