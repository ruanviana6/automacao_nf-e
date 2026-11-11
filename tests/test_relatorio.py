import services.relatorio as relatorio


def test_gera_relatorio_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(
        relatorio,
        "PASTA_RELATORIOS",
        tmp_path
    )

    notas = [
        {
            "id": 1,
            "numero_pedido": 1001,
            "id_externo": "SIM-1001",
            "numero_nfe": "SIM1001",
            "chave_nfe": "SIMULADA00001001",
            "status_nfe": "simulada",
            "usuario_gerador": "TESTE",
            "data_emissao": "2026-11-10T20:00:00+00:00",
            "origem": "gestaoclick_mock",
            "ambiente": "simulacao",
            "criado_em": "2026-11-10T20:00:00+00:00"
        }
    ]

    caminho = relatorio.gerar_relatorio(notas)
    conteudo = caminho.read_text(encoding="utf-8-sig")

    assert "numero_pedido" in conteudo
    assert "1001" in conteudo
