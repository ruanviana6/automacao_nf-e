"""Vocabulário fiscal observado, sem presumir códigos ou transições da API."""

import unicodedata

ESTADOS_OFICIAIS = ('Em aberto', 'Aprovada', 'Reprovada', 'Denegada', 'Cancelada', 'Enviando', 'Corrigida')


def normalizar_estado(valor):
    """Normaliza somente rótulos conhecidos; desconhecido também bloqueia recriação."""
    if not isinstance(valor, str):
        return 'desconhecido'
    texto = ''.join(c for c in unicodedata.normalize('NFKD', valor.strip()) if not unicodedata.combining(c)).casefold()
    for estado in ESTADOS_OFICIAIS + ('criada', 'processando', 'simulada'):
        normal = ''.join(c for c in unicodedata.normalize('NFKD', estado) if not unicodedata.combining(c)).casefold()
        if texto == normal:
            return estado
    return 'desconhecido'
