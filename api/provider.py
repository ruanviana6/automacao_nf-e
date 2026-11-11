"""Escolhe a origem dos dados sem espalhar essa decisão pelo projeto."""

from api.gestaoclick import GestaoClickAPI
from api.mock_gestaoclick import MockGestaoClickAPI
from config.settings import MODO_SIMULACAO


def obter_provedor():
    if MODO_SIMULACAO:
        return MockGestaoClickAPI()

    return GestaoClickAPI()
