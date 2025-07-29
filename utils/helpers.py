"""
Funções Auxiliares
==================
Utilitários e helpers para o sistema
"""

import re
import math
from typing import Optional, Dict, Any, List
from datetime import datetime, time, timedelta
import pytz
from loguru import logger

def calculate_typing_delay(message: str, wpm: int = 400) -> float:
    """
    Calcula o delay de digitação baseado no tamanho da mensagem
    OTIMIZADO PARA PERFORMANCE: Máximo 1 segundo
    
    Args:
        message: Mensagem a ser enviada
        wpm: Palavras por minuto de digitação (aumentado para 400)
        
    Returns:
        Tempo em segundos para simular digitação
    """
    # Conta palavras
    words = len(message.split())
    
    # Calcula tempo base
    base_time = (words / wpm) * 60
    
    # Adiciona variação aleatória mínima (±10%)
    import random
    variation = base_time * 0.1
    final_time = base_time + random.uniform(-variation, variation)
    
    # OTIMIZAÇÃO: Limita entre 0.5 e 1 segundo (era 2-10s)
    return max(0.5, min(1.0, final_time))

def format_phone_number(phone: str) -> str:
    """
    Formata número de telefone brasileiro
    
    Args:
        phone: Número de telefone
        
    Returns:
        Número formatado
    """
    # Remove caracteres não numéricos
    digits = re.sub(r'\D', '', phone)
    
    # Adiciona código do país se não tiver
    if len(digits) == 11:  # Celular brasileiro sem código do país
        digits = '55' + digits
    elif len(digits) == 10:  # Fixo brasileiro sem código do país
        digits = '55' + digits
    
    # Formata
    if len(digits) == 13:  # +55 11 99999-9999
        return f"+{digits[:2]} {digits[2:4]} {digits[4:9]}-{digits[9:]}"
    elif len(digits) == 12:  # +55 11 9999-9999
        return f"+{digits[:2]} {digits[2:4]} {digits[4:8]}-{digits[8:]}"
    else:
        return phone  # Retorna original se não conseguir formatar

def extract_phone_from_jid(jid: str) -> str:
    """
    Extrai número de telefone do JID do WhatsApp
    
    Args:
        jid: JID do WhatsApp (ex: 5511999999999@s.whatsapp.net)
        
    Returns:
        Número de telefone
    """
    match = re.match(r'(\d+)@', jid)
    return match.group(1) if match else jid

def is_business_hours(
    timezone: str = "America/Sao_Paulo",
    start_hour: int = 8,
    end_hour: int = 18,
    include_saturday: bool = True
) -> bool:
    """
    Verifica se está em horário comercial
    
    Args:
        timezone: Fuso horário
        start_hour: Hora de início
        end_hour: Hora de fim
        include_saturday: Se inclui sábado
        
    Returns:
        True se está em horário comercial
    """
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    
    # Verifica dia da semana
    weekday = now.weekday()  # 0=Segunda, 6=Domingo
    
    if weekday == 6:  # Domingo
        return False
    
    if weekday == 5 and not include_saturday:  # Sábado
        return False
    
    # Verifica hora
    current_hour = now.hour
    return start_hour <= current_hour < end_hour

def format_currency(value: float) -> str:
    """
    Formata valor em Real brasileiro
    
    Args:
        value: Valor numérico
        
    Returns:
        Valor formatado em R$
    """
    return f"R$ {value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

def parse_currency(text: str) -> Optional[float]:
    """
    Extrai valor monetário de texto
    
    Args:
        text: Texto contendo valor
        
    Returns:
        Valor float ou None
    """
    # Procura por padrões de valor em reais
    patterns = [
        r'R\$\s*(\d+(?:\.\d{3})*(?:,\d{2})?)',  # R$ 1.234,56
        r'(\d+(?:\.\d{3})*(?:,\d{2})?)\s*reais',  # 1.234,56 reais
        r'(\d+(?:,\d{2})?)',  # 1234,56
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value_str = match.group(1)
            # Converte formato brasileiro para float
            value_str = value_str.replace(".", "").replace(",", ".")
            try:
                return float(value_str)
            except ValueError:
                continue
    
    return None

def clean_text(text: str) -> str:
    """
    Limpa e normaliza texto
    
    Args:
        text: Texto a ser limpo
        
    Returns:
        Texto limpo
    """
    # Remove espaços extras
    text = ' '.join(text.split())
    
    # Remove caracteres de controle
    text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
    
    # Normaliza quebras de linha
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def estimate_solar_savings(monthly_bill: float) -> Dict[str, float]:
    """
    Estima economia com energia solar
    
    Args:
        monthly_bill: Valor mensal da conta
        
    Returns:
        Dicionário com estimativas
    """
    # Fatores de cálculo
    savings_percentage = 0.9  # 90% de economia
    system_lifetime_years = 25
    annual_increase = 0.08  # 8% aumento anual energia
    
    # Cálculos
    monthly_savings = monthly_bill * savings_percentage
    annual_savings_year1 = monthly_savings * 12
    
    # Economia total considerando aumentos
    total_savings = 0
    annual_savings = annual_savings_year1
    for year in range(system_lifetime_years):
        total_savings += annual_savings
        annual_savings *= (1 + annual_increase)
    
    # Estimativa de investimento (baseado em payback de 4 anos)
    estimated_investment = annual_savings_year1 * 4
    
    return {
        "monthly_savings": monthly_savings,
        "annual_savings": annual_savings_year1,
        "total_savings_25_years": total_savings,
        "estimated_investment": estimated_investment,
        "payback_years": 4,
        "roi_percentage": (total_savings / estimated_investment - 1) * 100
    }

def get_greeting_by_time(timezone: str = "America/Sao_Paulo") -> str:
    """
    Retorna saudação apropriada baseada no horário
    
    Args:
        timezone: Fuso horário
        
    Returns:
        Saudação apropriada
    """
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    hour = now.hour
    
    if 5 <= hour < 12:
        return "Bom dia"
    elif 12 <= hour < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

def generate_meeting_slots(
    days_ahead: int = 3,
    slots_per_day: int = 4,
    timezone: str = "America/Sao_Paulo"
) -> List[Dict[str, str]]:
    """
    Gera slots de horários para agendamento
    
    Args:
        days_ahead: Dias à frente para gerar
        slots_per_day: Slots por dia
        timezone: Fuso horário
        
    Returns:
        Lista de slots disponíveis
    """
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    slots = []
    
    # Horários padrão
    default_times = ["09:00", "10:30", "14:00", "15:30", "17:00"]
    
    for day_offset in range(1, days_ahead + 1):
        date = now + timedelta(days=day_offset)
        
        # Pula domingo
        if date.weekday() == 6:
            continue
        
        # Formata dia
        day_name = date.strftime("%A").lower()
        day_names = {
            "monday": "Segunda",
            "tuesday": "Terça",
            "wednesday": "Quarta",
            "thursday": "Quinta",
            "friday": "Sexta",
            "saturday": "Sábado"
        }
        
        day_str = f"{day_names.get(day_name, day_name)} ({date.strftime('%d/%m')})"
        
        # Adiciona slots
        for i in range(min(slots_per_day, len(default_times))):
            slots.append({
                "date": date.strftime("%Y-%m-%d"),
                "time": default_times[i],
                "display": f"{day_str} às {default_times[i]}"
            })
    
    return slots[:slots_per_day * 2]  # Retorna apenas alguns slots

def is_valid_email(email: str) -> bool:
    """
    Valida formato de email
    
    Args:
        email: Email a validar
        
    Returns:
        True se válido
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitiza entrada do usuário
    
    Args:
        text: Texto a sanitizar
        max_length: Tamanho máximo
        
    Returns:
        Texto sanitizado
    """
    # Limita tamanho
    text = text[:max_length]
    
    # Remove caracteres perigosos
    text = re.sub(r'[<>\"\'&]', '', text)
    
    # Limpa e normaliza
    return clean_text(text)

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula distância entre coordenadas em km
    
    Args:
        lat1, lon1: Coordenadas do ponto 1
        lat2, lon2: Coordenadas do ponto 2
        
    Returns:
        Distância em quilômetros
    """
    # Raio da Terra em km
    R = 6371
    
    # Converte para radianos
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Fórmula de Haversine
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

# Exporta todas as funções
__all__ = [
    "calculate_typing_delay",
    "format_phone_number",
    "extract_phone_from_jid",
    "is_business_hours",
    "format_currency",
    "parse_currency",
    "clean_text",
    "estimate_solar_savings",
    "get_greeting_by_time",
    "generate_meeting_slots",
    "is_valid_email",
    "sanitize_input",
    "calculate_distance_km"
]