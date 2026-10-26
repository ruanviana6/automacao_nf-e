"""Validação dos dados antes de tentar emitir uma NF-e.

Este será um dos primeiros arquivos que você realmente vai programar.
"""


def validar_cliente(cliente):
    # OBJETIVO:
    # verificar se o cliente possui os dados mínimos necessários.
    #
    # Exemplo de lógica que você vai construir:
    #
    # if cliente não tiver nome:
    #     adicionar "Cliente sem nome" à lista de erros
    #
    # if cliente não tiver documento:
    #     adicionar outro erro
    #
    # No final:
    # return erros
    pass


def validar_produtos(produtos):
    # OBJETIVO:
    # percorrer os produtos usando "for"
    # e verificar quantidade, descrição e valores.
    pass


def validar_valores(venda):
    # OBJETIVO:
    # calcular:
    # quantidade * valor_unitario
    #
    # depois comparar com o valor total da venda.
    pass


def validar_venda(venda):
    # Esta função será uma função "organizadora".
    #
    # Ela chamará:
    # validar_cliente()
    # validar_produtos()
    # validar_valores()
    #
    # e juntará todos os erros encontrados.
    pass
