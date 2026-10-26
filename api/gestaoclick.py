"""Cliente de integração com a API do GestãoClick.

Os endpoints serão implementados conforme a documentação disponível
na conta da empresa.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


class GestaoClickAPI:
    """Centraliza autenticação e requisições ao GestãoClick."""

    def __init__(self):
        self.base_url = os.getenv("GESTAOCLICK_BASE_URL")
        self.access_token = os.getenv("GESTAOCLICK_ACCESS_TOKEN")
        self.secret_access = os.getenv("GESTAOCLICK_SECRET_ACCESS")

    def testar_configuracao(self):
        """Verifica se as variáveis essenciais foram configuradas."""
        return all(
            [
                self.base_url,
                self.access_token,
                self.secret_access,
            ]
        )

    # TODO: adicionar métodos de requisição conforme a documentação real da API.
