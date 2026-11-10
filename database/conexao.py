import sqlite3

from config.settings import CAMINHO_BANCO


# Cuida apenas de abrir a conexão com o banco.
# As regras de NF-e ficam em outro arquivo para o banco poder crescer com novos módulos no futuro.
def conectar_banco():
    CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(CAMINHO_BANCO)
    # Ativa relacionamentos entre tabelas no SQLite.
    conexao.execute("PRAGMA foreign_keys = ON")
    # Permite acessar os resultados pelo nome da coluna, além da posição.
    conexao.row_factory = sqlite3.Row
    return conexao
