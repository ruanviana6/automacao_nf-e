"""Regras relacionadas às notas fiscais.

Este arquivo NÃO fará toda a comunicação HTTP.
A comunicação com o GestãoClick ficará em api/gestaoclick.py.
"""


def preparar_dados_nf(venda):
    # OBJETIVO:
    # pegar os dados da venda e montar a estrutura
    # que futuramente será enviada para a API.
    pass


def processar_nota(venda):
    # FUTURAMENTE esta função vai coordenar:
    #
    # preparar dados
    # → emitir
    # → consultar status
    # → salvar arquivos
    pass
