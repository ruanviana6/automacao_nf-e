"""Armazenamento temporário de XML e PDF."""

from pathlib import Path

PASTA_XML = Path("data/xml")
PASTA_PDF = Path("data/pdf")


def preparar_pastas():
    """Garante que as pastas locais existam."""
    PASTA_XML.mkdir(parents=True, exist_ok=True)
    PASTA_PDF.mkdir(parents=True, exist_ok=True)


def limpar_arquivos_expirados():
    """Remove somente arquivos locais que ultrapassaram a retenção."""
    # TODO: implementar retenção de 30 ou 90 dias.
    # Esta função não deve excluir ou cancelar notas no GestãoClick.
    pass
