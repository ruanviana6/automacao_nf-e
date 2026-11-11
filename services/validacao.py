"""Validação básica DEMO; não substitui homologação fiscal."""

import math
from decimal import Decimal


def _numero_valido(valor):
    """Limita números DEMO finitos antes de conversões que podem estourar."""
    return type(valor) in (int, float) and -10**12 <= valor <= 10**12 and math.isfinite(valor)


def validar_cliente(cliente):
    """Recusa campos ausentes; não presume homologação de CPF/CNPJ ou tributação."""
    erros = []

    if not isinstance(cliente, dict):
        return ["Cliente inválido."]

    if not isinstance(cliente.get("nome"), str) or not cliente["nome"].strip():
        erros.append("Cliente sem nome.")

    if not isinstance(cliente.get("documento"), str) or not cliente['documento'].strip():
        erros.append("Cliente sem documento.")

    if not isinstance(cliente.get("uf"), str) or not cliente["uf"].strip():
        erros.append("Cliente sem UF.")

    return erros


def validar_produtos(produtos):
    """Exige produtos descritivos e valores finitos, sem booleanos numéricos."""
    erros = []

    if not isinstance(produtos, list) or not produtos:
        return ["Pedido sem produtos."]

    for indice, produto in enumerate(produtos, start=1):
        if not isinstance(produto, dict):
            erros.append(f"Produto {indice} inválido.")
            continue

        if not isinstance(produto.get('descricao'), str) or not produto['descricao'].strip():
            erros.append(f"Produto {indice} sem descrição.")

        quantidade = produto.get("quantidade")
        if not _numero_valido(quantidade) or quantidade <= 0:
            erros.append(f"Produto {indice} com quantidade inválida.")

        valor_unitario = produto.get("valor_unitario")
        if not _numero_valido(valor_unitario) or valor_unitario < 0:
            erros.append(f"Produto {indice} com valor unitário inválido.")

    return erros


def validar_valores(venda):
    """Compara os totais DEMO com decimais, sem calcular tributos presumidos."""
    erros = []

    produtos = venda.get("produtos", [])
    valor_total = venda.get("valor_total")

    if not _numero_valido(valor_total) or valor_total < 0:
        return ["Valor total da venda inválido."]

    if not isinstance(produtos, list):
        return ["Lista de produtos inválida."]

    total_calculado = Decimal(0)

    for produto in produtos:
        if not isinstance(produto, dict):
            continue

        quantidade = produto.get("quantidade")
        valor_unitario = produto.get("valor_unitario")

        if not _numero_valido(quantidade) or not _numero_valido(valor_unitario):
            return ['Item com valor ou quantidade inválida.']
        total_calculado += Decimal(str(quantidade)) * Decimal(str(valor_unitario))

    if round(total_calculado, 2) != round(Decimal(str(valor_total)), 2):
        erros.append(
            f"Valor total divergente: calculado {total_calculado:.2f}, informado {valor_total:.2f}."
        )

    return erros


def validar_venda(venda):
    """Reúne validações básicas, preservando erros para revisão humana."""
    erros = []

    if not isinstance(venda, dict):
        return ["Pedido inválido."]

    if not venda.get("numero_pedido"):
        erros.append("Pedido sem número.")

    erros.extend(validar_cliente(venda.get("cliente")))
    erros.extend(validar_produtos(venda.get("produtos")))
    erros.extend(validar_valores(venda))

    return erros
