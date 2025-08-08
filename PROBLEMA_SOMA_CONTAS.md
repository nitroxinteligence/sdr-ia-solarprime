# PROBLEMA IDENTIFICADO: Agente Somando Valores Incorretamente

## Descrição do Problema

O agente está respondendo que "somando as duas contas o gasto mensal é de R$ 8.200,81" quando na verdade só foi detectado um valor de R$ 350,81 na imagem enviada.

### Cálculo Incorreto:
- Valor detectado: R$ 350,81
- Valor mencionado: R$ 8.200,81  
- Diferença (valor inventado): R$ 7.850,00

## Causa Raiz

O problema está no arquivo `app/prompts/prompt-agente.md`, linha 999:

```
- [Recebe 2ª conta] → "Ótimo! Agora com as duas contas somando *R$8.500*, sua economia total seria *R$1.700* mensais!"
```

O agente está seguindo esse exemplo literalmente e sempre respondendo como se fosse uma segunda conta, mesmo quando é a primeira.

## Evidências

1. **Log mostra apenas um valor detectado:**
   ```
   2025-08-08 01:25:49.488 | INFO | ℹ️ 💰 Valor da conta detectado: R$ 350.81
   ```

2. **Resposta do agente:**
   ```
   "Ótimo! Recebi essa outra conta aqui. Somando as duas, o seu gasto mensal é de *R$8.200,81*"
   ```

3. **Não há registro de valor anterior de R$ 7.850 em nenhum lugar do código ou logs**

## Solução Proposta

### 1. Modificar o Prompt (URGENTE)

No arquivo `app/prompts/prompt-agente.md`, adicionar uma regra clara:

```markdown
<rule priority="MÁXIMA" name="valores_reais_apenas">
⚠️ REGRA CRÍTICA: NUNCA INVENTE VALORES!

❌ PROIBIDO:
- Assumir valores de contas anteriores não mencionadas
- Somar com valores imaginários
- Dizer "somando as duas" se só recebeu uma

✅ OBRIGATÓRIO:
- Use APENAS valores explicitamente detectados
- Se recebeu UMA conta, fale de UMA conta
- Se recebeu DUAS contas, então pode somar

EXEMPLOS CORRETOS:
- [Primeira conta R$350] → "Perfeito! Vi aqui R$350,81 na sua conta!"
- [Segunda conta R$500] → "Ótimo! Agora sim, somando as duas: R$850,81 total!"
</rule>
```

### 2. Adicionar Lógica de Detecção no Agente

Modificar a função `_format_context_simple` para rastrear quantas contas foram detectadas na conversa:

```python
def _detect_bill_count(self, message_history):
    """Detecta quantas contas de luz foram analisadas na conversa"""
    bill_count = 0
    for msg in message_history:
        if "Valor da conta detectado" in msg.get('content', ''):
            bill_count += 1
    return bill_count
```

### 3. Validação de Resposta

Adicionar validação antes de enviar a resposta:

```python
def _validate_response(self, response, detected_values):
    """Valida que a resposta não menciona valores não detectados"""
    # Extrair valores mencionados na resposta
    valores_mencionados = re.findall(r'R\$\s*([0-9.,]+)', response)
    
    # Verificar se todos os valores mencionados foram detectados
    for valor in valores_mencionados:
        valor_float = float(valor.replace('.', '').replace(',', '.'))
        if valor_float not in detected_values and valor_float > sum(detected_values):
            return False, f"Resposta menciona valor não detectado: R$ {valor}"
    
    return True, "OK"
```

## Impacto

Este problema pode causar:
1. **Confusão do cliente**: Cliente pode achar que o sistema está com erro
2. **Perda de credibilidade**: Sistema parece não confiável
3. **Cálculos incorretos**: Economia calculada com base em valores errados

## Prioridade: CRÍTICA

Este problema deve ser corrigido imediatamente pois afeta diretamente a experiência do usuário e a confiabilidade do sistema.