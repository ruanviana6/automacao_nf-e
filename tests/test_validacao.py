from services.validacao import validar_venda


def criar_pedido_valido():
    return {
        "numero_pedido": 1001,
        "status": "Em separação",
        "cliente": {
            "nome": "Cliente Teste",
            "documento": "12345678900",
            "uf": "CE"
        },
        "produtos": [
            {
                "descricao": "Produto A",
                "quantidade": 2,
                "valor_unitario": 50.00
            }
        ],
        "valor_total": 100.00
    }


def test_pedido_valido_nao_tem_erros():
    pedido = criar_pedido_valido()

    assert validar_venda(pedido) == []


def test_detecta_valor_total_divergente():
    pedido = criar_pedido_valido()
    pedido["valor_total"] = 90.00

    erros = validar_venda(pedido)

    assert any("Valor total divergente" in erro for erro in erros)


def test_detecta_cliente_sem_nome():
    pedido = criar_pedido_valido()
    pedido["cliente"]["nome"] = ""

    erros = validar_venda(pedido)

    assert "Cliente sem nome." in erros
