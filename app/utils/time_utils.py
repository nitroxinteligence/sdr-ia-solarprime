"""
Utilitários de tempo para o sistema SDR IA
"""
from datetime import datetime, time, timedelta
import pytz
from app.config import settings

def get_period_of_day(timezone: str = "America/Sao_Paulo") -> str:
    """
    Retorna o período do dia (Manhã, Tarde, Noite) baseado no fuso horário.
    
    Args:
        timezone: String com o fuso horário (padrão: America/Sao_Paulo)
        
    Returns:
        String com o período: "Manhã", "Tarde" ou "Noite"
    """
    try:
        tz = pytz.timezone(timezone)
        current_hour = datetime.now(tz).hour

        if 5 <= current_hour < 12:
            return "Manhã"
        elif 12 <= current_hour < 18:
            return "Tarde"
        else:
            return "Noite"
    except Exception:
        # Fallback em caso de erro de timezone
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            return "Manhã"
        elif 12 <= current_hour < 18:
            return "Tarde"
        else:
            return "Noite"


def adjust_datetime_to_business_hours(dt: datetime) -> datetime:
    """
    Ajusta um datetime para estar dentro do horário comercial (08:00-20:00) 
    e em dias úteis (seg-sex), respeitando o fuso horário do sistema.

    Args:
        dt: O datetime a ser ajustado.

    Returns:
        Um novo objeto datetime ajustado para o próximo horário comercial válido.
    """
    try:
        tz = pytz.timezone(settings.timezone)
    except (pytz.UnknownTimeZoneError, AttributeError):
        # Fallback para timezone padrão se não estiver configurado
        tz = pytz.timezone("America/Sao_Paulo")

    # Garante que o datetime de entrada tenha o fuso horário correto
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    else:
        dt = dt.astimezone(tz)

    business_start = time(8, 0)  # 8:00
    business_end = time(20, 0)   # 20:00

    # Se for fim de semana, avança para a próxima segunda-feira às 8h
    if dt.weekday() >= 5:  # 5 = sábado, 6 = domingo
        days_to_monday = 7 - dt.weekday()
        dt = (dt + timedelta(days=days_to_monday)).replace(
            hour=business_start.hour, 
            minute=business_start.minute, 
            second=0, 
            microsecond=0
        )
        return dt

    # Se for antes do horário comercial, ajusta para o início do dia
    if dt.time() < business_start:
        return dt.replace(
            hour=business_start.hour, 
            minute=business_start.minute, 
            second=0, 
            microsecond=0
        )

    # Se for depois do horário comercial, avança para o próximo dia útil às 8h
    if dt.time() > business_end:
        next_day = dt + timedelta(days=1)
        # Se o próximo dia for fim de semana, avança para segunda
        if next_day.weekday() >= 5:
            days_to_monday = 7 - next_day.weekday()
            next_day += timedelta(days=days_to_monday)
        return next_day.replace(
            hour=business_start.hour, 
            minute=business_start.minute, 
            second=0, 
            microsecond=0
        )

    # Se já está dentro do horário comercial, retorna como está
    return dt


def get_business_aware_datetime(minutes_from_now: int = 0, hours_from_now: int = 0) -> datetime:
    """
    Retorna um datetime ajustado para horário comercial, a partir de agora + delta especificado.
    
    Args:
        minutes_from_now: Minutos a partir de agora
        hours_from_now: Horas a partir de agora
        
    Returns:
        Datetime ajustado para horário comercial
    """
    try:
        tz = pytz.timezone(settings.timezone)
    except (pytz.UnknownTimeZoneError, AttributeError):
        tz = pytz.timezone("America/Sao_Paulo")
    
    # Obter datetime atual com timezone correto
    now_with_tz = datetime.now(tz)
    
    # Aplicar delta
    target_time = now_with_tz + timedelta(minutes=minutes_from_now, hours=hours_from_now)
    
    # Ajustar para horário comercial
    return adjust_datetime_to_business_hours(target_time)