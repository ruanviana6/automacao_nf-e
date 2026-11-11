import argparse

from api.provider import obter_provedor
from config.settings import MODO_SIMULACAO, USUARIO_EXECUCAO
from database.nfe_repository import (
    inicializar_banco,
    marcar_arquivo_removido,
    registrar_processamento
)
from services.arquivos import (
    excluir_arquivo_manual,
    listar_arquivos_locais
)
from services.notas import processar_nota
from services.rotinas import (
    enviar_relatorio_periodo,
    executar_limpeza,
    executar_relatorio_automatico,
    gerar_relatorio_periodo
)
from services.validacao import validar_venda
from services.vendas import (
    buscar_pedidos_pendentes,
    pedido_liberado_gerar_nfe
)
from utils.data_hora import agora_utc, formatar_horario_local
from utils.logger import configurar_logger


def solicitar_autorizacao_em_andamento():
    usuario = input(
        "Digite o nome de quem está autorizando a emissão da NF-e: "
    ).strip().upper()

    resposta = input(
        "Pedido em andamento. Autorizar emissão da NF-e? (s/n): "
    ).strip().lower()

    if resposta == "s":
        return True, usuario, agora_utc()

    return False, None, None


def obter_usuario_execucao():
    if USUARIO_EXECUCAO:
        return USUARIO_EXECUCAO.upper()

    usuario = input(
        "Digite o nome de quem está executando a automação: "
    ).strip().upper()

    return usuario or "SISTEMA"


def processar_pedidos(logger):
    provedor = obter_provedor()
    usuario_gerador = obter_usuario_execucao()
    pedidos = buscar_pedidos_pendentes(provedor)

    logger.info(
        "Processamento iniciado em modo %s.",
        "SIMULAÇÃO" if MODO_SIMULACAO else "PRODUÇÃO"
    )

    for pedido in pedidos:
        numero_pedido = pedido["numero_pedido"]
        status = str(
            pedido.get("status", "")
        ).strip().lower()

        print("\n------------------")
        print("Pedido:", numero_pedido)
        print("Status:", status)

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
            status_processamento = (
                "liberado"
                if liberado
                else "bloqueado"
            )

        registrar_processamento({
            "numero_pedido": numero_pedido,
            "status_pedido": status,
            "liberado": liberado,
            "usuario_autorizador": usuario_autorizador,
            "data_hora_autorizacao": data_hora_autorizacao,
            "status_processamento": status_processamento
        })

        if not liberado:
            print("Pedido NÃO liberado para gerar NF-e.")
            logger.info("Pedido %s bloqueado.", numero_pedido)
            continue

        print("Pedido liberado para gerar NF-e.")

        if usuario_autorizador:
            print(
                "Autorizado por:",
                usuario_autorizador
            )
            print(
                "Data/hora:",
                formatar_horario_local(
                    data_hora_autorizacao
                )
            )

        try:
            resultado = processar_nota(
                pedido,
                provedor,
                usuario_gerador
            )
        except Exception:
            logger.exception(
                "Falha ao processar NF-e do pedido %s.",
                numero_pedido
            )
            print(
                "Falha ao processar a NF-e. Consulte o log."
            )
            continue

        if resultado["status"] == "duplicada":
            print(
                "NF-e já registrada para este pedido. Emissão ignorada."
            )
            logger.warning(
                "Pedido %s ignorado para evitar duplicidade.",
                numero_pedido
            )
            continue

        if resultado["status"] == "pendente_consulta":
            print(
                "Já existe uma NF-e criada para este pedido, "
                "mas o resultado final precisa ser consultado antes de nova emissão."
            )
            logger.warning(
                "Pedido %s possui NF-e pendente de consulta (ID externo: %s).",
                numero_pedido,
                resultado.get("id_externo")
            )
            continue

        print(
            "NF-e processada com status:",
            resultado["status"]
        )

        if resultado.get("numero_nfe"):
            print(
                "Número:",
                resultado["numero_nfe"]
            )

        if resultado.get("caminho_xml"):
            print(
                "XML:",
                resultado["caminho_xml"]
            )

        if resultado.get("caminho_pdf"):
            print(
                "PDF:",
                resultado["caminho_pdf"]
            )

        logger.info(
            "NF-e do pedido %s processada com status %s.",
            numero_pedido,
            resultado["status"]
        )

    executar_relatorio_automatico(logger)
    logger.info("Processamento finalizado.")


def criar_parser():
    parser = argparse.ArgumentParser(
        description="Automação de NF-e"
    )

    parser.add_argument(
        "--limpar",
        action="store_true",
        help="Executa a limpeza manual dos arquivos e logs expirados."
    )
    parser.add_argument(
        "--listar-arquivos",
        action="store_true",
        help="Lista XMLs e PDFs armazenados localmente."
    )
    parser.add_argument(
        "--excluir-arquivo",
        metavar="CAMINHO",
        help="Exclui manualmente um XML ou PDF local."
    )
    parser.add_argument(
        "--relatorio",
        action="store_true",
        help="Gera o relatório do período configurado."
    )
    parser.add_argument(
        "--enviar-relatorio",
        action="store_true",
        help="Gera e envia o relatório por e-mail."
    )

    return parser


def main():
    inicializar_banco()
    logger = configurar_logger()
    args = criar_parser().parse_args()

    limpeza = executar_limpeza()
    logger.info(
        "Limpeza automática: %s arquivo(s) e %s log(s) removido(s).",
        len(limpeza["arquivos"]),
        len(limpeza["logs"])
    )

    if args.limpar:
        print(
            "Limpeza concluída:",
            len(limpeza["arquivos"]),
            "arquivo(s) e",
            len(limpeza["logs"]),
            "log(s) removido(s)."
        )
        return

    if args.listar_arquivos:
        arquivos = listar_arquivos_locais()

        if not arquivos:
            print("Nenhum XML/PDF armazenado localmente.")
            return

        for arquivo in arquivos:
            print(arquivo)
        return

    if args.excluir_arquivo:
        removido = excluir_arquivo_manual(
            args.excluir_arquivo
        )

        if removido:
            marcar_arquivo_removido(
                args.excluir_arquivo
            )
            print(
                "Arquivo local excluído com sucesso."
            )
        else:
            print(
                "Arquivo não encontrado ou exclusão não permitida."
            )
        return

    if args.relatorio:
        resultado = gerar_relatorio_periodo()
        print(
            "Relatório gerado:",
            resultado["caminho"],
            "-",
            resultado["quantidade_notas"],
            "nota(s)."
        )
        return

    if args.enviar_relatorio:
        resultado = enviar_relatorio_periodo()
        print(
            "Relatório enviado:",
            resultado["quantidade_notas"],
            "nota(s)."
        )
        return

    processar_pedidos(logger)


if __name__ == "__main__":
    main()
