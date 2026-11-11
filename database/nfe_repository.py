from datetime import timedelta

from database.conexao import conectar_banco
from utils.data_hora import agora_utc


def _colunas_tabela(cursor, nome_tabela):
    cursor.execute(f"PRAGMA table_info({nome_tabela})")
    return {linha["name"] for linha in cursor.fetchall()}


def _adicionar_coluna_se_necessario(cursor, tabela, coluna, definicao):
    colunas = _colunas_tabela(cursor, tabela)

    if coluna not in colunas:
        cursor.execute(
            f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}"
        )


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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas_fiscais(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_pedido INTEGER NOT NULL,
            id_externo TEXT,
            numero_nfe TEXT,
            chave_nfe TEXT UNIQUE,
            status_nfe TEXT NOT NULL,
            usuario_gerador TEXT,
            data_emissao TEXT,
            origem TEXT NOT NULL DEFAULT 'gestaoclick',
            ambiente TEXT NOT NULL DEFAULT 'producao',
            criado_em TEXT NOT NULL
        )
    """)

    _adicionar_coluna_se_necessario(
        cursor,
        "notas_fiscais",
        "id_externo",
        "TEXT"
    )
    _adicionar_coluna_se_necessario(
        cursor,
        "notas_fiscais",
        "origem",
        "TEXT NOT NULL DEFAULT 'gestaoclick'"
    )
    _adicionar_coluna_se_necessario(
        cursor,
        "notas_fiscais",
        "ambiente",
        "TEXT NOT NULL DEFAULT 'producao'"
    )

    _adicionar_coluna_se_necessario(cursor, "notas_fiscais", "solicitacao_referencia", "TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS arquivos_nfe(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nota_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            caminho TEXT NOT NULL UNIQUE,
            removido INTEGER NOT NULL DEFAULT 0,
            removido_em TEXT,
            criado_em TEXT NOT NULL,
            FOREIGN KEY(nota_id) REFERENCES notas_fiscais(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estado_sistema(
            chave TEXT PRIMARY KEY,
            valor TEXT,
            atualizado_em TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_processamentos_numero_pedido
        ON processamentos_nfe(numero_pedido)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_notas_numero_pedido
        ON notas_fiscais(numero_pedido)
    """)

    conexao.commit()
    conexao.close()


def pedido_ja_processado(numero_pedido):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT numero_pedido
        FROM processamentos_nfe
        WHERE numero_pedido = ?
        LIMIT 1
    """, (numero_pedido,))
    resultado = cursor.fetchone()
    conexao.close()
    return resultado is not None


def buscar_nota_ativa_para_pedido(numero_pedido, ambiente="producao"):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            numero_pedido,
            id_externo,
            numero_nfe,
            chave_nfe,
            status_nfe,
            usuario_gerador,
            data_emissao,
            origem,
            ambiente,
            criado_em
        FROM notas_fiscais
        WHERE numero_pedido = ?
          AND ambiente = ?
        ORDER BY id DESC
        LIMIT 1
    """, (numero_pedido, ambiente))

    resultado = cursor.fetchone()
    conexao.close()
    return resultado


def nota_ja_emitida_para_pedido(numero_pedido, ambiente="producao"):
    nota = buscar_nota_ativa_para_pedido(
        numero_pedido,
        ambiente
    )

    if nota is None:
        return False

    return str(nota["status_nfe"]).lower() in (
        "aprovada",
        "simulada"
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
    """, (
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


def registrar_nota(nota):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    criado_em = agora_utc().isoformat(timespec="seconds")
    data_emissao = nota.get("data_emissao")

    if hasattr(data_emissao, "isoformat"):
        data_emissao = data_emissao.isoformat(timespec="seconds")

    cursor.execute("""
        INSERT INTO notas_fiscais(
            numero_pedido,
            id_externo,
            numero_nfe,
            chave_nfe,
            status_nfe,
            usuario_gerador,
            data_emissao,
            origem,
            ambiente,
            criado_em,
            solicitacao_referencia
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nota["numero_pedido"],
        nota.get("id_externo"),
        nota.get("numero_nfe"),
        nota.get("chave_nfe"),
        nota["status_nfe"],
        nota.get("usuario_gerador"),
        data_emissao,
        nota.get("origem", "gestaoclick"),
        nota.get("ambiente", "producao"),
        criado_em,
        nota.get("solicitacao_referencia")
    ))

    nota_id = cursor.lastrowid
    conexao.commit()
    conexao.close()
    return nota_id


def atualizar_nota(nota_id, dados):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    data_emissao = dados.get("data_emissao")

    if hasattr(data_emissao, "isoformat"):
        data_emissao = data_emissao.isoformat(timespec="seconds")

    cursor.execute("""
        UPDATE notas_fiscais
        SET numero_nfe = COALESCE(?, numero_nfe),
            chave_nfe = COALESCE(?, chave_nfe),
            status_nfe = COALESCE(?, status_nfe),
            data_emissao = COALESCE(?, data_emissao)
        WHERE id = ?
    """, (
        dados.get("numero_nfe"),
        dados.get("chave_nfe"),
        dados.get("status_nfe"),
        data_emissao,
        nota_id
    ))

    conexao.commit()
    conexao.close()


def registrar_arquivo_nfe(nota_id, tipo, caminho):
    tipo = tipo.strip().lower()

    if tipo not in ("xml", "pdf"):
        raise ValueError("Tipo de arquivo deve ser 'xml' ou 'pdf'.")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO arquivos_nfe(
            nota_id,
            tipo,
            caminho,
            removido,
            removido_em,
            criado_em
        )
        VALUES (?, ?, ?, 0, NULL, ?)
        ON CONFLICT(caminho) DO UPDATE SET
            nota_id = excluded.nota_id,
            tipo = excluded.tipo,
            removido = 0,
            removido_em = NULL,
            criado_em = excluded.criado_em
    """, (
        nota_id,
        tipo,
        str(caminho),
        agora_utc().isoformat(timespec="seconds")
    ))

    conexao.commit()
    conexao.close()


def marcar_arquivo_removido(caminho):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE arquivos_nfe
        SET removido = 1,
            removido_em = ?
        WHERE caminho = ?
    """, (
        agora_utc().isoformat(timespec="seconds"),
        str(caminho)
    ))

    conexao.commit()
    conexao.close()


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
    registros = cursor.fetchall()
    conexao.close()
    return registros


def listar_notas_recentes(dias=15):
    limite = (agora_utc() - timedelta(days=dias)).isoformat(timespec="seconds")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            numero_pedido,
            id_externo,
            numero_nfe,
            chave_nfe,
            status_nfe,
            usuario_gerador,
            data_emissao,
            origem,
            ambiente,
            criado_em
        FROM notas_fiscais
        WHERE criado_em >= ?
        ORDER BY criado_em DESC
    """, (limite,))

    notas = cursor.fetchall()
    conexao.close()
    return notas


def obter_estado(chave):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT valor
        FROM estado_sistema
        WHERE chave = ?
    """, (chave,))

    resultado = cursor.fetchone()
    conexao.close()

    if resultado is None:
        return None

    return resultado["valor"]


def definir_estado(chave, valor):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO estado_sistema(chave, valor, atualizado_em)
        VALUES (?, ?, ?)
        ON CONFLICT(chave) DO UPDATE SET
            valor = excluded.valor,
            atualizado_em = excluded.atualizado_em
    """, (
        chave,
        str(valor),
        agora_utc().isoformat(timespec="seconds")
    ))

    conexao.commit()
    conexao.close()


def buscar_legado_sem_escopo(numero_pedido, ambiente):
    """História antiga sem conta atribuída exige conferência, independentemente do status."""
    conexao = conectar_banco()
    try:
        return conexao.execute("SELECT id,id_externo FROM notas_fiscais WHERE numero_pedido=? AND ambiente=? AND solicitacao_referencia IS NULL LIMIT 1", (numero_pedido, ambiente)).fetchone()
    finally:
        conexao.close()
