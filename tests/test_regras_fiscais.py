"""Regressões para os campos fiscais que o operador escolhe no Gerente."""
import pytest

from services.regras_fiscais import (
    EscolhasFiscaisManuais, MODALIDADES_FRETE, TIPOS_CONTRIBUINTE,
    validar_escolhas_manuais,
)
from services.notas import preparar_dados_nf


def test_codigo_fob_e_contribuinte_nao_sao_inferidos():
    opcoes = validar_escolhas_manuais({"modalidade_frete": 1, "tipo_contribuinte": 9})
    assert opcoes == EscolhasFiscaisManuais(1, 9)
    assert opcoes.para_registro_interno() == {"modalidade_frete": 1, "tipo_contribuinte": 9}


def test_isento_e_nao_contribuinte_sao_distintos():
    assert validar_escolhas_manuais({"modalidade_frete": 1, "tipo_contribuinte": 2}).tipo_contribuinte == 2
    assert validar_escolhas_manuais({"modalidade_frete": 1, "tipo_contribuinte": 9}).tipo_contribuinte == 9
    assert MODALIDADES_FRETE[1].startswith("FOB")
    assert TIPOS_CONTRIBUINTE[2] != TIPOS_CONTRIBUINTE[9]


@pytest.mark.parametrize("opcoes", [
    None, {}, {"modalidade_frete": 1}, {"tipo_contribuinte": 2},
    {"modalidade_frete": "1", "tipo_contribuinte": 9},
    {"modalidade_frete": True, "tipo_contribuinte": 9},
    {"modalidade_frete": 5, "tipo_contribuinte": 9},
    {"modalidade_frete": 1, "tipo_contribuinte": "isento"},
    {"modalidade_frete": 1, "tipo_contribuinte": 0},
    {"modalidade_frete": 1, "tipo_contribuinte": False},
])
def test_bloqueia_ausentes_ambiguos_e_invalidos(opcoes):
    with pytest.raises(ValueError):
        validar_escolhas_manuais(opcoes)


def test_permite_todos_codigos_previstos_no_layout_sem_default():
    for frete in (0, 1, 2, 3, 4, 9):
        for contribuinte in (1, 2, 9):
            opcoes = validar_escolhas_manuais({
                "modalidade_frete": frete, "tipo_contribuinte": contribuinte
            })
            assert opcoes.modalidade_frete == frete
            assert opcoes.tipo_contribuinte == contribuinte


def test_preparo_da_nota_transporta_opcoes_internas_para_provedor():
    venda = {
        "numero_pedido": 4589,
        "cliente": {"nome": "Cliente Teste", "documento": "12345678901", "uf": "CE"},
        "produtos": [{"descricao": "Produto Teste", "quantidade": 1, "valor_unitario": 10.0}],
        "valor_total": 10.0
    }
    dados = preparar_dados_nf(venda, {"modalidade_frete": 1, "tipo_contribuinte": 2})
    assert dados["opcoes_fiscais_manuais"] == {
        "modalidade_frete": 1, "tipo_contribuinte": 2
    }
    with pytest.raises(ValueError):
        preparar_dados_nf(venda)  # DEMO também exige escolhas manuais explícitas.
