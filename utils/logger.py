"""Configuração central de logs."""

import logging


def configurar_logger():
    """Retorna o logger principal da aplicação."""
    return logging.getLogger("automacao_nfe")
