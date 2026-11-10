"""Base da integração com a API do GestãoClick.

Os endpoints específicos serão conectados usando o arquivo OpenAPI
disponível dentro da conta do GestãoClick.
"""

import requests

from config.settings import (
    GESTAOCLICK_BASE_URL,
    GESTAOCLICK_ACCESS_TOKEN,
    GESTAOCLICK_SECRET_ACCESS,
    GESTAOCLICK_TIMEOUT
)


class GestaoClickAPI:
    def __init__(
        self,
        base_url=None,
        access_token=None,
        secret_access=None
    ):
        self.base_url = (base_url or GESTAOCLICK_BASE_URL).rstrip("/")
        self.access_token = access_token or GESTAOCLICK_ACCESS_TOKEN
        self.secret_access = secret_access or GESTAOCLICK_SECRET_ACCESS
        self.timeout = GESTAOCLICK_TIMEOUT

        self.session = requests.Session()
        self.session.headers.update({
            "access-token": self.access_token,
            "secret-access-token": self.secret_access,
            "Accept": "application/json"
        })

    def _validar_configuracao(self):
        if not self.base_url:
            raise ValueError("GESTAOCLICK_BASE_URL não configurada.")

        if not self.access_token or not self.secret_access:
            raise ValueError("Credenciais da API do GestãoClick não configuradas.")

    def _request(self, metodo, endpoint, **kwargs):
        self._validar_configuracao()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        resposta = self.session.request(
            metodo,
            url,
            timeout=self.timeout,
            **kwargs
        )

        if resposta.status_code == 429:
            raise RuntimeError("Limite de requisições da API atingido.")

        resposta.raise_for_status()

        if not resposta.content:
            return None

        return resposta.json()

    def listar(self, endpoint, params=None):
        return self._request(
            "GET",
            endpoint,
            params=params
        )

    def visualizar(self, endpoint):
        return self._request(
            "GET",
            endpoint
        )

    def cadastrar(self, endpoint, dados):
        return self._request(
            "POST",
            endpoint,
            json=dados
        )

    def executar_acao(self, endpoint, dados=None):
        return self._request(
            "POST",
            endpoint,
            json=dados or {}
        )
