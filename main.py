# Importa as funções que cuidam dos pedidos, horários e banco de dados
# O main apenas coordena essas partes, sem concentrar toda a lógica do projeto
# Importação das funções de vendas e banco de dados
from services.vendas import(
    buscar_pedidos_pendentes, pedido_liberado_gerar_nfe
)
from utils.data_hora import (agora_utc, formatar_horario_local)
from database.nfe_repository import (inicializar_banco, registrar_processamento)

# Solicita uma autorização somente para pedidos que ainda estão "em andamento"
# Retorna três informações juntas: se autorizou, quem autorizou e quando autorizou
# Função para autorizar a emissão de notas de pedidos ainda em andamento
def solicitar_autorizacao_em_andamento():
    # strip() remove espaços extras e upper() padroniza o nome do autorizador
    usuario = input("Digite o nome de quem está autorizando a emissão da NF-e:").strip().upper()
    # lower() permite aceitar respostas como "S" ou "s" da mesma forma
    resposta = input("Pedido em andamento. Autorizar emissão da NF-e? (s/n):").strip().lower()
    if resposta =="s":
        # Guarda o momento da autorização em UTC para manter um padrão interno no sistema
        data_hora_autorizacao = agora_utc()
        # O retorno múltiplo permite levar as três informações para o fluxo principal
        return True, usuario, data_hora_autorizacao
    # Quando não há autorização, usamos False e None para indicar ausência de usuário e horário
    return False, None, None

# Controla o fluxo principal: busca pedidos, aplica regras e registra o resultado no banco
def main():
   # Garante que a estrutura do banco exista antes de tentar gravar qualquer processamento
   inicializar_banco()
   # Por enquanto recebe a lista de pedidos fictícios usada nos testes
   pedidos = buscar_pedidos_pendentes()
   # Analisa cada pedido separadamente
   for pedido in pedidos:
       numero_pedido = pedido["numero_pedido"]
       # Padroniza o status para evitar diferenças de espaços e letras maiúsculas/minúsculas
       status = pedido["status"].strip().lower()
       print("\n------------------")
       print("Pedido", numero_pedido)
       print("Status", status)
       # Valores padrão: pedidos normais não precisam de autorização especial
       autorizacao_em_andamento = False
       usuario_autorizador = None
       data_hora_autorizacao = None
       if status == "em andamento":
          # Recebe os três valores retornados pela função de autorização
          (autorizacao_em_andamento, usuario_autorizador, data_hora_autorizacao) = solicitar_autorizacao_em_andamento()
       # Centraliza em vendas.py a regra que decide se o pedido pode seguir para NF-e
       liberado = pedido_liberado_gerar_nfe(pedido, autorizacao_em_andamento)
       # Transforma o resultado booleano em um status mais legível para o histórico
       if liberado:
           status_processamento = "liberado"
       else:
           status_processamento = "bloqueado"
       # Reúne em um único dicionário os dados que serão enviados ao banco
       registro = {
              "numero_pedido": numero_pedido,
              "status_pedido": status,
              "liberado": liberado,
              "usuario_autorizador": usuario_autorizador,
              "data_hora_autorizacao": data_hora_autorizacao,
              "status_processamento": status_processamento
       }
       # Persiste o resultado do processamento para manter histórico
       registrar_processamento(registro)
       print(registro)
       # Mostra ao usuário o resultado da análise do pedido
       if liberado:
            print("Pedido liberado para gerar NF-e.")
            if usuario_autorizador:
                print("Autorizado por:", usuario_autorizador)
                # Converte o horário interno em UTC para o horário local na exibição
                print("Data/hora:", formatar_horario_local(data_hora_autorizacao))
       else:
            print("Pedido NÃO liberado para gerar NF-e.")

# Faz main() rodar apenas quando este arquivo é executado diretamente
# Se main.py for importado por outro módulo, esse bloco não é executado automaticamente
if __name__ == "__main__":
   main()