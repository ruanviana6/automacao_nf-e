"""Controle dos XMLs e PDFs salvos temporariamente."""

from pathlib import Path
from datetime import datetime, timedelta, timezone
from utils.data_hora import agora_utc
import os

# Define as pastas usadas para guardar temporariamente XML e PDF
PASTA_XML = Path("data/xml")
PASTA_PDF = Path("data/pdf")


# Garante que as pastas existam antes de tentar salvar arquivos
def preparar_pastas():
    # parents=True permite criar também pastas anteriores, se necessário
    # exist_ok=True evita erro caso a pasta já exista
    PASTA_XML.mkdir(
        parents=True,
        exist_ok=True
    )
    PASTA_PDF.mkdir(
        parents=True,
        exist_ok=True
    )

# Salva o XML como texto usando UTF-8 e devolve o caminho criado
def salvar_xml(conteudo, nome_arquivo):
    preparar_pastas()
    # O operador / do Path monta caminhos de forma simples e legível
    caminho_arquivo = PASTA_XML / nome_arquivo
    caminho_arquivo.write_text(conteudo, encoding="utf-8")
    return caminho_arquivo

# Salva o PDF como bytes, pois PDF é um arquivo binário e não texto comum
def salvar_pdf(conteudo, nome_arquivo):
    preparar_pastas()
    caminho_arquivo = PASTA_PDF / nome_arquivo
    caminho_arquivo.write_bytes(conteudo)
    return caminho_arquivo

# Verifica se um arquivo passou do prazo de retenção definido
def arquivo_expirado(caminho_arquivo, dias=45):
    # Converte o caminho recebido para Path para usar os recursos de arquivo
    caminho_arquivo = Path(caminho_arquivo)
    # Se o arquivo não existir, não há nada para considerar expirado
    if not caminho_arquivo.exists():
        return False
    # st_mtime guarda o momento da última modificação do arquivo em formato timestamp
    timestamp_modificacao = caminho_arquivo.stat().st_mtime
    # Converte o timestamp para datetime usando UTC, mantendo o padrão de horário do sistema
    data_modificacao = datetime.fromtimestamp(
        timestamp_modificacao,
        tz=timezone.utc
    )
    # Calcula o limite comparando o momento atual com o prazo de retenção
    limite = agora_utc() - timedelta(days=dias)
    # Retorna True quando a data do arquivo é anterior ao limite
    return data_modificacao < limite

# Percorre as pastas de XML e PDF e remove somente arquivos que passaram do prazo
def limpar_arquivos_expirados(dias=45):
    preparar_pastas()
    # Agrupa as duas pastas para usar a mesma lógica de limpeza
    pastas = [PASTA_XML, PASTA_PDF]
    # Guarda os caminhos removidos para permitir relatório ou log depois
    arquivos_excluidos = []
    for pasta in pastas:
        # iterdir() percorre os itens existentes dentro de cada pasta
        for arquivo in pasta.iterdir():
            # Só exclui quando for arquivo e estiver realmente expirado
            if arquivo.is_file() and arquivo_expirado(arquivo, dias):
                # unlink() remove o arquivo local
                arquivo.unlink()
                arquivos_excluidos.append(arquivo)
    return arquivos_excluidos

# Permite excluir manualmente um arquivo, mas somente dentro das pastas controladas pelo sistema
def excluir_arquivo_manual(caminho_arquivo):
    caminho_arquivo = Path(caminho_arquivo)
    # Evita tentar excluir algo que não existe
    if not caminho_arquivo.exists():
        return False
    # Evita tratar uma pasta como se fosse arquivo
    if not caminho_arquivo.is_file():
        return False
    # resolve() transforma o caminho em um caminho completo para validar sua localização real
    caminho_resolvido = caminho_arquivo.resolve()

    pasta_xml = PASTA_XML.resolve()
    pasta_pdf = PASTA_PDF.resolve()

    # Só permite apagar se o arquivo estiver dentro de data/xml ou data/pdf
    # Essa verificação evita apagar arquivos de outras partes do projeto ou do sistema
    if(pasta_xml not in caminho_resolvido.parents
       and pasta_pdf not in caminho_resolvido.parents):
       return False
    caminho_arquivo.unlink()
    return True


