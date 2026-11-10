"""Geração do relatório das notas processadas."""

import csv

from config.settings import PASTA_RELATORIOS
from utils.data_hora import agora_utc


def gerar_relatorio(notas):
    PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)

    nome_arquivo = agora_utc().strftime("relatorio_nfe_%Y%m%d_%H%M%S.csv")
    caminho_relatorio = PASTA_RELATORIOS / nome_arquivo

    campos = [
        "id",
        "numero_pedido",
        "numero_nfe",
        "chave_nfe",
        "status_nfe",
        "usuario_gerador",
        "data_emissao",
        "criado_em"
    ]

    with caminho_relatorio.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos,
            delimiter=";"
        )
        escritor.writeheader()

        for nota in notas:
            escritor.writerow({
                campo: nota[campo]
                for campo in campos
            })

    return caminho_relatorio
