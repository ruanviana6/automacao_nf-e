"""Referência simulada; a execução operacional única fica no Supabase."""

from api.duas_contas import IntegracaoFiscalPendente
from database.nfe_repository import atualizar_nota, registrar_nota, buscar_legado_sem_escopo
from database.referencia_repository import atualizar, reservar
from services.regras_fiscais import validar_escolhas_manuais
from services.validacao import validar_venda
from services.vendas import pedido_liberado_gerar_nfe


def preparar_dados_nf(venda, opcoes_fiscais_manuais=None):
    """Valida dados de referência e exige escolhas explícitas, sem mapear HTTP."""
    erros = validar_venda(venda)
    if erros:
        raise ValueError(' | '.join(erros))
    escolhas = validar_escolhas_manuais(opcoes_fiscais_manuais)
    return {'numero_pedido': venda['numero_pedido'], 'cliente': venda['cliente'],
            'produtos': venda['produtos'], 'valor_total': venda['valor_total'],
            'opcoes_fiscais_manuais': escolhas.para_registro_interno()}


def processar_nota(venda, provedor, usuario_gerador='REFERENCIA_DEMO', *, opcoes_fiscais_manuais=None,
                   autorizacao_em_andamento=False, organizacao='ORGANIZACAO_DEMO',
                   origem='DEMO-ATACADO', destino='DEMO-VAREJO'):
    """Executa só dublês de teste; nunca baixa arquivos ou usa credencial real.

    O diário é reservado antes da criação. Timeout, rejeição e estado desconhecido
    mantêm a identidade ocupada. Não constitui uma segunda base de produção.
    """
    if getattr(provedor, 'ambiente', None) != 'simulacao':
        raise IntegracaoFiscalPendente('A execução operacional é exclusiva do executor Supabase, ainda em DEMO.')
    dados = preparar_dados_nf(venda, opcoes_fiscais_manuais)
    if type(autorizacao_em_andamento) is not bool or not pedido_liberado_gerar_nfe(venda, autorizacao_em_andamento):
        raise ValueError('Pedido não elegível ou sem autorização explícita de referência.')
    identidade = (organizacao, origem, str(venda.get('id') or venda['numero_pedido']), destino, 'simulacao')
    if any(not isinstance(v, str) or not 0 < len(v) <= 120 for v in identidade):
        raise ValueError('Identidade do pedido inválida.')
    legado = buscar_legado_sem_escopo(venda['numero_pedido'], 'simulacao')
    if legado is not None:
        return {'status': 'pendente_consulta', 'numero_pedido': venda['numero_pedido'],
                'nota_id': legado['id'], 'id_externo': legado['id_externo']}
    registro, novo = reservar(identidade, dados['opcoes_fiscais_manuais'])
    if not novo:
        return {'status': 'duplicada' if registro['estado'] in ('simulada', 'Aprovada', 'aprovada') else 'pendente_consulta',
                'numero_pedido': venda['numero_pedido'], 'solicitacao_id': registro['id'],
                'id_externo': registro['id_externo']}
    try:
        criada = provedor.criar_nota(dados)
        id_externo = criada['id_externo']
        if not isinstance(id_externo, str) or not 0 < len(id_externo) <= 120:
            raise ValueError('Identificador externo inválido.')
        atualizar(registro['id'], 'created', id_externo)
        nota_id = registrar_nota({'numero_pedido': venda['numero_pedido'], 'id_externo': id_externo,
            'numero_nfe': criada.get('numero_nfe'), 'chave_nfe': criada.get('chave_nfe'),
            'status_nfe': criada.get('status_nfe', 'criada'), 'usuario_gerador': usuario_gerador,
            'data_emissao': criada.get('data_emissao'), 'origem': getattr(provedor, 'origem', 'referencia_demo'),
            'ambiente': 'simulacao', 'solicitacao_referencia': registro['id']})
        emissao = provedor.emitir_nota(id_externo)
        atualizar_nota(nota_id, emissao)
        atualizar(registro['id'], emissao['status_nfe'], id_externo)
    except Exception:
        # Mesmo erro de resposta ou persistência após a chamada é incerto.
        atualizar(registro['id'], 'needs_reconciliation')
        raise
    return {'status': emissao['status_nfe'], 'nota_id': nota_id, 'solicitacao_id': registro['id'],
            'numero_pedido': venda['numero_pedido'], 'numero_nfe': emissao.get('numero_nfe'),
            'chave_nfe': emissao.get('chave_nfe'), 'caminho_xml': None, 'caminho_pdf': None}
