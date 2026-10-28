"""Funções relacionadas às vendas.

Este arquivo não precisa saber como a API funciona internamente.
"""
""" Regras relacionadas aos pedidos
Por enquanto vamos usar pedidos ficticios pra desenvolver e testar a lógica antes de conectar a API oficial
Regras atuais para emissão da NF-e:
1 - O cliente deve ser do Ceará(CE)
2 - Pedidos com status  "Em separação" podem gerar NF-e.
3 - Pedidos com status "Concretizada" podem gerar NF-e.
4 - Pedidos com status "Em andamento" só podem gerar NF-e com autorização.
5 - A emissão só deve ser feito seguindo essa regra, caso tenha alguma alteração nas regras, sendo necessaria a documentação.
"""

# Retorna pedidos fictícios para testar a lógica antes da integração com a API real
def buscar_pedidos_pendentes():
    # A lista guarda vários pedidos e cada pedido é representado por um dicionário
    # Inicialmente vamos retornar vendas fictícias.
    # Pedido 1
    pedidos = [{
        "numero_pedido": 1001,
        "status": "Em separação",
        # O cliente fica em um dicionário dentro do pedido
        "cliente": {"nome": "Ruan Viana",
                    "documento": 61160263388,
                    "uf": "Ceará"},
        # Produtos ficam em uma lista porque um pedido pode ter um ou vários itens
        "produtos": [{ "descricao": "Produto A",
                      "quantidade": 2,
                      "valor_unitario": 50.00}],
        "valor_total": 100.00},
    # Pedido 2
        {"numero_pedido": 1002,
        "status": "Concretizada",
        "cliente": {"nome": "Chico Jr",
                    "documento": 1313131313,
                    "uf": "Ceará"},
        "produtos": [{ "descricao": "Produto B",
                      "quantidade": 3,
                      "valor_unitario": 20.00},
                    {"descricao": "Produto C",
                      "quantidade": 2,
                      "valor_unitario": 40.00}],
        "valor_total": 140.00},
    # Pedido 3
         {"numero_pedido": 1003,
        "status": "Em andamento",
        "cliente": {"nome": "Jessica Alves",
                    "documento": 222222222222,
                    "uf": "Ceará"},
        "produtos": [{ "descricao": "Produto D",
                      "quantidade": 3,
                      "valor_unitario": 50.00},
                    {"descricao": "Produto E",
                      "quantidade": 2,
                      "valor_unitario": 80.00}],
        "valor_total": 310.00},
        # Pedido 4 - Pedido para testar a regra do estado
        {"numero_pedido": 1004,
        "status": "Em separação",
        "cliente": {"nome": "Elana Debora",
                    "documento": 99999999999,
                    "uf": "Piaui"},
        "produtos": [{ "descricao": "Produto F",
                      "quantidade": 5,
                      "valor_unitario": 25.00}],
        "valor_total": 125.00}]
    
    # Entrega a lista completa para quem chamou a função
    return pedidos

# Decide se um pedido está liberado para gerar NF-e conforme UF, status e autorização
# O parâmetro autorizacao_em_andamento começa como False para bloquear exceções por padrão
def  pedido_liberado_gerar_nfe(pedido, autorizacao_em_andamento=False):
# Verificação estado do cliente
# Padronização do valor UF antes das comparações
    # Acessa a UF dentro de cliente e padroniza o texto antes de comparar
    uf_cliente = pedido["cliente"]["uf"].strip().lower()
    # Aceita formas diferentes de escrever Ceará e bloqueia qualquer outro estado
    if uf_cliente not in ["ce", "ceará", "ceara"]:
        return False
# Verificação status atual do pedido
    # Padroniza o status pelo mesmo motivo: evitar diferença de escrita na comparação
    status = pedido["status"].strip().lower()
    # Esses dois status podem seguir normalmente sem autorização extra
    if status in ["em separação", "concretizada"]:
        return True
    # Pedido em andamento depende diretamente da autorização recebida pelo main
    if status == "em andamento":
        return autorizacao_em_andamento
    # Qualquer status fora das regras conhecidas é bloqueado por segurança
    return False

    pass