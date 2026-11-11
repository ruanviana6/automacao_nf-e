"""Coordenação da emissão e armazenamento das NF-e."""

from database.nfe_repository import (
    nota_ja_emitida_para_pedido,
    registrar_arquivo_nfe,
    registrar_nota
)
from services.arquivos import salvar_pdf, salvar_xml
from services.validacao import validar_venda


def preparar_dados_nf(venda):
    erros = validar_venda(venda)

    if erros:
        raise ValueError(" | ".join(erros))

    return {
        "numero_pedido": venda["numero_pedido"],
        "cliente": venda["cliente"],
        "produtos": venda["produtos"],
        "valor_total": venda["valor_total"]
    }


def processar_nota(venda, provedor, usuario_gerador="SISTEMA"):
    numero_pedido = venda["numero_pedido"]
    ambiente = getattr(provedor, "ambiente", "producao")

    if nota_ja_emitida_para_pedido(numero_pedido, ambiente):
        return {
            "status": "duplicada",
            "numero_pedido": numero_pedido
        }

    dados = preparar_dados_nf(venda)

    criada = provedor.criar_nota(dados)
    id_externo = criada["id_externo"]

    emissao = provedor.emitir_nota(id_externo)

    nota = {
        "numero_pedido": numero_pedido,
        "id_externo": id_externo,
        "numero_nfe": emissao.get("numero_nfe"),
        "chave_nfe": emissao.get("chave_nfe"),
        "status_nfe": emissao["status_nfe"],
        "usuario_gerador": usuario_gerador,
        "data_emissao": emissao.get("data_emissao"),
        "origem": getattr(provedor, "origem", "gestaoclick"),
        "ambiente": ambiente
    }

    nota_id = registrar_nota(nota)

    resultado = {
        "status": nota["status_nfe"],
        "nota_id": nota_id,
        "numero_pedido": numero_pedido,
        "numero_nfe": nota["numero_nfe"],
        "chave_nfe": nota["chave_nfe"],
        "caminho_xml": None,
        "caminho_pdf": None
    }

    if str(nota["status_nfe"]).lower() not in ("aprovada", "simulada"):
        return resultado

    identificador_arquivo = (
        nota["chave_nfe"]
        or nota["numero_nfe"]
        or id_externo
    )
    identificador_arquivo = str(identificador_arquivo).replace("/", "_")

    xml = provedor.baixar_xml(id_externo)
    pdf = provedor.baixar_pdf(id_externo)

    caminho_xml = salvar_xml(
        xml,
        f"nfe_{identificador_arquivo}.xml"
    )
    caminho_pdf = salvar_pdf(
        pdf,
        f"nfe_{identificador_arquivo}.pdf"
    )

    registrar_arquivo_nfe(nota_id, "xml", caminho_xml)
    registrar_arquivo_nfe(nota_id, "pdf", caminho_pdf)

    resultado["caminho_xml"] = caminho_xml
    resultado["caminho_pdf"] = caminho_pdf

    return resultado
