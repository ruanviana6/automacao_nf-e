import sqlite3
from pathlib import Path
from utils.data_hora import agora_utc

# Criação de um caminho de um arquivo para um banco de dados SQLite
# Path facilita montar o caminho sem depender de barras específicas do sistema
CAMINHO_BANCO = Path("data")/"automacao_nfe.db"

# Abre a conexão com o SQLite e devolve a conexão pronta para uso
def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    # row_factory permite acessar os resultados pelo nome da coluna, e não só pela posição
    conexao.row_factory = sqlite3.Row
    return conexao

# Garante que a tabela principal de processamentos exista antes das gravações
def inicializar_banco():
    conexao = conectar_banco()
    # O cursor é usado para enviar comandos SQL para o banco
    cursor = conexao.cursor()
    # IF NOT EXISTS evita erro ou recriação da tabela quando ela já existe
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
    # commit confirma as alterações feitas no banco
    conexao.commit()
    # Fecha a conexão depois do trabalho para não deixá-la aberta sem necessidade
    conexao.close()

# Permite testar a inicialização quando este arquivo é executado diretamente
if __name__ == "__main__":
    inicializar_banco()

    print("Banco inicializado com sucesso.")

# Consulta se já existe algum registro para o número do pedido informado
def pedido_ja_processado(numero_pedido):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    # O ? recebe o valor separadamente, evitando montar SQL diretamente com o dado
    cursor.execute("""
        SELECT numero_pedido
        FROM processamentos_nfe
        WHERE numero_pedido = ?
    """, (numero_pedido,))
    # fetchone() pega somente uma linha do resultado, suficiente para saber se existe registro
    resultado = cursor.fetchone()
    conexao.close()
    # Retorna True se encontrou algo e False quando o resultado foi None
    return resultado is not None

# Bloco temporário de teste para conferir a consulta de pedido já processado
if __name__ == "__main__":

    inicializar_banco()

    print(
        "Pedido 1001 já processado?",
        pedido_ja_processado(1001)
    )

# Recebe o dicionário criado no main e grava o histórico do processamento no SQLite
def registrar_processamento(registro):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    # Guarda quando o registro foi criado, em UTC e no formato ISO
    criado_em = agora_utc().isoformat(timespec="seconds")
    data_hora_autorizacao = registro["data_hora_autorizacao"]
    # Nem todo pedido possui autorização; só converte a data quando ela realmente existe
    if data_hora_autorizacao is not None:
        data_hora_autorizacao = data_hora_autorizacao.isoformat(timespec="seconds")
    # Cada ? corresponde, na mesma ordem, a um valor da tupla enviada abaixo
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

# Busca todo o histórico de processamentos salvo no banco
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
    # fetchall() retorna todas as linhas encontradas pela consulta
    registros = cursor.fetchall()
    conexao.close()
    return registros