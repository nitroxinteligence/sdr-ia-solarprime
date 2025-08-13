# Correção: Remoção do QualificationAgent e Melhoria da Detecção de Calendário

## Data: 08/08/2025

## Problemas Identificados

1. **QualificationAgent Inexistente**
   - Sistema tentava chamar QualificationAgent que foi removido
   - Qualificação agora é 100% feita pelo prompt-agente.md
   - Referência obsoleta no método should_call_sdr_team

2. **Detecção de Calendário Falha**
   - Mensagem "Tem pra amanhã?" não era detectada como solicitação de calendário
   - Sistema não reconhecia palavras temporais isoladas como indicadores de agendamento

## Soluções Implementadas

### 1. Remoção do QualificationAgent

**Arquivo**: `/app/agents/agentic_sdr.py`

**Mudanças**:
- Linha 1032: Removida atribuição `decision_factors["recommended_agent"] = "QualificationAgent"`
- Atualizado comentário para esclarecer que qualificação é feita pelo AgenticSDR
- Mantida lógica de pontuação para leads de alto valor, mas sem delegar

### 2. Melhoria na Detecção de Calendário

**Novas funcionalidades adicionadas**:

1. **Lista de palavras temporais**:
   ```python
   temporal_keywords = [
       "amanhã", "hoje", "semana que vem", "próxima semana", 
       "segunda", "terça", "quarta", "quinta", "sexta",
       "manhã", "tarde", "noite", "horário", "hora",
       "disponível", "disponibilidade", "pode ser", "tem pra"
   ]
   ```

2. **Detecção de perguntas temporais curtas**:
   ```python
   is_short_temporal_question = (
       has_temporal_keyword and 
       len(current_message.split()) <= 5 and
       any(q in current_message.lower() for q in ["?", "tem", "pode", "disponível"])
   )
   ```

3. **Lógica atualizada para incluir perguntas temporais**:
   ```python
   is_real_calendar_request = (
       (calendar_detected or is_short_temporal_question) and 
       not is_simple_greeting and 
       not has_negative_context and 
       not is_followup_message
   )
   ```

## Casos de Teste

### Antes da correção:
- "Tem pra amanhã?" → ❌ Não detectava calendário
- Sistema tentava chamar QualificationAgent inexistente

### Após a correção:
- "Tem pra amanhã?" → ✅ Detecta calendário e chama CalendarAgent
- "Pode ser hoje?" → ✅ Detecta calendário
- "Disponível segunda?" → ✅ Detecta calendário
- "Qual horário?" → ✅ Detecta calendário
- Lead de alto valor → ✅ Qualificação feita pelo AgenticSDR (não delega)

## Resultado Esperado

1. **Detecção de Calendário Melhorada**:
   - Sistema agora reconhece perguntas temporais curtas
   - Detecta interesse em agendamento mesmo sem palavras explícitas como "reunião"
   - CalendarAgent é chamado corretamente

2. **Fluxo de Qualificação Corrigido**:
   - Nenhuma tentativa de chamar QualificationAgent
   - Qualificação 100% feita pelo AgenticSDR via prompt-agente.md
   - Sistema mais estável e sem erros de agente inexistente

## Validação

Para validar as correções:

1. Testar com mensagens temporais curtas:
   - "Tem pra amanhã?"
   - "Pode ser hoje?"
   - "Horário disponível?"

2. Verificar logs para confirmar:
   - CalendarAgent sendo chamado
   - Nenhuma menção a QualificationAgent
   - Detecção correta de intenção de agendamento

3. Testar leads de alto valor:
   - Verificar que qualificação ocorre sem delegação
   - Confirmar que AgenticSDR processa diretamente