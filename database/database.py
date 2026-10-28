"""Compatibilidade com a estrutura antiga do banco.

As funções continuam disponíveis por este arquivo para não quebrar imports antigos,
mas a conexão e as operações de NF-e agora ficam separadas em módulos próprios.
"""

# A conexão foi isolada para poder ser reutilizada por outros módulos no futuro
from database.conexao import conectar_banco

# As operações específicas de NF-e ficam concentradas no repositório de NF-e
from database.nfe_repository import (
    inicializar_banco,
    pedido_ja_processado,
    registrar_processamento,
    listar_processamentos
)


# Permite testar a inicialização quando este arquivo é executado diretamente
if __name__ == "__main__":
    inicializar_banco()

    print("Banco inicializado com sucesso.")
