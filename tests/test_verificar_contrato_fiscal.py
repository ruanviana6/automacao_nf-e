"""Regressões da inspeção OpenAPI offline, sem rede nem credenciais."""
import json

import pytest

from scripts.verificar_contrato_fiscal import analisar_contrato, ler_openapi


def exemplo():
    return {
        'openapi': '3.0.3',
        'servers': [{'url': 'https://segredo.invalid/nao-exibir'}],
        'paths': {
            '/api/lojas': {'get': {'summary': 'Listar lojas'}},
            '/api/vendas': {'get': {'summary': 'Listar vendas'}},
            '/api/notas_fiscais': {
                'get': {'tags': ['Notas Fiscais']},
                'post': {'summary': 'Cadastrar NF-e', 'description': 'token-nao-exibir'},
                'delete': {'summary': 'Excluir nota'},
            },
            '/api/notas_fiscais/{id}': {'get': {'summary': 'Ver NF-e'}, 'put': {'summary': 'Editar NF-e'}},
            '/api/notas_fiscais/emitir/{id}': {'post': {'summary': 'Emitir NF-e'}},
            '/api/notas_fiscais/cancelar/{id}': {'post': {'summary': 'Cancelar NF-e'}},
            '/api/notas_fiscais_consumidores': {'post': {'summary': 'Cadastrar NFC-e'}},
            '/api/notas_fiscais_servicos': {'post': {'summary': 'Cadastrar NFS-e'}},
        },
    }


def test_encontra_cadastro_mas_nao_emissao_cancelamento_ou_outros_tipos():
    saida = analisar_contrato(exemplo())
    assert saida['status'] == 'BLOQUEADO'
    assert saida['resumo'] == {
        'nf_e_consultas': 2, 'nf_e_cadastro_candidato': 1,
        'lojas_consultas': 1, 'pedidos_vendas_consultas': 1,
    }
    assert saida['candidatos']['nf_e_cadastro_candidato'] == [
        {'metodo': 'POST', 'rota_candidata': '/api/notas_fiscais'}]
    assert 'segredo.invalid' not in json.dumps(saida)
    assert 'token-nao-exibir' not in json.dumps(saida)
    assert 'emitir' not in json.dumps(saida['candidatos'])
    assert 'cancelar' not in json.dumps(saida['candidatos'])


@pytest.mark.parametrize('documento', [
    {}, {'openapi': '2.0', 'paths': {}},
    {'openapi': '3.0.0', 'paths': []},
    {'openapi': '3.0.0', 'paths': {'rota-invalida': {}}},
])
def test_rejeita_contrato_invalido(documento):
    with pytest.raises(ValueError):
        analisar_contrato(documento)


def test_nao_inventa_contrato_caso_nao_encontre_nfe():
    saida = analisar_contrato({'openapi': '3.1.0', 'paths': {
        '/api/lojas': {'get': {'summary': 'Listar'}},
    }})
    assert saida['resumo']['nf_e_cadastro_candidato'] == 0
    assert saida['status'] == 'BLOQUEADO'


def test_cli_offline_nao_expoe_segredos(tmp_path, capsys):
    p = tmp_path / 'openapi.json'
    p.write_text(json.dumps(exemplo()), encoding='utf-8')
    from scripts.verificar_contrato_fiscal import main
    assert main([str(p)]) == 0
    exibido = capsys.readouterr().out
    assert 'segredo.invalid' not in exibido and 'token-nao-exibir' not in exibido
    assert 'BLOQUEADO' in exibido
    assert ler_openapi(p)['openapi'] == '3.0.3'


def test_cli_rejeita_yaml_e_erro_sem_exibir_conteudo(tmp_path, capsys):
    from scripts.verificar_contrato_fiscal import main
    p = tmp_path / 'dados.yaml'
    p.write_text('segredo: nao-imprima', encoding='utf-8')
    assert main([str(p)]) == 2
    assert 'nao-imprima' not in capsys.readouterr().err
