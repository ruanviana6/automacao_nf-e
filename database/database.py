"""Banco de dados local da automação.

Vamos usar SQLite porque é simples e já vem com o Python.

Ele NÃO substituirá o GestãoClick.
Servirá apenas para nosso controle interno.
"""

import sqlite3


def criar_banco():
    # Nesta etapa você vai aprender:
    #
    # sqlite3.connect()
    # cursor
    # CREATE TABLE
    # commit()
    # close()
    #
    # A tabela deverá guardar informações como:
    # venda_id
    # numero_nf
    # status
    # data_emissao
    # caminhos dos arquivos
    pass


def nota_ja_processada(venda_id):
    # OBJETIVO:
    # consultar o SQLite e responder:
    #
    # True  -> venda já processada
    # False -> venda ainda não processada
    pass


def registrar_nota(nota):
    # OBJETIVO:
    # inserir no banco o histórico da nota.
    pass
