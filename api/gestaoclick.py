"""Integração futura com a API do GestãoClick.

IMPORTANTE:
A lógica da API fica isolada neste arquivo para evitar espalhar
requests, tokens e URLs por todo o projeto.

Quando chegar o momento da integração, este módulo será responsável por:

- autenticar;
- buscar vendas;
- buscar clientes;
- enviar dados de NF-e;
- consultar status;
- baixar XML/PDF.

Por enquanto NÃO vamos implementar endpoints reais.
"""

# FUTURAMENTE:
# import requests
# import os
# from dotenv import load_dotenv


class GestaoClickAPI:
    """Representará nossa conexão com o GestãoClick."""

    def __init__(self):
        # Futuramente vamos carregar aqui:
        # self.base_url
        # self.token
        # self.secret
        pass

    def buscar_vendas(self):
        """Buscará vendas através da API."""
        # TODO: você implementará quando estudarmos GET + requests.
        pass

    def emitir_nota(self, dados):
        """Enviará dados para emissão da NF-e."""
        # TODO: você implementará quando soubermos o endpoint oficial.
        pass

    def consultar_nota(self, nota_id):
        """Consultará o status de uma NF-e."""
        pass
