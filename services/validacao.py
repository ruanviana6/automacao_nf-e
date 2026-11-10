"""Validações dos dados antes de tentar emitir uma NF-e."""


def validar_cliente(cliente):
    erros = []

    if not isinstance(cliente, dict):
        return ["Cliente inválido."]

    if not str(cliente.get("nome", "")).strip():
        erros.append("Cliente sem nome.")

    if not str(cliente.get("documento", "")).strip():
        erros.append("Cliente sem documento.")

    if not str(cliente.get("uf", "")).strip():
        erros.append("Cliente sem UF.")

    return erros


def validar_produtos(produtos):
    erros = []

    if not isinstance(produtos, list) or not produtos:
        return ["Pedido sem produtos."]

    for indice, produto in enumerate(produtos, start=1):
        if not str(produto.get("descricao", "")).strip():
            erros.append(f"Produto {indice} sem descrição.")

        quantidade = produto.get("quantidade")
        if not isinstance(quantidade, (int, float)) or quantidade <= 0:
            erros.append(f"Produto {indice} com quantidade inválida.")

        valor_unitario = produto.get("valor_unitario")
        if not isinstance(valor_unitario, (int, float)) or valor_unitario < 0:
            erros.append(f"Produto {indice} com valor unitário inválido.")

    return erros


def validar_valores(venda):
    erros = []

    produtos = venda.get("produtos", [])
    valor_total = venda.get("valor_total")

    if not isinstance(valor_total, (int, float)) or valor_total < 0:
        return ["Valor total da venda inválido."]

    total_calculado = 0

    for produto in produtos:
        quantidade = produto.get("quantidade")
        valor_unitario = produto.get("valor_unitario")

        if isinstance(quantidade, (int, float)) and isinstance(valor_unitario, (int, float)):
            total_calculado += quantidade * valor_unitario

    # Arredonda para duas casas para comparar valores monetários desta primeira versão.
    if round(total_calculado, 2) != round(valor_total, 2):
        erros.append(
            f"Valor total divergente: calculado {total_calculado:.2f}, informado {valor_total:.2f}."
        )

    return erros


def validar_venda(venda):
    erros = []

    if not isinstance(venda, dict):
        return ["Pedido inválido."]

    if not venda.get("numero_pedido"):
        erros.append("Pedido sem número.")

    erros.extend(validar_cliente(venda.get("cliente")))
    erros.extend(validar_produtos(venda.get("produtos")))
    erros.extend(validar_valores(venda))

    return erros
