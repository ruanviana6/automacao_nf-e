from pathlib import Path

import services.arquivos as arquivos


def test_exclusao_manual_so_permite_pastas_controladas(tmp_path, monkeypatch):
    pasta_xml = tmp_path / "xml"
    pasta_pdf = tmp_path / "pdf"

    monkeypatch.setattr(arquivos, "PASTA_XML", pasta_xml)
    monkeypatch.setattr(arquivos, "PASTA_PDF", pasta_pdf)

    arquivos.preparar_pastas()

    permitido = pasta_xml / "teste.xml"
    permitido.write_text("<xml />", encoding="utf-8")

    fora = tmp_path / "fora.txt"
    fora.write_text("não apagar", encoding="utf-8")

    assert arquivos.excluir_arquivo_manual(permitido) is True
    assert permitido.exists() is False

    assert arquivos.excluir_arquivo_manual(fora) is False
    assert fora.exists() is True


def test_salvar_xml_e_pdf(tmp_path, monkeypatch):
    pasta_xml = tmp_path / "xml"
    pasta_pdf = tmp_path / "pdf"

    monkeypatch.setattr(arquivos, "PASTA_XML", pasta_xml)
    monkeypatch.setattr(arquivos, "PASTA_PDF", pasta_pdf)

    caminho_xml = arquivos.salvar_xml("<xml />", "teste.xml")
    caminho_pdf = arquivos.salvar_pdf(b"%PDF-teste", "teste.pdf")

    assert Path(caminho_xml).read_text(encoding="utf-8") == "<xml />"
    assert Path(caminho_pdf).read_bytes() == b"%PDF-teste"
