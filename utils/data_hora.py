from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from config.settings import FUSO_HORARIO

# Define o fuso usado para mostrar datas e horários ao usuário
FUSO_LOCAL = ZoneInfo(FUSO_HORARIO)

# Retorna o horário atual em UTC para manter um padrão interno no sistema
def agora_utc():
    return datetime.now(timezone.utc)

# Converte um datetime em UTC para o horário local e devolve em formato legível
def formatar_horario_local(data_hora):
    horario_local = data_hora.astimezone(FUSO_LOCAL)
    # strftime organiza a data no formato dia/mês/ano hora:minuto:segundo
    return horario_local.strftime("%d/%m/%Y %H:%M:%S")