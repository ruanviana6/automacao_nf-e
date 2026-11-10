"""Envio do relatório por e-mail."""

import smtplib
from email.message import EmailMessage
from pathlib import Path

from config.settings import (
    EMAIL_USUARIO,
    EMAIL_SENHA,
    EMAIL_DESTINO,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USE_TLS
)


def enviar_relatorio(caminho_relatorio):
    caminho_relatorio = Path(caminho_relatorio)

    if not caminho_relatorio.exists():
        raise FileNotFoundError("Relatório não encontrado.")

    if not all([
        EMAIL_USUARIO,
        EMAIL_SENHA,
        EMAIL_DESTINO,
        SMTP_HOST
    ]):
        raise ValueError("Configurações de e-mail incompletas.")

    mensagem = EmailMessage()
    mensagem["Subject"] = "Relatório quinzenal de NF-e"
    mensagem["From"] = EMAIL_USUARIO
    mensagem["To"] = EMAIL_DESTINO
    mensagem.set_content(
        "Segue em anexo o relatório das NF-e processadas no período."
    )

    conteudo = caminho_relatorio.read_bytes()

    mensagem.add_attachment(
        conteudo,
        maintype="text",
        subtype="csv",
        filename=caminho_relatorio.name
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as servidor:
        if SMTP_USE_TLS:
            servidor.starttls()

        servidor.login(
            EMAIL_USUARIO,
            EMAIL_SENHA
        )
        servidor.send_message(mensagem)

    return True
