import api.mock_gestaoclick as mock_api
import database.conexao as conexao
import services.arquivos as arquivos

from database.nfe_repository import inicializar_banco
from services.notas import processar_nota


def test_fluxo_simulado_salva_nota_e_impede_duplicidade(tmp_path, monkeypatch):
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
