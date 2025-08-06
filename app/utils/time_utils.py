"""
Utilitários de tempo para o sistema SDR IA
"""
from datetime import datetime
import pytz

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