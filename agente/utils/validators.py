"""
Validadores para o sistema SDR Agent
"""

import re
from typing import Optional, Union
from datetime import datetime, time

from loguru import logger


def validate_phone_number(phone: str) -> tuple[bool, Optional[str]]:
    """
    Valida número de telefone brasileiro
    
    Args:
        phone: Número de telefone
        
    Returns:
        (is_valid, error_message)
    """
    # Remove caracteres não numéricos
    digits = re.sub(r'\D', '', phone)
    
    # Remove código do país se tiver
    if digits.startswith('55'):
        digits = digits[2:]
    
    # Verifica se tem 10 ou 11 dígitos (com ou sem 9)
    if len(digits) == 10 or len(digits) == 11:
        # Verifica se começa com DDD válido (11-99)
        ddd = int(digits[:2])
        if 11 <= ddd <= 99:
            return True, None
        else:
            return False, "DDD inválido"
    else:
        return False, "Número de telefone deve ter 10 ou 11 dígitos"


def validate_cpf(cpf: str) -> tuple[bool, Optional[str]]:
    """
    Valida CPF brasileiro
    
    Args:
        cpf: CPF para validar
        
    Returns:
        (is_valid, error_message)
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False, "CPF deve ter 11 dígitos"
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False, "CPF inválido"
    
    # Validação dos dígitos verificadores
    def calculate_digit(digits):
        s = sum(int(digit) * weight for digit, weight in zip(digits, range(len(digits) + 1, 1, -1)))
        remainder = s % 11
        return '0' if remainder < 2 else str(11 - remainder)
    
    # Verifica primeiro dígito
    if cpf[9] != calculate_digit(cpf[:9]):
        return False, "CPF inválido"
    
    # Verifica segundo dígito
    if cpf[10] != calculate_digit(cpf[:10]):
        return False, "CPF inválido"
    
    return True, None


def validate_cnpj(cnpj: str) -> tuple[bool, Optional[str]]:
    """
    Valida CNPJ brasileiro
    
    Args:
        cnpj: CNPJ para validar
        
    Returns:
        (is_valid, error_message)
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'\D', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False, "CNPJ deve ter 14 dígitos"
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False, "CNPJ inválido"
    
    # Validação dos dígitos verificadores
    def calculate_digit(cnpj, digit):
        if digit == 1:
            weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            digits = cnpj[:12]
        else:
            weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            digits = cnpj[:13]
        
        s = sum(int(d) * w for d, w in zip(digits, weights))
        remainder = s % 11
        return '0' if remainder < 2 else str(11 - remainder)
    
    # Verifica primeiro dígito
    if cnpj[12] != calculate_digit(cnpj, 1):
        return False, "CNPJ inválido"
    
    # Verifica segundo dígito
    if cnpj[13] != calculate_digit(cnpj, 2):
        return False, "CNPJ inválido"
    
    return True, None


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Valida endereço de email
    
    Args:
        email: Email para validar
        
    Returns:
        (is_valid, error_message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return True, None
    else:
        return False, "Email inválido"


def validate_cep(cep: str) -> tuple[bool, Optional[str]]:
    """
    Valida CEP brasileiro
    
    Args:
        cep: CEP para validar
        
    Returns:
        (is_valid, error_message)
    """
    # Remove caracteres não numéricos
    cep = re.sub(r'\D', '', cep)
    
    # Verifica se tem 8 dígitos
    if len(cep) == 8:
        return True, None
    else:
        return False, "CEP deve ter 8 dígitos"


def validate_bill_value(value: Union[str, float]) -> tuple[bool, Optional[str]]:
    """
    Valida valor da conta de luz
    
    Args:
        value: Valor para validar
        
    Returns:
        (is_valid, error_message)
    """
    try:
        if isinstance(value, str):
            # Remove R$ e espaços, substitui vírgula por ponto
            value = value.replace('R$', '').replace(' ', '').replace(',', '.')
        
        amount = float(value)
        
        if amount < 0:
            return False, "Valor não pode ser negativo"
        elif amount > 50000:
            return False, "Valor muito alto, verifique se está correto"
        else:
            return True, None
            
    except (ValueError, TypeError):
        return False, "Valor inválido"


def validate_consumption(kwh: Union[str, int]) -> tuple[bool, Optional[str]]:
    """
    Valida consumo em kWh
    
    Args:
        kwh: Consumo para validar
        
    Returns:
        (is_valid, error_message)
    """
    try:
        consumption = int(kwh)
        
        if consumption < 0:
            return False, "Consumo não pode ser negativo"
        elif consumption > 100000:
            return False, "Consumo muito alto, verifique se está correto"
        else:
            return True, None
            
    except (ValueError, TypeError):
        return False, "Consumo inválido"


def validate_business_hours(dt: datetime) -> tuple[bool, Optional[str]]:
    """
    Valida se datetime está em horário comercial
    
    Args:
        dt: Datetime para validar
        
    Returns:
        (is_valid, error_message)
    """
    # Horário comercial: Segunda a Sexta, 8h às 18h
    # Sábado: 9h às 13h
    
    weekday = dt.weekday()  # 0 = Segunda, 6 = Domingo
    hour = dt.hour
    minute = dt.minute
    
    # Domingo
    if weekday == 6:
        return False, "Não agendamos reuniões aos domingos"
    
    # Segunda a Sexta
    elif weekday < 5:
        if hour < 8 or (hour >= 18 and minute > 0):
            return False, "Horário comercial: Segunda a Sexta das 8h às 18h"
        else:
            return True, None
    
    # Sábado
    else:
        if hour < 9 or (hour >= 13 and minute > 0):
            return False, "Aos sábados atendemos das 9h às 13h"
        else:
            return True, None


def validate_meeting_duration(minutes: int) -> tuple[bool, Optional[str]]:
    """
    Valida duração da reunião
    
    Args:
        minutes: Duração em minutos
        
    Returns:
        (is_valid, error_message)
    """
    if minutes < 30:
        return False, "Reunião deve ter no mínimo 30 minutos"
    elif minutes > 120:
        return False, "Reunião não pode exceder 2 horas"
    else:
        return True, None


def validate_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Valida nome completo
    
    Args:
        name: Nome para validar
        
    Returns:
        (is_valid, error_message)
    """
    # Remove espaços extras
    name = ' '.join(name.split())
    
    if len(name) < 3:
        return False, "Nome muito curto"
    elif len(name) > 100:
        return False, "Nome muito longo"
    elif not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', name):
        return False, "Nome contém caracteres inválidos"
    elif len(name.split()) < 2:
        return False, "Por favor, informe nome e sobrenome"
    else:
        return True, None


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Valida URL
    
    Args:
        url: URL para validar
        
    Returns:
        (is_valid, error_message)
    """
    pattern = r'^https?://[^\s]+$'
    
    if re.match(pattern, url):
        return True, None
    else:
        return False, "URL inválida"


def validate_qualification_score(score: int) -> tuple[bool, Optional[str]]:
    """
    Valida score de qualificação
    
    Args:
        score: Score para validar (0-100)
        
    Returns:
        (is_valid, error_message)
    """
    if 0 <= score <= 100:
        return True, None
    else:
        return False, "Score deve estar entre 0 e 100"


def validate_follow_up_interval(hours: int) -> tuple[bool, Optional[str]]:
    """
    Valida intervalo de follow-up
    
    Args:
        hours: Intervalo em horas
        
    Returns:
        (is_valid, error_message)
    """
    if hours < 0:
        return False, "Intervalo não pode ser negativo"
    elif hours == 0:
        return False, "Intervalo deve ser maior que zero"
    elif hours > 168:  # 1 semana
        return False, "Intervalo máximo é de 1 semana (168 horas)"
    else:
        return True, None


def is_valid_json(data: str) -> bool:
    """
    Verifica se string é JSON válido
    
    Args:
        data: String para verificar
        
    Returns:
        True se for JSON válido
    """
    import json
    try:
        json.loads(data)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitiza entrada de texto removendo caracteres perigosos
    
    Args:
        text: Texto para sanitizar
        max_length: Tamanho máximo permitido
        
    Returns:
        Texto sanitizado
    """
    # Remove caracteres de controle
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    
    # Remove tags HTML/Script
    text = re.sub(r'<[^>]+>', '', text)
    
    # Limita tamanho
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()