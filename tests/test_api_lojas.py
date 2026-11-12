"""Regressões da API única e da proibição permanente de emissão automática."""

import pytest

from api.lojas import CredenciaisAPI, IntegracaoFiscalPendente, LojasFiscais, ProvedorPorLojas


def configuracao():
    """Usa IDs e credenciais fictícios, sem relação com as lojas reais."""
    return CredenciaisAPI('https://api.gestaoclick.com.br', 'token-demo', 'segredo-demo'), LojasFiscais('LOJA-DEMO-ORIGEM', 'LOJA-DEMO-DESTINO')


def test_conexao_unica_compartilhada_com_contextos_de_lojas_distintos():
    creds, lojas = configuracao()
    provider = ProvedorPorLojas(creds, lojas)
    assert provider.leitor.credenciais is provider.cadastrador.credenciais is creds
    assert provider.leitor.lojas is provider.cadastrador.lojas is lojas
    assert not hasattr(provider.leitor, 'criar_nota')
    assert not hasattr(provider.cadastrador, 'emitir_nota')
    assert not hasattr(provider.cadastrador, 'criar_venda')
    assert not hasattr(provider.cadastrador, 'criar_pedido')
    assert 'token-demo' not in repr(creds) and 'segredo-demo' not in repr(creds)


@pytest.mark.parametrize('origin,destination', [('', '2'), ('1', ''), ('1', '1'), (None, '2')])
def test_ids_de_lojas_ausentes_ou_iguais_sao_bloqueados(origin, destination):
    creds, _ = configuracao()
    with pytest.raises(ValueError):
        ProvedorPorLojas(creds, LojasFiscais(origin, destination))


@pytest.mark.parametrize('url', ['http://api.gestaoclick.com.br', 'https://gestaoclick.com.br.evil.invalid', 'https://api.gestaoclick.com.br?token=segredo'])
def test_conexao_unica_preserva_https_e_origem_oficial(url):
    with pytest.raises(ValueError):
        CredenciaisAPI(url, 'token', 'segredo').validar()


def test_emissao_sempre_proibida_e_cadastro_real_ainda_bloqueado(monkeypatch):
    from config import settings
    creds, lojas = configuracao()
    provider = ProvedorPorLojas(creds, lojas)
    for enabled in (False, True):
        monkeypatch.setattr(settings, 'NFE_CADASTRO_REAL_HABILITADO', enabled)
        monkeypatch.setattr(settings, 'NFE_EMISSAO_REAL_HABILITADA', enabled)
        with pytest.raises(IntegracaoFiscalPendente, match='manual'):
            provider.emitir_nota('DEMO-NOTA')
        with pytest.raises(IntegracaoFiscalPendente):
            provider.criar_nota({'opcoes_fiscais_manuais': {'modalidade_frete': 1, 'tipo_contribuinte': 9}})
    with pytest.raises(IntegracaoFiscalPendente):
        provider.buscar_pedidos_pendentes()


def test_fluxo_de_referencia_cadastra_sem_chamar_emissao(tmp_path, monkeypatch):
    import database.conexao as conexao
    from api.mock_gestaoclick import MockGestaoClickAPI
    from database.nfe_repository import inicializar_banco
    from services.notas import processar_nota
    monkeypatch.setattr(conexao, 'CAMINHO_BANCO', tmp_path / 'referencia.db')
    inicializar_banco()
    provider = MockGestaoClickAPI()
    def proibido(*_args, **_kwargs):
        pytest.fail('O fluxo de cadastro tentou emitir uma nota.')
    provider.emitir_nota = proibido
    result = processar_nota(provider.buscar_pedidos_pendentes()[0], provider,
                           opcoes_fiscais_manuais={'modalidade_frete': 1, 'tipo_contribuinte': 2})
    assert result['status'] == 'cadastrada_demo'
    assert result['emissao_automatica'] is False
    assert result['chave_nfe'] is None and result['numero_nfe'] is None
