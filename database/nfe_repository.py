from database.conexao import conectar_banco
from utils.data_hora import agora_utc


# Reúne somente as operações de banco relacionadas ao processamento de NF-e.
# Futuramente estoque e outros módulos podem ter seus próprios arquivos de acesso ao banco.
def inicializar_banco():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    # IF NOT EXISTS evita recriar a tabela quando ela já existe.
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


# Consulta se já existe algum registro para o número do pedido informado.
def pedido_ja_processado(numero_pedido):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    # O ? recebe o valor separadamente, evitando montar SQL diretamente com o dado.
    cursor.execute("""
        SELECT numero_pedido
        FROM processamentos_nfe
        WHERE numero_pedido = ?
    """, (numero_pedido,))
    # Uma linha já é suficiente para saber se existe registro.
    resultado = cursor.fetchone()
    conexao.close()
    return resultado is not None


# Recebe o dicionário criado no main e grava o histórico do processamento no SQLite.
def registrar_processamento(registro):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    # Guarda quando o registro foi criado usando o padrão UTC do sistema.
    criado_em = agora_utc().isoformat(timespec="seconds")
    data_hora_autorizacao = registro["data_hora_autorizacao"]
    # Nem todo pedido possui autorização; só converte a data quando ela existe.
    if data_hora_autorizacao is not None:
        data_hora_autorizacao = data_hora_autorizacao.isoformat(timespec="seconds")
    # Cada ? corresponde, na mesma ordem, aos valores enviados abaixo.
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


# Busca todo o histórico de processamentos salvo no banco.
def listar_processamentos():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("""
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
    # fetchall() retorna todas as linhas encontradas pela consulta.
    registros = cursor.fetchall()
    conexao.close()
    return registros
