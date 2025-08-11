# Correção: Falsos Positivos na Detecção de Termos Proibidos

## Problema Identificado

As seguintes mensagens legítimas estavam sendo bloqueadas incorretamente:

1. "Prazer, Mateus! Então vamos lá... Hoje na SolarPrime nós temos 4 soluções energéticas: instalação de usina própria, aluguel de lote para instalação de usina própria, compra de energia com desconto e usina de investimento. Qual desses modelos seria do seu interesse? Ou seria outra opção?"

2. "Oii Wanessa, tudo bem? Acredito que você enviou a mensagem para o contato errado, aqui é a Helen Vieira. Sou consultora especialista da SolarPrime aqui em Recife, mas desejo muito sucesso na sua seleção para a Stint Edu! Se um dia precisar de qualquer ajuda com projetos de energia solar, estou por aqui."

### Causa Raiz

A verificação de termos proibidos estava usando `term in text`, que encontra substrings. Isso causava falsos positivos:

- "rg" era encontrado em "ene**rg**éticas" e "ene**rg**ia"
- Potencialmente "conta bancária" poderia ser encontrado em palavras como "des**conta**r"

## Solução Implementada

Alterado o método de detecção para usar expressões regulares com limites de palavra (`\b`), garantindo que apenas palavras completas sejam detectadas.

### Código Anterior (com problema)
```python
response_lower = final_response.lower()
contains_forbidden = any(term in response_lower for term in forbidden_terms)
```

### Código Corrigido
```python
response_lower = final_response.lower()

# CORREÇÃO: Usar regex para detectar palavras completas, não substrings
import re
contains_forbidden = False
for term in forbidden_terms:
    # \b marca limites de palavra para evitar falsos positivos
    pattern = r'\b' + re.escape(term) + r'\b'
    if re.search(pattern, response_lower):
        contains_forbidden = True
        break
```

## Arquivos Modificados

1. `/app/api/webhooks.py` - Função `extract_final_response()`
2. `/app/agents/agentic_sdr.py` - Método `process_message()`

## Testes Realizados

### Mensagens que agora passam corretamente:
- ✅ Mensagens sobre "energia" não são mais bloqueadas
- ✅ Mensagens com "energéticas" não são mais bloqueadas

### Mensagens que continuam sendo bloqueadas (correto):
- ❌ "Por favor, me envie seu CPF para cadastro"
- ❌ "Preciso do seu RG e identidade"
- ❌ "Envie seus dados bancários e senha"

## Impacto

Esta correção elimina os falsos positivos mantendo a segurança contra solicitações reais de dados sensíveis. O sistema agora diferencia corretamente entre:
- "energia" (permitido) vs "rg" (bloqueado)
- "desconto" (permitido) vs "conta bancária" (bloqueado)

## Data da Correção

08 de agosto de 2025