"""Regras relacionadas às notas fiscais.

Este arquivo prepara e coordena dados internos.
O formato oficial enviado ao GestãoClick será ajustado com o OpenAPI da conta.
"""

from services.validacao import validar_venda


def preparar_dados_nf(venda):
    erros = validar_venda(venda)

    if erros:
        raise ValueError(" | ".join(erros))

    # Estrutura interna do projeto.
    # Ainda não representa o payload oficial do GestãoClick.
    return {
        "numero_pedido": venda["numero_pedido"],
        "cliente": venda["cliente"],
        "produtos": venda["produtos"],
        "valor_total": venda["valor_total"]
    }


def processar_nota(venda):
    dados = preparar_dados_nf(venda)

    # A emissão real será ligada aqui quando os endpoints e campos
    # do OpenAPI da conta forem adicionados.
    return {
        "status": "pronta_para_integracao",
        "dados": dados
    }
