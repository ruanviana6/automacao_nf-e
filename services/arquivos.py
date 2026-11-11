"""Controle dos XMLs e PDFs salvos temporariamente."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from config.settings import (
    PASTA_XML,
    PASTA_PDF,
    RETENCAO_ARQUIVOS_DIAS
)
from utils.data_hora import agora_utc


def preparar_pastas():
    PASTA_XML.mkdir(parents=True, exist_ok=True)
    PASTA_PDF.mkdir(parents=True, exist_ok=True)


def salvar_xml(conteudo, nome_arquivo):
    preparar_pastas()
    caminho_arquivo = PASTA_XML / nome_arquivo
    caminho_arquivo.write_text(conteudo, encoding="utf-8")
    return caminho_arquivo


def salvar_pdf(conteudo, nome_arquivo):
    preparar_pastas()
    caminho_arquivo = PASTA_PDF / nome_arquivo
    caminho_arquivo.write_bytes(conteudo)
    return caminho_arquivo


def arquivo_expirado(caminho_arquivo, dias=RETENCAO_ARQUIVOS_DIAS):
    caminho_arquivo = Path(caminho_arquivo)

    if not caminho_arquivo.exists():
        return False

    timestamp_modificacao = caminho_arquivo.stat().st_mtime
    data_modificacao = datetime.fromtimestamp(
        timestamp_modificacao,
        tz=timezone.utc
    )

    limite = agora_utc() - timedelta(days=dias)
    return data_modificacao < limite


def limpar_arquivos_expirados(dias=RETENCAO_ARQUIVOS_DIAS):
    preparar_pastas()
    pastas = [PASTA_XML, PASTA_PDF]
    arquivos_excluidos = []

    for pasta in pastas:
        for arquivo in pasta.iterdir():
            if arquivo.is_file() and arquivo_expirado(arquivo, dias):
                arquivo.unlink()
                arquivos_excluidos.append(arquivo)

    return arquivos_excluidos


def listar_arquivos_locais():
    preparar_pastas()

    return sorted(
        [
            arquivo
            for pasta in (PASTA_XML, PASTA_PDF)
            for arquivo in pasta.iterdir()
            if arquivo.is_file()
        ],
        key=lambda arquivo: str(arquivo)
    )


def excluir_arquivo_manual(caminho_arquivo):
    caminho_arquivo = Path(caminho_arquivo)

    if not caminho_arquivo.exists():
        return False

    if not caminho_arquivo.is_file():
        return False

    caminho_resolvido = caminho_arquivo.resolve()
    pasta_xml = PASTA_XML.resolve()
    pasta_pdf = PASTA_PDF.resolve()

    if (
        pasta_xml not in caminho_resolvido.parents
        and pasta_pdf not in caminho_resolvido.parents
    ):
        return False

    caminho_arquivo.unlink()
    return True
