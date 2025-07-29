# Correção de Conversão de Valores Monetários

## Problema Identificado

O sistema estava falhando ao tentar converter valores monetários brasileiros para float, gerando o erro:
```
could not convert string to float: 'R$ 800'
```

### Causa Raiz:
O código estava tentando converter diretamente strings como "R$ 800" para float usando `float()`, mas a função não consegue processar:
- Símbolo de moeda (R$)
- Espaços
- Formato brasileiro com vírgula como decimal
- Pontos como separador de milhar

## Solução Implementada

### 1. Criação do Módulo `utils/currency_parser.py`

Criamos um módulo especializado para conversão de valores monetários brasileiros:

```python
def parse_brazilian_currency(value: Union[str, float, int]) -> Optional[float]:
    """
    Converte valor monetário brasileiro para float.
    
    Suporta formatos como:
    - "R$ 800"
    - "R$ 1.500,00"
    - "1500,00"
    - "1.500"
    - 800 (int)
    - 800.0 (float)
    """
```

### 2. Funcionalidades do Parser

- **Remoção de símbolos**: Remove "R$" e espaços
- **Formato brasileiro**: Detecta vírgula como decimal
- **Separador de milhar**: Remove pontos quando são separadores
- **Validação**: Não aceita valores negativos
- **Robustez**: Trata None, strings vazias e valores inválidos

### 3. Atualização do `agents/sdr_agent.py`

Substituímos o código problemático:

**Antes:**
```python
lead_updates["bill_value"] = float(lead_info["bill_value"])
```

**Depois:**
```python
parsed_value = parse_brazilian_currency(lead_info["bill_value"])
if parsed_value is not None:
    lead_updates["bill_value"] = parsed_value
```

### 4. Testes Implementados

Criamos testes abrangentes em `tests/unit/test_currency_parser.py`:
- Valores simples: "R$ 800"
- Com decimais: "R$ 1.500,00"
- Sem símbolo: "800"
- Casos extremos: None, "", valores inválidos

## Resultados

✅ **Todos os 11 testes passaram com sucesso**
✅ **O erro não ocorrerá mais para valores monetários brasileiros**
✅ **Suporte completo para diferentes formatos de entrada**

## Uso da Função

### Importação:
```python
from utils.currency_parser import parse_brazilian_currency, format_brazilian_currency
```

### Conversão:
```python
# Converter string para float
value = parse_brazilian_currency("R$ 800")  # Retorna: 800.0

# Formatar float para moeda
formatted = format_brazilian_currency(800)  # Retorna: "R$ 800,00"
```

## Benefícios

1. **Robustez**: Trata diversos formatos de entrada
2. **Reutilização**: Função centralizada para todo o sistema
3. **Manutenibilidade**: Fácil adicionar novos formatos
4. **Testabilidade**: Totalmente coberto por testes unitários
5. **Logs melhorados**: Mensagens de erro mais informativas