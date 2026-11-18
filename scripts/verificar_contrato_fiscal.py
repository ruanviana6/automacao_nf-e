"""Inspeciona um OpenAPI local, sem rede, tokens ou escrita no GestãoClick.

A identificação de rotas é somente exploratória e não substitui homologação.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

MAX_BYTES = 10 * 1024 * 1024
MAX_PATHS = 5000
VERBOS = frozenset({'get', 'post'})


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return texto.lower().replace('-', '_')


def _tipo_descricao(caminho: str, operacao: dict[str, Any]) -> str | None:
    # Descrições não são exibidas: podem conter dados da conta ou credenciais.
    campos = [caminho, operacao.get('summary', ''), operacao.get('operationId', '')]
    tags = operacao.get('tags', [])
    if isinstance(tags, list):
        campos.extend(t for t in tags if isinstance(t, str))
    texto = _normalizar(' '.join(c for c in campos if isinstance(c, str)))
    if any(c in texto for c in ('notas_fiscais_consumidores', 'nfce', 'nfc_e',
                               'notas_fiscais_servicos', 'nfse', 'nfs_e')):
        return None
    if any(c in texto for c in ('notas_fiscais', 'notafiscal', 'nota_fiscal', 'nf_e', 'nfe')):
        return 'nf_e'
    if any(c in texto for c in ('lojas', 'loja')):
        return 'lojas'
    if any(c in texto for c in ('vendas', 'pedidos')):
        return 'pedidos_vendas'
    return None


def _rota_sem_acao(caminho: str, operacao: dict[str, Any]) -> bool:
    texto = _normalizar(' '.join(str(v) for v in (
        caminho, operacao.get('summary', ''), operacao.get('operationId', ''))))
    if re.search(r'(emitir|emissao|cancelar|cancelamento|excluir|delete|inutilizar|enviar|autorizar|correcao|atualizar|editar)', texto):
        return False
    # POST candidato a cadastro deve ser em coleção, nunca em /{id}/acao.
    return not re.search(r'/\{[^{}]+\}(?:/|$)', caminho)


def analisar_contrato(documento: Any) -> dict[str, Any]:
    """Retorna apenas metadados mínimos; nunca autoriza ativação."""
    if not isinstance(documento, dict) or not re.fullmatch(
        r'3\.[0-9]+(?:\.[0-9]+)?', str(documento.get('openapi', ''))
    ):
        raise ValueError('É necessário um documento OpenAPI 3 válido.')
    caminhos = documento.get('paths')
    if not isinstance(caminhos, dict) or len(caminhos) > MAX_PATHS:
        raise ValueError('Tabela de rotas OpenAPI inválida ou excessiva.')
    achados: dict[str, list[dict[str, str]]] = {
        'nf_e_consultas': [], 'nf_e_cadastro_candidato': [],
        'lojas_consultas': [], 'pedidos_vendas_consultas': [],
    }
    for caminho, item in caminhos.items():
        if not isinstance(caminho, str) or not caminho.startswith('/') or len(caminho) > 200 or '?' in caminho or any(ord(c) < 32 for c in caminho):
            raise ValueError('Documento contém rota malformada. Análise interrompida.')
        if not isinstance(item, dict):
            continue
        for verbo in VERBOS:
            operacao = item.get(verbo)
            if not isinstance(operacao, dict):
                continue
            tipo = _tipo_descricao(caminho, operacao)
            if tipo == 'nf_e':
                if verbo == 'get':
                    achados['nf_e_consultas'].append({'metodo': 'GET', 'rota_candidata': caminho})
                elif verbo == 'post' and _rota_sem_acao(caminho, operacao):
                    achados['nf_e_cadastro_candidato'].append({'metodo': 'POST', 'rota_candidata': caminho})
            elif tipo == 'lojas' and verbo == 'get':
                achados['lojas_consultas'].append({'metodo': 'GET', 'rota_candidata': caminho})
            elif tipo == 'pedidos_vendas' and verbo == 'get':
                achados['pedidos_vendas_consultas'].append({'metodo': 'GET', 'rota_candidata': caminho})
    for itens in achados.values():
        itens.sort(key=lambda x: (x['rota_candidata'], x['metodo']))
    return {
        'status': 'BLOQUEADO',
        'tipo': 'preflight_estatico_nao_homologado',
        'resumo': {nome: len(itens) for nome, itens in achados.items()},
        'candidatos': achados,
        'avisos': [
            'Nenhuma requisição foi executada. Rotas candidatas não provam disponibilidade na conta.',
            'OpenAPI não comprova IDs de lojas, permissões, identidade estável, idempotência ou dados fiscais.',
            'Confirmar que cadastrar NF-e cria só rascunho e não gera pedido, baixa, emissão ou envio automático.',
            'Não ativar POST real, emitir ou cancelar sem autorização e homologação fiscal.',
            'Exigir validação fiscal de CFOP, NCM, CST/CSOSN, impostos, frete e contribuinte.',
        ],
    }


def ler_openapi(caminho: Path) -> dict[str, Any]:
    if caminho.suffix.lower() != '.json':
        raise ValueError('Exporte o OpenAPI como JSON. YAML não é analisado por esta ferramenta.')
    if not caminho.is_file() or caminho.stat().st_size > MAX_BYTES:
        raise ValueError('Arquivo OpenAPI inexistente ou maior que 10 MiB.')
    with caminho.open('r', encoding='utf-8') as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arquivo', type=Path, help='Arquivo OpenAPI 3 JSON local, sem credenciais.')
    args = parser.parse_args(argv)
    try:
        resultado = analisar_contrato(ler_openapi(args.arquivo))
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError):
        # Não ecoar mensagem de erro: parser pode incluir material do arquivo.
        print('Falha na leitura/validação do contrato local. Verifique JSON e OpenAPI 3.', file=sys.stderr)
        return 2
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
