import os
from pathlib import Path

from dotenv import load_dotenv


# Carrega o arquivo .env quando ele existir.
# Credenciais reais ficam fora do GitHub.
load_dotenv()


def _inteiro_env(nome, padrao):
    valor = os.getenv(nome)
    if not valor:
        return padrao
    return int(valor)


# Configurações gerais
RETENCAO_ARQUIVOS_DIAS = _inteiro_env("RETENCAO_ARQUIVOS_DIAS", 45)
RETENCAO_LOGS_DIAS = _inteiro_env("RETENCAO_LOGS_DIAS", 45)
RELATORIO_DIAS = _inteiro_env("RELATORIO_DIAS", 15)
FUSO_HORARIO = os.getenv("FUSO_HORARIO", "America/Fortaleza")

# Caminhos usados pela aplicação
PASTA_DADOS = Path("data")
PASTA_XML = PASTA_DADOS / "xml"
PASTA_PDF = PASTA_DADOS / "pdf"
PASTA_RELATORIOS = PASTA_DADOS / "relatorios"
PASTA_LOGS = Path("logs")
CAMINHO_BANCO = PASTA_DADOS / "automacao_nfe.db"

# API GestãoClick
GESTAOCLICK_BASE_URL = os.getenv("GESTAOCLICK_BASE_URL", "").rstrip("/")
GESTAOCLICK_ACCESS_TOKEN = os.getenv("GESTAOCLICK_ACCESS_TOKEN", "")
GESTAOCLICK_SECRET_ACCESS = os.getenv("GESTAOCLICK_SECRET_ACCESS", "")
GESTAOCLICK_TIMEOUT = _inteiro_env("GESTAOCLICK_TIMEOUT", 30)

# E-mail
EMAIL_USUARIO = os.getenv("EMAIL_USUARIO", "")
EMAIL_SENHA = os.getenv("EMAIL_SENHA", "")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = _inteiro_env("SMTP_PORT", 587)
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").strip().lower() == "true"
