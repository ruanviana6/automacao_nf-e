"""Persistência dos eventos que poderão ser consumidos por outros sistemas."""

import json
import uuid

from database.conexao import conectar_banco
from utils.data_hora import agora_utc


def inicializar_integracao():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos_integracao(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento_id TEXT NOT NULL UNIQUE,
            chave_idempotencia TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL,
            versao INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pendente',
            tentativas INTEGER NOT NULL DEFAULT 0,
            ultimo_erro TEXT,
            criado_em TEXT NOT NULL,
            enviado_em TEXT
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_eventos_integracao_status
        ON eventos_integracao(status)
    """)

    conexao.commit()
    conexao.close()


def registrar_evento(tipo, payload, chave_idempotencia, versao=1):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    evento_id = str(uuid.uuid4())
    criado_em = agora_utc().isoformat(timespec="seconds")

    cursor.execute("""
        INSERT OR IGNORE INTO eventos_integracao(
            evento_id,
            chave_idempotencia,
            tipo,
            versao,
            payload_json,
            status,
            tentativas,
            criado_em
        )
        VALUES (?, ?, ?, ?, ?, 'pendente', 0, ?)
    """, (
        evento_id,
        chave_idempotencia,
        tipo,
        versao,
        json.dumps(payload, ensure_ascii=False, sort_keys=True),
        criado_em
    ))

    if cursor.rowcount == 0:
        cursor.execute("""
            SELECT *
            FROM eventos_integracao
            WHERE chave_idempotencia = ?
        """, (chave_idempotencia,))
    else:
        cursor.execute("""
            SELECT *
            FROM eventos_integracao
            WHERE evento_id = ?
        """, (evento_id,))

    evento = cursor.fetchone()
    conexao.commit()
    conexao.close()
    return evento


def listar_eventos_pendentes(limite=100):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT *
        FROM eventos_integracao
        WHERE status IN ('pendente', 'erro')
        ORDER BY id
        LIMIT ?
    """, (limite,))

    eventos = cursor.fetchall()
    conexao.close()
    return eventos


def marcar_evento_enviado(evento_id):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE eventos_integracao
        SET status = 'enviado',
            tentativas = tentativas + 1,
            ultimo_erro = NULL,
            enviado_em = ?
        WHERE evento_id = ?
    """, (
        agora_utc().isoformat(timespec="seconds"),
        evento_id
    ))

    conexao.commit()
    conexao.close()


def marcar_evento_erro(evento_id, erro):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE eventos_integracao
        SET status = 'erro',
            tentativas = tentativas + 1,
            ultimo_erro = ?
        WHERE evento_id = ?
    """, (
        str(erro)[:1000],
        evento_id
    ))

    conexao.commit()
    conexao.close()
