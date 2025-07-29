"""
Testes unitários para o currency_parser
"""

import pytest
from utils.currency_parser import parse_brazilian_currency, format_brazilian_currency


class TestParseBrazilianCurrency:
    """Testes para a função parse_brazilian_currency"""
    
    def test_parse_simple_currency(self):
        """Testa conversão de valores simples com R$"""
        assert parse_brazilian_currency("R$ 800") == 800.0
        assert parse_brazilian_currency("R$ 500") == 500.0
        assert parse_brazilian_currency("R$ 1500") == 1500.0
    
    def test_parse_with_decimal_comma(self):
        """Testa valores com vírgula como decimal"""
        assert parse_brazilian_currency("R$ 800,00") == 800.0
        assert parse_brazilian_currency("R$ 1.500,00") == 1500.0
        assert parse_brazilian_currency("R$ 1.234,56") == 1234.56
    
    def test_parse_with_thousand_separator(self):
        """Testa valores com ponto como separador de milhar"""
        assert parse_brazilian_currency("R$ 1.500") == 1500.0
        assert parse_brazilian_currency("R$ 10.000") == 10000.0
        assert parse_brazilian_currency("R$ 1.234.567") == 1234567.0
    
    def test_parse_without_currency_symbol(self):
        """Testa valores sem símbolo de moeda"""
        assert parse_brazilian_currency("800") == 800.0
        assert parse_brazilian_currency("1500,00") == 1500.0
        assert parse_brazilian_currency("1.500") == 1500.0
    
    def test_parse_numeric_types(self):
        """Testa entrada de tipos numéricos"""
        assert parse_brazilian_currency(800) == 800.0
        assert parse_brazilian_currency(800.0) == 800.0
        assert parse_brazilian_currency(1500.50) == 1500.50
    
    def test_parse_edge_cases(self):
        """Testa casos extremos"""
        assert parse_brazilian_currency(None) is None
        assert parse_brazilian_currency("") is None
        assert parse_brazilian_currency("R$ ") is None
        assert parse_brazilian_currency("abc") is None
        assert parse_brazilian_currency("R$ -100") is None  # Valor negativo
    
    def test_parse_with_spaces(self):
        """Testa valores com espaços extras"""
        assert parse_brazilian_currency("  R$ 800  ") == 800.0
        assert parse_brazilian_currency("R$   800") == 800.0
        assert parse_brazilian_currency("R$ 1 500") == 1500.0


class TestFormatBrazilianCurrency:
    """Testes para a função format_brazilian_currency"""
    
    def test_format_simple_values(self):
        """Testa formatação de valores simples"""
        assert format_brazilian_currency(800) == "R$ 800,00"
        assert format_brazilian_currency(1500) == "R$ 1.500,00"
        assert format_brazilian_currency(1234.56) == "R$ 1.234,56"
    
    def test_format_large_values(self):
        """Testa formatação de valores grandes"""
        assert format_brazilian_currency(10000) == "R$ 10.000,00"
        assert format_brazilian_currency(1234567.89) == "R$ 1.234.567,89"
        assert format_brazilian_currency(1000000) == "R$ 1.000.000,00"
    
    def test_format_decimal_values(self):
        """Testa formatação com casas decimais"""
        assert format_brazilian_currency(800.50) == "R$ 800,50"
        assert format_brazilian_currency(1234.5) == "R$ 1.234,50"
        assert format_brazilian_currency(0.99) == "R$ 0,99"


# Teste de integração simulando o caso real
def test_real_world_scenario():
    """Testa o cenário real que causou o erro"""
    # Simular o valor que veio do WhatsApp
    bill_value_from_user = "R$ 800"
    
    # Converter usando a função
    parsed_value = parse_brazilian_currency(bill_value_from_user)
    
    # Verificar que foi convertido corretamente
    assert parsed_value == 800.0
    assert isinstance(parsed_value, float)
    
    # Testar outros formatos que podem vir do usuário
    test_cases = [
        ("800 reais", 800.0),
        ("minha conta é 800", 800.0),
        ("R$ 1.500,00", 1500.0),
        ("1500", 1500.0),
        ("conta de 800 reais por mes", 800.0)  # Caso com texto extra
    ]
    
    for input_text, expected in test_cases:
        # Extrair apenas a parte numérica (simulando o que o agente faria)
        import re
        match = re.search(r'R?\$?\s*(\d+\.?\d*,?\d*)', input_text)
        if match:
            value_str = "R$ " + match.group(1) if not input_text.startswith("R$") else match.group(0)
            result = parse_brazilian_currency(value_str)
            assert result == expected, f"Falhou para '{input_text}': esperado {expected}, obtido {result}"