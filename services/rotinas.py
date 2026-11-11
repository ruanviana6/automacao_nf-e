"""Rotinas automáticas e manuais que não dependem da API do ERP."""

from datetime import datetime, timedelta

from config.settings import (
    EMAIL_ENVIO_AUTOMATICO,
    RELATORIO_DIAS
)
from database.nfe_repository import (
    definir_estado,
    listar_notas_recentes,
    marcar_arquivo_removido,
    obter_estado
)
from services.arquivos import limpar_arquivos_expirados
from services.email_service import email_configurado, enviar_relatorio
from services.relatorio import gerar_relatorio
from utils.data_hora import agora_utc
from utils.logger import limpar_logs_expirados


CHAVE_ULTIMO_RELATORIO = "ultimo_relatorio_quinzenal"


def executar_limpeza():
    arquivos_excluidos = limpar_arquivos_expirados()

    for caminho in arquivos_excluidos:
        marcar_arquivo_removido(caminho)

    logs_excluidos = limpar_logs_expirados()

    return {
        "arquivos": arquivos_excluidos,
        "logs": logs_excluidos
    }


def gerar_relatorio_periodo(dias=RELATORIO_DIAS):
    notas = listar_notas_recentes(dias)
    caminho = gerar_relatorio(notas)

    return {
        "caminho": caminho,
        "quantidade_notas": len(notas)
    }


def enviar_relatorio_periodo(dias=RELATORIO_DIAS):
    resultado = gerar_relatorio_periodo(dias)
    enviar_relatorio(resultado["caminho"])
    return resultado


def _relatorio_esta_vencido():
    ultimo = obter_estado(CHAVE_ULTIMO_RELATORIO)

    if not ultimo:
        return True

    try:
        ultima_data = datetime.fromisoformat(ultimo)
    except ValueError:
        return True

    return agora_utc() >= ultima_data + timedelta(days=RELATORIO_DIAS)


def executar_relatorio_automatico(logger=None):
    if not EMAIL_ENVIO_AUTOMATICO:
        return {"status": "desativado"}

    if not _relatorio_esta_vencido():
        return {"status": "ainda_no_prazo"}

    if not email_configurado():
        if logger:
            logger.warning(
                "Envio automático de relatório ativado, mas o e-mail não está configurado."
            )
        return {"status": "email_nao_configurado"}

    resultado = enviar_relatorio_periodo()

    definir_estado(
        CHAVE_ULTIMO_RELATORIO,
        agora_utc().isoformat(timespec="seconds")
    )

    if logger:
        logger.info(
            "Relatório quinzenal enviado com %s nota(s).",
            resultado["quantidade_notas"]
        )

    return {
        "status": "enviado",
        **resultado
    }
