"""Seleciona simulação ou fluxo Atacado (GET) + Varejo (NF-e).

A implementação real está deliberadamente BLOQUEADA até conferir o contrato
das duas APIs. Nunca usa a mesma credencial para ler Atacado e emitir no Varejo.
"""
from api.duas_contas import ProvedorDuasContas
from api.mock_gestaoclick import MockGestaoClickAPI
from config.settings import MODO_SIMULACAO


def obter_provedor():
    if MODO_SIMULACAO:
        return MockGestaoClickAPI()
    return ProvedorDuasContas()
