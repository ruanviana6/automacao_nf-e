import sqlite3

from config.settings import (
    CAMINHO_BANCO,
    DB_BUSY_TIMEOUT_MS
)


# Mantemos o journal padrão do SQLite nesta V1.
# A automação é de um único processo e a concorrência é bloqueada na aplicação.
def conectar_banco():
    CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(
        CAMINHO_BANCO,
        timeout=DB_BUSY_TIMEOUT_MS / 1000
    )

    conexao.row_factory = sqlite3.Row

    # Garante integridade dos relacionamentos.
    conexao.execute("PRAGMA foreign_keys = ON")

    # Evita falha imediata se o banco estiver momentaneamente ocupado.
    conexao.execute(
        f"PRAGMA busy_timeout = {int(DB_BUSY_TIMEOUT_MS)}"
    )

    # Prioriza durabilidade dos commits em uma automação fiscal.
    conexao.execute("PRAGMA synchronous = FULL")

    return conexao
