"""Simulação local do GestãoClick para testar o sistema completo sem API real."""

from utils.data_hora import agora_utc


def _escapar_pdf(texto):
    return (
        texto
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def _gerar_pdf_simples(texto):
    texto = _escapar_pdf(texto)

    stream = (
        "BT\n"
        "/F1 16 Tf\n"
        "72 720 Td\n"
        f"({texto}) Tj\n"
        "ET\n"
    ).encode("latin-1", errors="replace")

    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R "
            b"/MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 5 0 R >> >> "
            b"/Contents 4 0 R >>"
        ),
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    for indice, objeto in enumerate(objetos, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{indice} 0 obj\n".encode())
        pdf.extend(objeto)
        pdf.extend(b"\nendobj\n")

    inicio_xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objetos) + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")

    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\n"
            f"startxref\n{inicio_xref}\n%%EOF\n"
        ).encode()
    )

    return bytes(pdf)


class MockGestaoClickAPI:
    origem = "gestaoclick_mock"
    ambiente = "simulacao"

    def __init__(self):
        self.notas = {}

    def buscar_pedidos_pendentes(self):
        from services.vendas import pedidos_ficticios
        return pedidos_ficticios()

    def criar_nota(self, dados):
        numero_pedido = dados["numero_pedido"]
        id_externo = f"SIM-{numero_pedido}"

        self.notas[id_externo] = {
            "id_externo": id_externo,
            "numero_pedido": numero_pedido,
            "dados": dados,
            "status_nfe": "criada"
        }

        return {
            "id_externo": id_externo,
            "status_nfe": "criada"
        }

    def emitir_nota(self, id_externo):
        """Nem a referência DEMO simula emissão automática após a nova regra."""
        raise RuntimeError('Emissão automática proibida. Emita manualmente no GestãoClick.')

    def consultar_nota(self, id_externo):
        return self.notas[id_externo].copy()

    def baixar_xml(self, id_externo):
        nota = self.notas[id_externo]

        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<nfe_simulada>\n"
            f"  <id>{id_externo}</id>\n"
            f"  <numero_pedido>{nota['numero_pedido']}</numero_pedido>\n"
            f"  <status>{nota['status_nfe']}</status>\n"
            "</nfe_simulada>\n"
        )

    def baixar_pdf(self, id_externo):
        nota = self.notas[id_externo]
        return _gerar_pdf_simples(
            f"NF-e simulada - Pedido {nota['numero_pedido']}"
        )
