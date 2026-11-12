"""Rotas seguras da automação com duas contas, sem acesso real à rede."""
import pytest

from api.duas_contas import (
    CredenciaisConta,
    EmissorVarejo,
    IntegracaoFiscalPendente,
    LeitorAtacado,
    ProvedorDuasContas,
)


def credenciais(tipo="ATACADO", host="https://api.gestaoclick.com.br/api"):
    return CredenciaisConta(tipo, host, "token-ficticio", "segredo-ficticio")


@pytest.mark.parametrize("url", [
    "http://api.gestaoclick.com.br/api",
    "https://gestaoclick.com.br.evil.example/api",
    "https://127.0.0.1/api",
    "https://user:pass@api.gestaoclick.com.br/api",
    "https://api.gestaoclick.com.br/api?token=secret",
])
def test_configuracao_recusa_destinos_inseguros(url):
    with pytest.raises(ValueError):
        credenciais(host=url).validar()


def test_segredos_nao_aparecem_na_representacao():
    conf = credenciais()
    assert "token-ficticio" not in repr(conf)
    assert "segredo-ficticio" not in repr(conf)


def test_atacado_so_fornece_consulta_e_nao_implementa_fiscal():
    leitor = LeitorAtacado(credenciais())
    assert not hasattr(leitor, "criar_nota")
    assert not hasattr(leitor, "emitir_nota")
    with pytest.raises(IntegracaoFiscalPendente):
        leitor.buscar_pedidos_pendentes()


def test_legado_nao_pode_emitir_mesmo_com_flag_antiga(monkeypatch):
    """A autorização nova proíbe emissão, inclusive nos caminhos antigos."""
    import api.duas_contas as mod
    monkeypatch.setattr(mod.settings, 'NFE_EMISSAO_REAL_HABILITADA', True)
    emissor = EmissorVarejo(credenciais('VAREJO'))
    with pytest.raises(IntegracaoFiscalPendente):
        emissor.emitir_nota('NF-123')
    with pytest.raises(IntegracaoFiscalPendente):
        emissor.criar_nota({'numero_pedido':123})
    with pytest.raises(IntegracaoFiscalPendente):
        ProvedorDuasContas(leitor=object(), emissor=object())


def test_provedor_modo_simulacao_preserva_contrato(monkeypatch):
    import api.provider as provider
    from api.mock_gestaoclick import MockGestaoClickAPI

    monkeypatch.setattr(provider, "MODO_SIMULACAO", True)
    assert isinstance(provider.obter_provedor(), MockGestaoClickAPI)


def test_provedor_real_nao_deixa_reutilizar_chaves_legadas(monkeypatch):
    import api.provider as provider
    from config import settings

    monkeypatch.setattr(provider, "MODO_SIMULACAO", False)
    monkeypatch.setattr(settings, "GESTAOCLICK_API_BASE_URL", "")
    monkeypatch.setattr(settings, "GESTAOCLICK_API_ACCESS_TOKEN", "")
    monkeypatch.setattr(settings, "GESTAOCLICK_API_SECRET_ACCESS", "")
    # Não aceita fallback para as credenciais genéricas legadas.
    with pytest.raises(ValueError):
        provider.obter_provedor()
