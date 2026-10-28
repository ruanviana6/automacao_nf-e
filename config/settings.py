from pathlib import Path

# Mantém em um único lugar valores usados por diferentes partes do sistema.
# Assim uma mudança de prazo, fuso ou caminho não exige procurar valores espalhados pelo projeto.
RETENCAO_ARQUIVOS_DIAS = 45
RETENCAO_LOGS_DIAS = 45
FUSO_HORARIO = "America/Fortaleza"

# Caminhos principais usados pela aplicação.
PASTA_DADOS = Path("data")
PASTA_XML = PASTA_DADOS / "xml"
PASTA_PDF = PASTA_DADOS / "pdf"
PASTA_LOGS = Path("logs")
CAMINHO_BANCO = PASTA_DADOS / "automacao_nfe.db"
