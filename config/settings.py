import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def _inteiro_env(nome, padrao):
    valor = os.getenv(nome)
    if not valor:
        return padrao
    return int(valor)


def _float_env(nome, padrao):
    valor = os.getenv(nome)
    if not valor:
        return padrao
    return float(valor)


def _booleano_env(nome, padrao=False):
    valor = os.getenv(nome)

    if valor is None:
        return padrao

    return valor.strip().lower() in ("1", "true", "sim", "s", "yes")


# Configurações gerais
RETENCAO_ARQUIVOS_DIAS = _inteiro_env("RETENCAO_ARQUIVOS_DIAS", 45)
RETENCAO_LOGS_DIAS = _inteiro_env("RETENCAO_LOGS_DIAS", 45)
RELATORIO_DIAS = _inteiro_env("RELATORIO_DIAS", 15)
FUSO_HORARIO = os.getenv("FUSO_HORARIO", "America/Fortaleza")
MODO_SIMULACAO = _booleano_env("MODO_SIMULACAO", True)
USUARIO_EXECUCAO = os.getenv("USUARIO_EXECUCAO", "").strip()

# Caminhos usados pela aplicação
PASTA_DADOS = Path("data")
PASTA_XML = PASTA_DADOS / "xml"
PASTA_PDF = PASTA_DADOS / "pdf"
PASTA_RELATORIOS = PASTA_DADOS / "relatorios"
PASTA_LOGS = Path("logs")
CAMINHO_BANCO = PASTA_DADOS / "automacao_nfe.db"
CAMINHO_LOCK = PASTA_DADOS / "automacao_nfe.lock"

# SQLite
DB_BUSY_TIMEOUT_MS = _inteiro_env("DB_BUSY_TIMEOUT_MS", 10000)

# Configuração legado: apenas para compatibilidade do cliente HTTP antigo.
# NÃO usar as chaves genéricas no roteamento entre Atacado e Varejo.
GESTAOCLICK_BASE_URL = os.getenv("GESTAOCLICK_BASE_URL", "").rstrip("/")
GESTAOCLICK_ACCESS_TOKEN = os.getenv("GESTAOCLICK_ACCESS_TOKEN", "")
GESTAOCLICK_SECRET_ACCESS = os.getenv("GESTAOCLICK_SECRET_ACCESS", "")
GESTAOCLICK_CONNECT_TIMEOUT = _float_env("GESTAOCLICK_CONNECT_TIMEOUT", 3.5)
GESTAOCLICK_READ_TIMEOUT = _float_env(
    "GESTAOCLICK_READ_TIMEOUT", _float_env("GESTAOCLICK_TIMEOUT", 30.0)
)

# Legado desativado. Estes nomes não são usados pelo provedor vigente.
GESTAOCLICK_ATACADO_BASE_URL = os.getenv("GESTAOCLICK_ATACADO_BASE_URL", "").rstrip("/")
GESTAOCLICK_ATACADO_ACCESS_TOKEN = os.getenv("GESTAOCLICK_ATACADO_ACCESS_TOKEN", "")
GESTAOCLICK_ATACADO_SECRET_ACCESS = os.getenv("GESTAOCLICK_ATACADO_SECRET_ACCESS", "")
GESTAOCLICK_VAREJO_BASE_URL = os.getenv("GESTAOCLICK_VAREJO_BASE_URL", "").rstrip("/")
GESTAOCLICK_VAREJO_ACCESS_TOKEN = os.getenv("GESTAOCLICK_VAREJO_ACCESS_TOKEN", "")
GESTAOCLICK_VAREJO_SECRET_ACCESS = os.getenv("GESTAOCLICK_VAREJO_SECRET_ACCESS", "")
# Mesmo true não ativa emissão sem os endpoints e regras fiscais confirmados.
NFE_EMISSAO_REAL_HABILITADA = False  # Emissão é sempre manual no GestãoClick.

# Conexão única e lojas distintas. Não utilizar as duas credenciais legadas.
GESTAOCLICK_API_BASE_URL = os.getenv('GESTAOCLICK_API_BASE_URL', '').rstrip('/')
GESTAOCLICK_API_ACCESS_TOKEN = os.getenv('GESTAOCLICK_API_ACCESS_TOKEN', '')
GESTAOCLICK_API_SECRET_ACCESS = os.getenv('GESTAOCLICK_API_SECRET_ACCESS', '')
GESTAOCLICK_LOJA_ATACADO_ID = os.getenv('GESTAOCLICK_LOJA_ATACADO_ID', '').strip()
GESTAOCLICK_LOJA_VAREJO_ID = os.getenv('GESTAOCLICK_LOJA_VAREJO_ID', '').strip()
NFE_CADASTRO_REAL_HABILITADO = _booleano_env('NFE_CADASTRO_REAL_HABILITADO', False)

# E-mail
EMAIL_USUARIO = os.getenv("EMAIL_USUARIO", "")
EMAIL_SENHA = os.getenv("EMAIL_SENHA", "")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = _inteiro_env("SMTP_PORT", 587)
SMTP_USE_TLS = _booleano_env("SMTP_USE_TLS", True)
EMAIL_ENVIO_AUTOMATICO = _booleano_env("EMAIL_ENVIO_AUTOMATICO", False)

# Integração futura com o Gerente de Estoque
INTEGRACAO_GERENTE_ATIVA = _booleano_env("INTEGRACAO_GERENTE_ATIVA", False)
GERENTE_ESTOQUE_WEBHOOK_URL = os.getenv("GERENTE_ESTOQUE_WEBHOOK_URL", "").strip()
GERENTE_ESTOQUE_WEBHOOK_SECRET = os.getenv("GERENTE_ESTOQUE_WEBHOOK_SECRET", "").strip()
GERENTE_ESTOQUE_WEBHOOK_TOKEN = os.getenv("GERENTE_ESTOQUE_WEBHOOK_TOKEN", "").strip()
GERENTE_ESTOQUE_CONNECT_TIMEOUT = _float_env("GERENTE_ESTOQUE_CONNECT_TIMEOUT", 3.5)
GERENTE_ESTOQUE_READ_TIMEOUT = _float_env(
    "GERENTE_ESTOQUE_READ_TIMEOUT", _float_env("GERENTE_ESTOQUE_TIMEOUT", 10.0)
)
