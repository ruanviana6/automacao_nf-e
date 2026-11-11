"""Base segura da integração com a API real do GestãoClick."""

from urllib.parse import urlparse

import requests

from config.settings import (
    GESTAOCLICK_ACCESS_TOKEN,
    GESTAOCLICK_BASE_URL,
    GESTAOCLICK_CONNECT_TIMEOUT,
    GESTAOCLICK_READ_TIMEOUT,
    GESTAOCLICK_SECRET_ACCESS
)


class GestaoClickAPI:
    origem = "gestaoclick"
    ambiente = "producao"

    def __init__(
        self,
        base_url=None,
        access_token=None,
        secret_access=None
    ):
        self.base_url = (base_url or GESTAOCLICK_BASE_URL).rstrip("/")
        self.access_token = access_token or GESTAOCLICK_ACCESS_TOKEN
        self.secret_access = secret_access or GESTAOCLICK_SECRET_ACCESS
        self.timeout = (
            GESTAOCLICK_CONNECT_TIMEOUT,
            GESTAOCLICK_READ_TIMEOUT
        )

        self.session = requests.Session()
        self.session.headers.update({
            "access-token": self.access_token,
            "secret-access-token": self.secret_access,
            "Accept": "application/json",
            "User-Agent": "automacao-nfe/1.0"
        })

    def _validar_configuracao(self):
        if not self.base_url:
            raise ValueError("GESTAOCLICK_BASE_URL não configurada.")

        url = urlparse(self.base_url)

        if url.scheme != "https":
            raise ValueError(
                "A API do GestãoClick deve usar HTTPS."
            )

        if not url.hostname:
            raise ValueError(
                "GESTAOCLICK_BASE_URL inválida."
            )

        if url.username or url.password:
            raise ValueError(
                "GESTAOCLICK_BASE_URL não pode conter credenciais."
            )

        if not self.access_token or not self.secret_access:
            raise ValueError(
                "Credenciais da API do GestãoClick não configuradas."
            )

    def _request(self, metodo, endpoint, **kwargs):
        """Descontinua o cliente genérico: nenhuma rota HTTP real é liberada."""
        raise RuntimeError('Cliente legado desativado. Use os contratos Atacado/Varejo e o executor fiscal isolado.')

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
        # POST não recebe retry automático para reduzir risco de duplicidade.
        return self._request(
            "POST",
            endpoint,
            json=dados
        )

    def executar_acao(self, endpoint, dados=None):
        # A emissão também não é repetida automaticamente em erro/timeout.
        return self._request(
            "POST",
            endpoint,
            json=dados or {}
        )

    def buscar_pedidos_pendentes(self):
        raise NotImplementedError(
            "Integração de pedidos aguardando os endpoints do OpenAPI do GestãoClick."
        )

    def criar_nota(self, dados):
        raise NotImplementedError(
            "Criação da NF-e aguardando o endpoint oficial do OpenAPI."
        )

    def emitir_nota(self, id_externo):
        raise NotImplementedError(
            "Emissão da NF-e aguardando o endpoint oficial do OpenAPI."
        )

    def consultar_nota(self, id_externo):
        raise NotImplementedError(
            "Consulta da NF-e aguardando o endpoint oficial do OpenAPI."
        )

    def baixar_xml(self, id_externo):
        raise NotImplementedError(
            "Download do XML aguardando o endpoint oficial do OpenAPI."
        )

    def baixar_pdf(self, id_externo):
        raise NotImplementedError(
            "Download do PDF aguardando o endpoint oficial do OpenAPI."
        )
