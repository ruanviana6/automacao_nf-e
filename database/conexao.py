import sqlite3

from config.settings import CAMINHO_BANCO


# Cuida apenas de abrir a conexão com o banco.
# As regras de NF-e ficam em outro arquivo para o banco poder crescer com novos módulos no futuro.
def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    # Permite acessar os resultados pelo nome da coluna, além da posição.
    conexao.row_factory = sqlite3.Row
    return conexao
