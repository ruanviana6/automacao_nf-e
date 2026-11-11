import pytest

from api.gestaoclick import GestaoClickAPI


def test_api_exige_https():
    api = GestaoClickAPI(
        base_url="http://api.exemplo.local",
        access_token="access",
        secret_access="secret"
    )

    with pytest.raises(ValueError, match="HTTPS"):
        api._validar_configuracao()


def test_api_rejeita_url_com_credenciais():
    api = GestaoClickAPI(
        base_url="https://usuario:senha@api.exemplo.local",
        access_token="access",
        secret_access="secret"
    )

    with pytest.raises(
        ValueError,
        match="não pode conter credenciais"
    ):
        api._validar_configuracao()


def test_api_bloqueia_redirect_e_usa_timeout(monkeypatch):
    api = GestaoClickAPI(
        base_url="https://api.exemplo.local",
        access_token="access",
        secret_access="secret"
    )

    capturado = {}

    class Resposta:
        status_code = 302
        content = b""

        def raise_for_status(self):
            return None

    def request_fake(
        metodo,
        url,
        timeout,
        allow_redirects,
        **kwargs
    ):
        capturado["timeout"] = timeout
        capturado["allow_redirects"] = allow_redirects
        return Resposta()

    monkeypatch.setattr(
        api.session,
        "request",
        request_fake
    )

    with pytest.raises(
        RuntimeError,
        match="Cliente legado"
    ):
        api.visualizar("/teste")

    assert capturado == {}  # O cliente legado não pode abrir nenhuma requisição.
