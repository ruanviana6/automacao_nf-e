"""Logs estruturados e limpeza dos arquivos de log."""

import json
import logging
from datetime import datetime, timedelta, timezone

from config.settings import (
    PASTA_LOGS,
    RETENCAO_LOGS_DIAS
)


LIMITE_MENSAGEM_LOG = 4000


def _sanitizar_texto(valor):
    texto = str(valor)
    texto = texto.replace("\r", "\\r")
    texto = texto.replace("\n", "\\n")
    return texto[:LIMITE_MENSAGEM_LOG]


class JsonFormatter(logging.Formatter):
    def format(self, record):
        evento = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(timespec="seconds"),
            "nivel": record.levelname,
            "logger": record.name,
            "mensagem": _sanitizar_texto(
                record.getMessage()
            )
        }

        if record.exc_info:
            evento["erro"] = _sanitizar_texto(
                self.formatException(
                    record.exc_info
                )
            )

        return json.dumps(
            evento,
            ensure_ascii=False
        )


def limpar_logs_expirados(dias=RETENCAO_LOGS_DIAS):
    PASTA_LOGS.mkdir(
        parents=True,
        exist_ok=True
    )

    limite = (
        datetime.now(timezone.utc)
        - timedelta(days=dias)
    )
    removidos = []

    for arquivo in PASTA_LOGS.glob("*.log"):
        data_modificacao = datetime.fromtimestamp(
            arquivo.stat().st_mtime,
            tz=timezone.utc
        )

        if data_modificacao < limite:
            arquivo.unlink()
            removidos.append(arquivo)

    return removidos


def configurar_logger():
    PASTA_LOGS.mkdir(
        parents=True,
        exist_ok=True
    )

    logger = logging.getLogger(
        "automacao_nfe"
    )
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    nome_arquivo = datetime.now().strftime(
        "automacao_%Y-%m-%d.log"
    )
    caminho_log = (
        PASTA_LOGS
        / nome_arquivo
    )

    formato = JsonFormatter()

    arquivo_handler = logging.FileHandler(
        caminho_log,
        encoding="utf-8"
    )
    arquivo_handler.setFormatter(
        formato
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        formato
    )

    logger.addHandler(
        arquivo_handler
    )
    logger.addHandler(
        console_handler
    )
    logger.propagate = False

    return logger
