from datetime import datetime, timezone
from zoneinfo import ZoneInfo

FUSO_LOCAL = ZoneInfo("America/Fortaleza")

def agora_utc():
    return datetime.now(timezone.utc)

def formatar_horario_local(data_hora):
    horario_local = data_hora.astimezone(FUSO_LOCAL)
    return horario_local.strftime("%d/%m/%Y %H:%M:%S")