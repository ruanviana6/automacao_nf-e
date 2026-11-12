"""Regressões de resultados incertos e isolamento da referência simulada."""

import copy
from concurrent.futures import ThreadPoolExecutor

import pytest

import database.conexao as conexao
from api.gestaoclick import GestaoClickAPI
from api.mock_gestaoclick import MockGestaoClickAPI
from database.nfe_repository import buscar_nota_ativa_para_pedido, inicializar_banco, registrar_nota
from database.referencia_repository import reservar
from services.notas import processar_nota
from services.validacao import validar_venda

ESCOLHAS = {'modalidade_frete': 1, 'tipo_contribuinte': 9}


@pytest.fixture
def referencia(tmp_path, monkeypatch):
    """Isola o SQLite fictício; não utiliza dados ou arquivos fiscais históricos."""
    monkeypatch.setattr(conexao, 'CAMINHO_BANCO', tmp_path / 'referencia.db')
    inicializar_banco()
    provedor = MockGestaoClickAPI()
    pedido = copy.deepcopy(provedor.buscar_pedidos_pendentes()[0])
    return provedor, pedido


def test_timeout_na_criacao_nao_repete_tentativa(referencia):
    """O caso antes não coberto precisa conservar o diário sem receber ID externo."""
    provedor, pedido = referencia
    tentativas = []

    def criar(_dados):
        """Simula a criação remota concluída cuja resposta foi perdida."""
        tentativas.append('criacao')
        raise TimeoutError('Resultado simulado desconhecido')

    provedor.criar_nota = criar
    with pytest.raises(TimeoutError):
        processar_nota(pedido, provedor, opcoes_fiscais_manuais=ESCOLHAS)
    repeticao = processar_nota(pedido, provedor, opcoes_fiscais_manuais=ESCOLHAS)
    assert repeticao['status'] == 'pendente_consulta'
    assert tentativas == ['criacao']


def test_dois_funcionarios_nao_criam_duas_notas(referencia):
    """A reserva única impede a corrida SELECT seguida de criação."""
    provedor, pedido = referencia
    tentativas = []
    original = provedor.criar_nota

    def criar(dados):
        """Conta as chamadas simuladas, sem arquivos ou operações HTTP."""
        tentativas.append(1)
        return original(dados)

    provedor.criar_nota = criar
    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(lambda _: processar_nota(pedido, provedor, opcoes_fiscais_manuais=ESCOLHAS), range(2)))
    assert len(tentativas) == 1
    assert sum(r['status'] == 'simulada' for r in resultados) == 1


@pytest.mark.parametrize('estado', ['Em aberto', 'Aprovada', 'Reprovada', 'Denegada', 'Cancelada', 'Enviando', 'Corrigida', 'desconhecido'])
def test_todo_estado_existente_exige_conferencia(referencia, estado):
    """Uma rejeição ou estado não mapeado não equivale a ausência de nota."""
    provedor, pedido = referencia
    registrar_nota({'numero_pedido': pedido['numero_pedido'], 'id_externo': 'DEMO-EXISTENTE', 'status_nfe': estado,
                    'usuario_gerador': 'TESTE', 'ambiente': 'simulacao'})
    assert buscar_nota_ativa_para_pedido(pedido['numero_pedido'], 'simulacao') is not None
    assert processar_nota(pedido, provedor, opcoes_fiscais_manuais=ESCOLHAS)['status'] == 'pendente_consulta'


def test_reserva_separa_organizacao_contas_e_pedido(referencia):
    """Números iguais de pedidos não são uma identidade global."""
    a, novo_a = reservar(('org-a', 'atacado-a', 'pedido-1', 'varejo-a', 'simulacao'), ESCOLHAS)
    b, novo_b = reservar(('org-b', 'atacado-b', 'pedido-1', 'varejo-b', 'simulacao'), ESCOLHAS)
    assert novo_a and novo_b and a['id'] != b['id']


def test_sem_download_de_documentos(referencia):
    """Mesmo uma autorização simulada não pode baixar XML ou PDF."""
    provedor, pedido = referencia

    def proibido(*_args):
        """Falha se o fluxo operacional tentar baixar um documento."""
        pytest.fail('Download não permitido')

    provedor.baixar_xml = proibido
    provedor.baixar_pdf = proibido
    resultado = processar_nota(pedido, provedor, opcoes_fiscais_manuais=ESCOLHAS)
    assert resultado['caminho_xml'] is resultado['caminho_pdf'] is None


@pytest.mark.parametrize('valor', [True, float('inf'), float('-inf'), float('nan'), 10**1000])
def test_valores_nao_finitos_e_booleanos_sao_bloqueados(referencia, valor):
    """Valores aceitos pelo tipo float não são automaticamente números fiscais válidos."""
    _provedor, pedido = referencia
    pedido['valor_total'] = valor
    assert validar_venda(pedido)


@pytest.mark.parametrize('metodo', ['cadastrar', 'executar_acao'])
def test_cliente_legado_nao_expoe_escrita_arbitraria(metodo):
    """Flags ou rotas fornecidas pelo chamador não reativam o cliente genérico."""
    api = GestaoClickAPI(base_url='https://api.gestaoclick.com', access_token='DEMO', secret_access='DEMO')
    with pytest.raises(RuntimeError, match='Cliente legado'):
        getattr(api, metodo)('clientes', {})
