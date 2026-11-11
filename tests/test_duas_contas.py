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


def test_varejo_rejeita_criacao_e_emissao_reais_sem_contrato(monkeypatch):
    import api.duas_contas as mod

    emissor = EmissorVarejo(credenciais("VAREJO"))
    monkeypatch.setattr(mod.settings, "NFE_EMISSAO_REAL_HABILITADA", False)
    with pytest.raises(IntegracaoFiscalPendente, match="desabilitada"):
        emissor.criar_nota({"numero_pedido": 123})
    with pytest.raises(IntegracaoFiscalPendente, match="desabilitada"):
        emissor.emitir_nota("NF-123")

    # Mesmo ativando a flag isoladamente, sem mapeamento OpenAPI nenhuma
    # requisição fiscal pode ser enviada por este adaptador.
    monkeypatch.setattr(mod.settings, "NFE_EMISSAO_REAL_HABILITADA", True)
    with pytest.raises(IntegracaoFiscalPendente, match="contrato"):
        emissor.criar_nota({"numero_pedido": 123})
    with pytest.raises(IntegracaoFiscalPendente, match="endpoint"):
        emissor.emitir_nota("NF-123")


def test_provedor_usa_atacado_para_pedidos_e_varejo_para_nfe():
    chamadas = []

    class Atacado:
        def buscar_pedidos_pendentes(self):
            chamadas.append(("atacado", "buscar"))
            return [{"numero_pedido": 123}]

    class Varejo:
        def criar_nota(self, dados):
            chamadas.append(("varejo", "criar", dados["numero_pedido"]))
            return {"id_externo": "N-1"}

        def emitir_nota(self, id_externo):
            chamadas.append(("varejo", "emitir", id_externo))
            return {"status_nfe": "simulada"}

        def consultar_nota(self, id_externo):
            chamadas.append(("varejo", "consultar", id_externo))
            return {}

        def baixar_xml(self, id_externo):
            chamadas.append(("varejo", "xml", id_externo))
            return b"XML"

        def baixar_pdf(self, id_externo):
            chamadas.append(("varejo", "pdf", id_externo))
            return b"PDF"

    provedor = ProvedorDuasContas(leitor=Atacado(), emissor=Varejo())
    assert provedor.buscar_pedidos_pendentes()[0]["numero_pedido"] == 123
    assert provedor.criar_nota({"numero_pedido": 123})["id_externo"] == "N-1"
    assert provedor.emitir_nota("N-1")["status_nfe"] == "simulada"
    provedor.consultar_nota("N-1")
    provedor.baixar_xml("N-1")
    provedor.baixar_pdf("N-1")
    assert chamadas == [
        ("atacado", "buscar"), ("varejo", "criar", 123),
        ("varejo", "emitir", "N-1"), ("varejo", "consultar", "N-1"),
        ("varejo", "xml", "N-1"), ("varejo", "pdf", "N-1"),
    ]


def test_provedor_modo_simulacao_preserva_contrato(monkeypatch):
    import api.provider as provider
    from api.mock_gestaoclick import MockGestaoClickAPI

    monkeypatch.setattr(provider, "MODO_SIMULACAO", True)
    assert isinstance(provider.obter_provedor(), MockGestaoClickAPI)


def test_provedor_real_nao_deixa_reutilizar_chaves_legadas(monkeypatch):
    import api.provider as provider
    from config import settings

    monkeypatch.setattr(provider, "MODO_SIMULACAO", False)
    monkeypatch.setattr(settings, "GESTAOCLICK_ATACADO_BASE_URL", "")
    monkeypatch.setattr(settings, "GESTAOCLICK_ATACADO_ACCESS_TOKEN", "")
    monkeypatch.setattr(settings, "GESTAOCLICK_ATACADO_SECRET_ACCESS", "")
    # Não aceita fallback para as credenciais genéricas legadas.
    with pytest.raises(ValueError):
        provider.obter_provedor()
