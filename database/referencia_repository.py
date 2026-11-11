"""Diário local exclusivo dos testes de referência, nunca do fluxo web produtivo."""

import json
import uuid

from database.conexao import conectar_banco
from utils.data_hora import agora_utc


def reservar(identidade, escolhas):
    """Reserva atomicamente a identidade antes da primeira tentativa simulada."""
    conexao = conectar_banco()
    try:
        conexao.execute('BEGIN IMMEDIATE')
        conexao.execute('''CREATE TABLE IF NOT EXISTS referencias_fiscais (
            id TEXT PRIMARY KEY, organizacao TEXT NOT NULL, origem TEXT NOT NULL,
            pedido_id TEXT NOT NULL, destino TEXT NOT NULL, ambiente TEXT NOT NULL CHECK(ambiente='simulacao'),
            escolhas TEXT NOT NULL, estado TEXT NOT NULL, id_externo TEXT, criado_em TEXT NOT NULL,
            UNIQUE(organizacao,origem,pedido_id,destino,ambiente))''')
        existente = conexao.execute('''SELECT * FROM referencias_fiscais WHERE organizacao=? AND origem=?
            AND pedido_id=? AND destino=? AND ambiente=?''', identidade).fetchone()
        if existente:
            conexao.commit()
            return dict(existente), False
        identificador = str(uuid.uuid4())
        conexao.execute('''INSERT INTO referencias_fiscais(id,organizacao,origem,pedido_id,destino,ambiente,
            escolhas,estado,criado_em) VALUES(?,?,?,?,?,?,?,'creation_started',?)''',
            (identificador, *identidade, json.dumps(escolhas, sort_keys=True), agora_utc().isoformat()))
        conexao.commit()
        return {'id': identificador, 'estado': 'creation_started', 'id_externo': None}, True
    finally:
        conexao.close()


def atualizar(identificador, estado, id_externo=None):
    """Mantém resultado incerto e identificador sem liberar nova criação."""
    conexao = conectar_banco()
    try:
        conexao.execute('UPDATE referencias_fiscais SET estado=?, id_externo=COALESCE(?,id_externo) WHERE id=?',
                        (estado, id_externo, identificador))
        conexao.commit()
    finally:
        conexao.close()
