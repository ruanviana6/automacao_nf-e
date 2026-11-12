"""Impede qualquer conexão de rede durante a regressão Python da automação."""

import socket

import pytest


@pytest.fixture(autouse=True)
def sem_rede(monkeypatch):
    """Um teste que esquecer de simular transporte deve falhar, nunca atingir ERP."""
    def negar(*_args, **_kwargs):
        raise AssertionError('Conexão externa proibida na suíte fictícia.')
    monkeypatch.setattr(socket.socket, 'connect', negar)
    monkeypatch.setattr(socket.socket, 'connect_ex', negar)
