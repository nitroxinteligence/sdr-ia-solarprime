# Diagnóstico: Problema de Timezone e Follow-ups

## Data: 08/08/2025

## Análise Detalhada

### 1. Configuração de Timezone

**Descobertas**:

1. **Criação de Follow-ups (webhooks.py)**:
   - Usa `datetime.now()` SEM timezone ao criar timestamp
   - Converte para ISO format: `datetime.now().isoformat()`
   - **PROBLEMA**: datetime naive (sem timezone) sendo salvo no banco

2. **Busca de Follow-ups (followup_executor_service.py)**:
   - Usa `datetime.now(timezone.utc)` - COM timezone UTC
   - Compara com dados salvos: `.lte('scheduled_at', now.isoformat())`
   - **PROBLEMA**: Comparando UTC com datetime naive

3. **Agendamento via time_utils.py**:
   - `get_business_aware_datetime()` usa timezone de São Paulo
   - Retorna datetime COM timezone America/Sao_Paulo
   - Ajusta para horário comercial corretamente

### 2. Problema Principal Identificado

**Inconsistência de Timezone**:

```python
# webhooks.py (ERRADO)
agent_response_timestamp = datetime.now().isoformat()  # Sem timezone!
scheduled_time = scheduled_time.isoformat()  # Com timezone SP

# followup_executor_service.py (CERTO)
now = datetime.now(timezone.utc)  # Com timezone UTC
```

**Resultado**: 
- Follow-up criado com horário de São Paulo (UTC-3)
- Executor busca com horário UTC
- Diferença de 3 horas causa:
  - Follow-ups não são encontrados no horário correto
  - Follow-ups podem ser executados 3 horas antes ou depois

### 3. Fluxo de Execução Atual

1. **Criação do Follow-up**:
   ```python
   # webhooks.py linha 1599
   agent_response_timestamp = datetime.now().isoformat()  # ❌ Sem timezone
   
   # scheduled_time vem de get_business_aware_datetime
   scheduled_time = get_business_aware_datetime(minutes_from_now=30)  # ✅ Com timezone SP
   ```

2. **Busca de Follow-ups Pendentes**:
   ```python
   # followup_executor_service.py linha 113
   now = datetime.now(timezone.utc)  # ✅ UTC
   
   # Query no banco
   .lte('scheduled_at', now.isoformat())  # Comparando UTC com SP
   ```

### 4. Solução Necessária

**Opção 1: Padronizar tudo em UTC** (Recomendado)
- Converter todos os datetimes para UTC antes de salvar
- Manter busca em UTC
- Converter para timezone local apenas na exibição

**Opção 2: Padronizar tudo em São Paulo**
- Usar timezone SP em todos os lugares
- Modificar followup_executor_service para usar SP

### 5. Correções Necessárias

1. **webhooks.py**:
   ```python
   # Linha 1599 - Corrigir para usar timezone
   from datetime import timezone
   agent_response_timestamp = datetime.now(timezone.utc).isoformat()
   ```

2. **followup_executor_service.py**:
   - Já está correto usando UTC
   - Talvez adicionar conversão na comparação se necessário

3. **Validação adicional**:
   - Verificar se `scheduled_time` de `get_business_aware_datetime` está sendo convertido corretamente
   - Garantir que todas as comparações usem o mesmo timezone

### 6. Logs de Debug Adicionados

Já foram adicionados logs de debug em:
- Linha 114: Mostra horário atual da verificação
- Linha 124: Mostra quantidade de follow-ups encontrados
- Linha 134-138: Lista próximos follow-ups agendados
- Linha 142-144: Detalhes dos follow-ups pendentes
- Linha 246-249: Detalhes da execução individual
- Linha 301-304: Detalhes do envio via Evolution
- Linha 312: Resultado do envio

### 7. Teste Recomendado

Para confirmar o problema:

1. Criar um follow-up de teste
2. Verificar no banco de dados o valor de `scheduled_at`
3. Comparar com o horário atual em UTC e São Paulo
4. Ver se há diferença de 3 horas

### 8. Status Atual

- **Timezone na criação**: ❌ Inconsistente (mistura naive e aware)
- **Timezone na busca**: ✅ Consistente (UTC)
- **Logs de debug**: ✅ Implementados
- **Envio via Evolution**: ❓ Precisa verificar se está funcionando

## Próximos Passos

1. Corrigir criação de timestamps em webhooks.py
2. Verificar se Evolution API está recebendo as chamadas
3. Testar fluxo completo com timezone corrigido
4. Monitorar logs para confirmar execução