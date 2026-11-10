from services.vendas import pedido_liberado_gerar_nfe


def criar_pedido(status, uf="CE"):
    return {
        "numero_pedido": 1,
        "status": status,
        "cliente": {
            "nome": "Cliente",
            "documento": "123",
            "uf": uf
        },
        "produtos": [],
        "valor_total": 0
    }


def test_em_separacao_ce_e_liberado():
    pedido = criar_pedido("Em separação")

    assert pedido_liberado_gerar_nfe(pedido) is True


def test_concretizada_ce_e_liberada():
    pedido = criar_pedido("Concretizada")

    assert pedido_liberado_gerar_nfe(pedido) is True


def test_em_andamento_sem_autorizacao_e_bloqueado():
    pedido = criar_pedido("Em andamento")

    assert pedido_liberado_gerar_nfe(pedido) is False


def test_em_andamento_com_autorizacao_e_liberado():
    pedido = criar_pedido("Em andamento")

    assert pedido_liberado_gerar_nfe(pedido, True) is True


def test_fora_do_ce_e_bloqueado():
    pedido = criar_pedido("Em separação", uf="Piauí")

    assert pedido_liberado_gerar_nfe(pedido) is False
