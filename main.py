# Importação das funções de vendas e banco de dados
from services.vendas import(
    buscar_pedidos_pendentes, pedido_liberado_gerar_nfe
)
from utils.data_hora import (agora_utc, formatar_horario_local)
from database.database import (inicializar_banco, registrar_processamento)

# Função para autorizar a emissão de notas de pedidos ainda em andamento
def solicitar_autorizacao_em_andamento():
    usuario = input("Digite o nome de quem está autorizando a emissão da NF-e:").strip().upper()
    resposta = input("Pedido em andamento. Autorizar emissão da NF-e? (s/n):").strip().lower()
    if resposta =="s":
        data_hora_autorizacao = agora_utc()
        return True, usuario, data_hora_autorizacao
    return False, None, None

def main():
   inicializar_banco()
   pedidos = buscar_pedidos_pendentes()
   for pedido in pedidos:
       numero_pedido = pedido["numero_pedido"]
       status = pedido["status"].strip().lower()
       print("\n------------------")
       print("Pedido", numero_pedido)
       print("Status", status)
       autorizacao_em_andamento = False
       usuario_autorizador = None
       data_hora_autorizacao = None
       if status == "em andamento":
          (autorizacao_em_andamento, usuario_autorizador, data_hora_autorizacao) = solicitar_autorizacao_em_andamento()
       liberado = pedido_liberado_gerar_nfe(pedido, autorizacao_em_andamento)
       if liberado:
           status_processamento = "liberado"
       else:
           status_processamento = "bloqueado"
       registro = {
              "numero_pedido": numero_pedido,
              "status_pedido": status,
              "liberado": liberado,
              "usuario_autorizador": usuario_autorizador,
              "data_hora_autorizacao": data_hora_autorizacao,
              "status_processamento": status_processamento
       }
       registrar_processamento(registro)
       print(registro)
       if liberado:
            print("Pedido liberado para gerar NF-e.")
            if usuario_autorizador:
                print("Autorizado por:", usuario_autorizador)
                print("Data/hora:", formatar_horario_local(data_hora_autorizacao))
       else:
            print("Pedido NÃO liberado para gerar NF-e.")

if __name__ == "__main__":
   main()