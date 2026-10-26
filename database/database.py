"""Banco local para histórico e controle de duplicidade."""

import sqlite3

DB_PATH = "notas.db"


def criar_banco():
    """Cria a estrutura inicial do banco SQLite."""
    # TODO: definir tabela após validar quais identificadores a API fornece.
    pass


def nota_ja_processada(venda_id):
    """Verifica se uma venda já foi processada."""
    pass


def registrar_nota(nota):
    """Registra o resultado do processamento de uma nota."""
    pass
