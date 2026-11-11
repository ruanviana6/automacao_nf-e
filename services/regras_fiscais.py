"""Regras manuais da NF-e modelo 55: seleção humana antes de criar/emitir.

Representação interna independente dos nomes dos campos da API GestãoClick.
Mapeamento para a requisição só poderá ser implementado após validar o OpenAPI
real da conta e as regras fiscais aplicáveis. Nenhuma função envia HTTP.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


MODALIDADES_FRETE = {
    0: "CIF - contratação por conta do remetente",
    1: "FOB - contratação por conta do destinatário",
    2: "Contratação por conta de terceiros",
    3: "Transporte próprio por conta do remetente",
    4: "Transporte próprio por conta do destinatário",
    9: "Sem ocorrência de transporte",
}

TIPOS_CONTRIBUINTE = {
    1: "Contribuinte do ICMS",
    2: "Contribuinte isento de inscrição estadual",
    9: "Não contribuinte do ICMS",
}


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
