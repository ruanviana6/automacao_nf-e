import sqlite3
from pathlib import Path
from utils.data_hora import agora_utc

# Criação de um caminho de um arquivo para um banco de dados SQLite
CAMINHO_BANCO = Path("data")/"automacao_nfe.db"

def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao

def inicializar_banco():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processamentos_nfe(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_pedido INTEGER NOT NULL,
            status_pedido TEXT NOT NULL,
            liberado INTEGER NOT NULL,
            usuario_autorizador TEXT,
            data_hora_autorizacao TEXT,
            status_processamento TEXT NOT NULL,
            criado_em TEXT NOT NULL
        )
    """)
    conexao.commit()
    conexao.close()

if __name__ == "__main__":
    inicializar_banco()

    print("Banco inicializado com sucesso.")

def pedido_ja_processado(numero_pedido):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT numero_pedido
        FROM processamentos_nfe
        WHERE numero_pedido = ?
    """, (numero_pedido,))
    resultado = cursor.fetchone()
    conexao.close()
    return resultado is not None

if __name__ == "__main__":

    inicializar_banco()

    print(
        "Pedido 1001 já processado?",
        pedido_ja_processado(1001)
    )

def registrar_processamento(registro):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    criado_em = agora_utc().isoformat(timespec="seconds")
    data_hora_autorizacao = registro["data_hora_autorizacao"]
    if data_hora_autorizacao is not None:
        data_hora_autorizacao = data_hora_autorizacao.isoformat(timespec="seconds")
    cursor.execute("""
        INSERT INTO processamentos_nfe(
            numero_pedido,
            status_pedido,
            liberado,
            usuario_autorizador,
            data_hora_autorizacao,
            status_processamento,
            criado_em
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,(
            registro["numero_pedido"],
            registro["status_pedido"],
            registro["liberado"],
            registro["usuario_autorizador"],
            data_hora_autorizacao,
            registro["status_processamento"],
            criado_em
    ))
    conexao.commit()
    conexao.close()

def listar_processamentos():
    conexao = conectar_banco()
    cursor= conexao.cursor()
    cursor.execute ("""
    SELECT
        id,
        numero_pedido,
        status_pedido,
        liberado,
        usuario_autorizador,
        data_hora_autorizacao,
        status_processamento,
        criado_em
    FROM processamentos_nfe
    ORDER BY id
    """)
    registros = cursor.fetchall()
    conexao.close()
    return registros