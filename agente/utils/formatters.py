"""
Utilitários de formatação para o sistema SDR Agent
"""

import re
from typing import Optional, Union
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from loguru import logger


def format_phone_number(phone: str) -> str:
    """
    Formata número de telefone para o padrão brasileiro
    
    Args:
        phone: Número de telefone em qualquer formato
        
    Returns:
        Número formatado: +5511999999999
    """
    # Remove todos os caracteres não numéricos
    digits = re.sub(r'\D', '', phone)
    
    # Remove o 9 extra se tiver 13 dígitos (5511999999999)
    if len(digits) == 13 and digits[4] == '9':
        digits = digits[:4] + digits[5:]
    
    # Adiciona código do país se não tiver
    if not digits.startswith('55'):
        digits = '55' + digits
    
    # Adiciona + no início
    return '+' + digits


def format_currency(value: Union[float, Decimal, str]) -> str:
    """
    Formata valor monetário para o padrão brasileiro
    
    Args:
        value: Valor monetário
        
    Returns:
        Valor formatado: R$ 1.234,56
    """
    if isinstance(value, str):
        # Remove R$ e espaços, substitui vírgula por ponto
        value = value.replace('R$', '').replace(' ', '').replace(',', '.')
        value = float(value)
    
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def format_cpf_cnpj(document: str) -> str:
    """
    Formata CPF ou CNPJ
    
    Args:
        document: CPF ou CNPJ sem formatação
        
    Returns:
        Documento formatado
    """
    # Remove caracteres não numéricos
    digits = re.sub(r'\D', '', document)
    
    if len(digits) == 11:  # CPF
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    elif len(digits) == 14:  # CNPJ
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
    else:
        return document  # Retorna original se não for válido


def format_address(
    street: Optional[str] = None,
    number: Optional[str] = None,
    complement: Optional[str] = None,
    neighborhood: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None
) -> str:
    """
    Formata endereço completo
    
    Returns:
        Endereço formatado
    """
    parts = []
    
    if street:
        if number:
            parts.append(f"{street}, {number}")
            if complement:
                parts[-1] += f" - {complement}"
        else:
            parts.append(street)
    
    if neighborhood:
        parts.append(neighborhood)
    
    if city:
        if state:
            parts.append(f"{city}/{state}")
        else:
            parts.append(city)
    
    if zip_code:
        # Formata CEP: 12345-678
        zip_clean = re.sub(r'\D', '', zip_code)
        if len(zip_clean) == 8:
            parts.append(f"CEP: {zip_clean[:5]}-{zip_clean[5:]}")
        else:
            parts.append(f"CEP: {zip_code}")
    
    return ", ".join(parts)


def format_datetime(dt: datetime, format: str = "full") -> str:
    """
    Formata datetime para exibição
    
    Args:
        dt: Datetime para formatar
        format: Tipo de formato (full, date, time, relative)
        
    Returns:
        Data/hora formatada
    """
    if format == "full":
        return dt.strftime("%d/%m/%Y às %H:%M")
    elif format == "date":
        return dt.strftime("%d/%m/%Y")
    elif format == "time":
        return dt.strftime("%H:%M")
    elif format == "relative":
        return format_relative_time(dt)
    else:
        return str(dt)


def format_relative_time(dt: datetime) -> str:
    """
    Formata tempo relativo (ex: há 5 minutos)
    
    Args:
        dt: Datetime para comparar
        
    Returns:
        Tempo relativo formatado
    """
    now = datetime.now()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return "agora mesmo"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"há {minutes} minuto{'s' if minutes > 1 else ''}"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"há {hours} hora{'s' if hours > 1 else ''}"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"há {days} dia{'s' if days > 1 else ''}"
    else:
        return dt.strftime("%d/%m/%Y")


def format_consumption(kwh: Union[int, float]) -> str:
    """
    Formata consumo de energia
    
    Args:
        kwh: Consumo em kWh
        
    Returns:
        Consumo formatado
    """
    return f"{int(kwh):,} kWh".replace(',', '.')


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formata percentual
    
    Args:
        value: Valor entre 0 e 1 ou 0 e 100
        decimals: Casas decimais
        
    Returns:
        Percentual formatado
    """
    # Se valor menor que 1, assume que está em decimal
    if value <= 1:
        value = value * 100
    
    if decimals == 0:
        return f"{int(value)}%"
    else:
        return f"{value:.{decimals}f}%"


def format_meeting_title(lead_name: str, company: str = "SolarPrime") -> str:
    """
    Formata título da reunião
    
    Args:
        lead_name: Nome do lead
        company: Nome da empresa
        
    Returns:
        Título formatado
    """
    return f"Reunião {company} - {lead_name}"


def format_meeting_description(
    lead_name: str,
    phone: str,
    consultant: str = "Helen Vieira",
    address: Optional[str] = None,
    bill_value: Optional[float] = None
) -> str:
    """
    Formata descrição completa da reunião
    
    Returns:
        Descrição formatada
    """
    description = f"""📅 Reunião de Apresentação - Energia Solar SolarPrime

👤 Cliente: {lead_name}
📱 WhatsApp: {phone}
👩‍💼 Consultora: {consultant}

🏠 Endereço: {address or 'A confirmar'}
💰 Valor atual da conta: {format_currency(bill_value) if bill_value else 'A informar'}

📋 Pauta:
• Apresentação da solução de energia solar
• Análise personalizada de economia
• Esclarecimento de dúvidas
• Proposta comercial

⏱️ Duração estimada: 1 hora

💬 Confirme sua presença respondendo esta mensagem!
"""
    return description


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca texto longo preservando palavras completas
    
    Args:
        text: Texto para truncar
        max_length: Tamanho máximo
        suffix: Sufixo para adicionar
        
    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text
    
    # Encontra o último espaço antes do limite
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + suffix


def clean_text(text: str) -> str:
    """
    Limpa texto removendo caracteres especiais e espaços extras
    
    Args:
        text: Texto para limpar
        
    Returns:
        Texto limpo
    """
    # Remove múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    
    # Remove espaços no início e fim
    text = text.strip()
    
    # Remove caracteres de controle
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    
    return text


def extract_numbers(text: str) -> list[float]:
    """
    Extrai números de um texto
    
    Args:
        text: Texto para extrair números
        
    Returns:
        Lista de números encontrados
    """
    # Padrão para números com vírgula como decimal
    pattern = r'\d+(?:[.,]\d+)?'
    matches = re.findall(pattern, text)
    
    numbers = []
    for match in matches:
        # Substitui vírgula por ponto
        number_str = match.replace(',', '.')
        try:
            numbers.append(float(number_str))
        except ValueError:
            logger.warning(f"Não foi possível converter '{match}' para número")
    
    return numbers


def format_bullet_list(items: list[str], bullet: str = "•") -> str:
    """
    Formata lista com bullets
    
    Args:
        items: Itens da lista
        bullet: Caractere do bullet
        
    Returns:
        Lista formatada
    """
    return "\n".join([f"{bullet} {item}" for item in items])


def format_stage_name(stage: str) -> str:
    """
    Formata nome do estágio para exibição
    
    Args:
        stage: Nome do estágio em UPPER_CASE
        
    Returns:
        Nome formatado
    """
    stage_names = {
        "INITIAL_CONTACT": "Contato Inicial",
        "IDENTIFYING": "Identificando",
        "QUALIFYING": "Qualificando",
        "QUALIFIED": "Qualificado",
        "SCHEDULING": "Agendando",
        "SCHEDULED": "Agendado",
        "NOT_INTERESTED": "Não Interessado",
        "LOST": "Perdido"
    }
    
    return stage_names.get(stage, stage.replace("_", " ").title())


def ensure_timezone_aware(dt: Union[datetime, str, None]) -> Optional[datetime]:
    """
    Garante que um datetime seja timezone-aware (UTC).
    
    Esta função resolve o erro comum "can't subtract offset-naive and offset-aware datetimes"
    garantindo que todos os datetimes tenham informação de timezone.
    
    Args:
        dt: Datetime, string ISO ou None
        
    Returns:
        Datetime timezone-aware em UTC ou None
        
    Examples:
        >>> ensure_timezone_aware("2025-01-01T10:00:00Z")
        datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        
        >>> ensure_timezone_aware("2025-01-01T10:00:00")  # sem timezone
        datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
    """
    if dt is None:
        return None
    
    try:
        # Se já é datetime
        if isinstance(dt, datetime):
            # Se já tem timezone, retorna como está
            if dt.tzinfo is not None:
                return dt
            # Se não tem timezone, assume UTC
            return dt.replace(tzinfo=timezone.utc)
        
        # Se é string, converte para datetime
        if isinstance(dt, str):
            # Trata diferentes padrões de string ISO
            dt_str = dt.strip()
            
            # Se termina com Z, substitui por +00:00
            if dt_str.endswith('Z'):
                dt_str = dt_str[:-1] + '+00:00'
            
            # Se não tem timezone info, adiciona UTC
            if '+' not in dt_str and 'Z' not in dt and dt_str.count('T') == 1:
                dt_str += '+00:00'
            
            # Converte usando fromisoformat
            parsed_dt = datetime.fromisoformat(dt_str)
            
            # Se ainda não tem timezone após conversão, assume UTC
            if parsed_dt.tzinfo is None:
                parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
            
            return parsed_dt
            
    except (ValueError, TypeError) as e:
        logger.warning(f"Erro ao converter datetime '{dt}' para timezone-aware: {e}")
        return None
    
    # Se chegou aqui, tipo não suportado
    logger.warning(f"Tipo não suportado para ensure_timezone_aware: {type(dt)}")
    return None