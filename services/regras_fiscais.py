"""Regras manuais da NF-e modelo 55: seleção humana antes de criar/emitir.

Representação interna independente dos nomes dos campos da API GestãoClick.
Mapeamento para a requisição só poderá ser implementado após validar o OpenAPI
real da conta e as regras fiscais aplicáveis. Nenhuma função envia HTTP.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Mapping


CONTRATO = json.loads((Path(__file__).resolve().parents[1] / 'contratos/fiscal_demo_v1.json').read_text())
MODALIDADES_FRETE = {int(k): v for k, v in CONTRATO['modalidades_frete'].items()}
TIPOS_CONTRIBUINTE = {int(k): v for k, v in CONTRATO['tipos_contribuinte'].items()}


@dataclass(frozen=True)
class EscolhasFiscaisManuais:
    """Confirmação imutável das duas escolhas para uma solicitação fiscal."""

    modalidade_frete: int
    tipo_contribuinte: int

    def __post_init__(self):
        if type(self.modalidade_frete) is not int or self.modalidade_frete not in MODALIDADES_FRETE:
            raise ValueError("Selecione uma modalidade válida de transporte/frete.")
        if type(self.tipo_contribuinte) is not int or self.tipo_contribuinte not in TIPOS_CONTRIBUINTE:
            raise ValueError("Selecione o tipo de contribuinte confirmado do cliente.")

    def para_registro_interno(self) -> dict[str, int]:
        """Preserva as escolhas, sem alegar que sejam os nomes da API."""
        return {
            "modalidade_frete": self.modalidade_frete,
            "tipo_contribuinte": self.tipo_contribuinte,
        }


def validar_escolhas_manuais(dados: Mapping | None) -> EscolhasFiscaisManuais:
    """Exige ambas as escolhas explícitas, sem defaults nem inferência pelo cadastro.

    Os códigos seguem os valores fiscais usuais modFrete/indIEDest, mas não
    substituem conferência da situação do cliente, IE, transportador ou
    documentação real do endpoint do ERP.
    """
    if not isinstance(dados, Mapping):
        raise ValueError(
            "Antes da NF-e, informe manualmente a modalidade do frete "
            "e o tipo de contribuinte do cliente."
        )
    if "modalidade_frete" not in dados or "tipo_contribuinte" not in dados:
        raise ValueError("As duas seleções fiscais são obrigatórias para cada nota.")
    return EscolhasFiscaisManuais(
        modalidade_frete=dados["modalidade_frete"],
        tipo_contribuinte=dados["tipo_contribuinte"],
    )
