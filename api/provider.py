"""Seleciona DEMO ou conexão única com duas lojas; cadastro real ainda bloqueado."""
from api.lojas import ProvedorPorLojas
from api.mock_gestaoclick import MockGestaoClickAPI
from config.settings import MODO_SIMULACAO


def obter_provedor():
    if MODO_SIMULACAO:
        return MockGestaoClickAPI()
    return ProvedorPorLojas()
