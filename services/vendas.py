"""Pedidos e regras de negócio usadas antes da emissão da NF-e."""


def pedidos_ficticios():
    return [
        {
            "numero_pedido": 1001,
            "status": "Em separação",
            "cliente": {
                "nome": "Ruan Viana",
                "documento": 61160263388,
                "uf": "Ceará"
            },
            "produtos": [
                {
                    "descricao": "Produto A",
                    "quantidade": 2,
                    "valor_unitario": 50.00
                }
            ],
            "valor_total": 100.00
        },
        {
            "numero_pedido": 1002,
            "status": "Concretizada",
            "cliente": {
                "nome": "Chico Jr",
                "documento": 1313131313,
                "uf": "Ceará"
            },
            "produtos": [
                {
                    "descricao": "Produto B",
                    "quantidade": 3,
                    "valor_unitario": 20.00
                },
                {
                    "descricao": "Produto C",
                    "quantidade": 2,
                    "valor_unitario": 40.00
                }
            ],
            "valor_total": 140.00
        },
        {
            "numero_pedido": 1003,
            "status": "Em andamento",
            "cliente": {
                "nome": "Jessica Alves",
                "documento": 222222222222,
                "uf": "Ceará"
            },
            "produtos": [
                {
                    "descricao": "Produto D",
                    "quantidade": 3,
                    "valor_unitario": 50.00
                },
                {
                    "descricao": "Produto E",
                    "quantidade": 2,
                    "valor_unitario": 80.00
                }
            ],
            "valor_total": 310.00
        },
        {
            "numero_pedido": 1004,
            "status": "Em separação",
            "cliente": {
                "nome": "Elana Debora",
                "documento": 99999999999,
                "uf": "Piaui"
            },
            "produtos": [
                {
                    "descricao": "Produto F",
                    "quantidade": 5,
                    "valor_unitario": 25.00
                }
            ],
            "valor_total": 125.00
        }
    ]


def buscar_pedidos_pendentes(provedor=None):
    if provedor is not None:
        return provedor.buscar_pedidos_pendentes()

    return pedidos_ficticios()


def pedido_liberado_gerar_nfe(pedido, autorizacao_em_andamento=False):
    uf_cliente = pedido["cliente"]["uf"].strip().lower()

    if uf_cliente not in ["ce", "ceará", "ceara"]:
        return False

    status = pedido["status"].strip().lower()

    if status in ["em separação", "concretizada"]:
        return True

    if status == "em andamento":
        return autorizacao_em_andamento

    return False
