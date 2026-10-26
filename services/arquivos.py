"""Controle dos XMLs e PDFs salvos temporariamente."""

from pathlib import Path


PASTA_XML = Path("data/xml")
PASTA_PDF = Path("data/pdf")


def preparar_pastas():
    # Aqui você aprenderá pathlib.
    #
    # O objetivo será criar as pastas automaticamente
    # caso ainda não existam.
    pass


def salvar_xml(conteudo, nome_arquivo):
    # OBJETIVO:
    # receber o conteúdo do XML
    # e gravar dentro de data/xml.
    pass


def salvar_pdf(conteudo, nome_arquivo):
    # Mesmo raciocínio do XML.
    pass


def limpar_arquivos_expirados(dias):
    # FUTURAMENTE:
    #
    # 1. descobrir a data atual;
    # 2. verificar arquivos antigos;
    # 3. comparar com 30 ou 90 dias;
    # 4. apagar SOMENTE os arquivos locais.
    #
    # Essa função não deve apagar nada no GestãoClick.
    pass
