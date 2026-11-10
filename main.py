# Importa as funções que cuidam dos pedidos, horários, banco, arquivos e logs
from services.vendas import (
    buscar_pedidos_pendentes,
    pedido_liberado_gerar_nfe
)
from services.validacao import validar_venda
from services.arquivos import limpar_arquivos_expirados
from utils.data_hora import agora_utc, formatar_horario_local
from utils.logger import configurar_logger, limpar_logs_expirados
from database.nfe_repository import (
    inicializar_banco,
    registrar_processamento,
    marcar_arquivo_removido
)


def solicitar_autorizacao_em_andamento():
    usuario = input(
        "Digite o nome de quem está autorizando a emissão da NF-e:"
    ).strip().upper()

    resposta = input(
        "Pedido em andamento. Autorizar emissão da NF-e? (s/n):"
    ).strip().lower()

    if resposta == "s":
        data_hora_autorizacao = agora_utc()
        return True, usuario, data_hora_autorizacao

    return False, None, None


def main():
    inicializar_banco()

    # As limpezas acontecem automaticamente sempre que a aplicação inicia.
    arquivos_excluidos = limpar_arquivos_expirados()
    for caminho in arquivos_excluidos:
        marcar_arquivo_removido(caminho)

    limpar_logs_expirados()
    logger = configurar_logger()

    logger.info("Aplicação iniciada.")
    logger.info(
        "Limpeza de arquivos finalizada: %s arquivo(s) removido(s).",
        len(arquivos_excluidos)
    )

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

        erros_validacao = validar_venda(pedido)

        if erros_validacao:
            liberado = False
            status_processamento = "bloqueado"

            print("Pedido bloqueado por validação:")
            for erro in erros_validacao:
                print("-", erro)

            logger.warning(
                "Pedido %s bloqueado por validação: %s",
                numero_pedido,
                " | ".join(erros_validacao)
            )

        else:
            if status == "em andamento":
                (
                    autorizacao_em_andamento,
                    usuario_autorizador,
                    data_hora_autorizacao
                ) = solicitar_autorizacao_em_andamento()

            liberado = pedido_liberado_gerar_nfe(
                pedido,
                autorizacao_em_andamento
            )

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

        if liberado:
            print("Pedido liberado para gerar NF-e.")
            logger.info("Pedido %s liberado para NF-e.", numero_pedido)

            if usuario_autorizador:
                print("Autorizado por:", usuario_autorizador)
                print(
                    "Data/hora:",
                    formatar_horario_local(data_hora_autorizacao)
                )

                logger.info(
                    "Pedido %s autorizado por %s.",
                    numero_pedido,
                    usuario_autorizador
                )
        else:
            print("Pedido NÃO liberado para gerar NF-e.")
            logger.info("Pedido %s bloqueado.", numero_pedido)

    logger.info("Processamento finalizado.")


if __name__ == "__main__":
    main()
