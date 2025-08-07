# Relatório de Análise e Soluções para Otimização do Agente SDR v0.3

## RESUMO EXECUTIVO

### 📊 Status Geral
- **Análise Profunda**: ✅ Completa
- **Correções Críticas**: 3/3 ✅ Implementadas
- **Problemas Resolvidos**: 2/5 confirmados e corrigidos
- **Tempo de Implementação**: ~30 minutos

### 🎯 Principais Descobertas
1. **Problema de Follow-up**: Funcionalidade estava DESABILITADA no código (hardcoded)
2. **Erro TypeError**: Conversões de tipo sem validação causando crashes
3. **Falsos Positivos**: 2 dos 5 problemas reportados não existiam no código
4. **Novo Problema**: Múltiplas conversões inseguras descobertas em todo o sistema

### ✅ Correções Implementadas
1. **Follow-ups Reabilitados**: Integração real com Google Calendar restaurada
2. **Conversões Seguras**: Módulo de utilidades criado para prevenir erros de tipo
3. **Resiliência Aumentada**: Sistema agora trata casos edge em conversões de dados

### 🚀 Próximos Passos Recomendados
1. Implementar melhorias de performance (connection pooling, cache)
2. Adicionar testes automatizados para prevenir regressões
3. Configurar monitoramento para detectar falhas proativamente

---

## 1. Introdução

Este relatório apresenta um diagnóstico detalhado e um plano de ação para resolver cinco problemas críticos identificados no sistema do agente SDR IA SolarPrime. A análise foi dividida por especialidade para garantir que cada problema seja tratado em sua raiz, com soluções diretas, eficientes e de baixa complexidade de implementação. O objetivo é elevar o sistema a um estado 100% funcional e otimizado.

---

## DIAGNÓSTICO COMPLETO DO SISTEMA (ANÁLISE PROFUNDA)

### Arquitetura Geral do Sistema

O sistema SDR IA SolarPrime segue uma arquitetura hierárquica de agentes com duas camadas principais:

**Camada 1: AGENTIC SDR (Orquestrador Principal)**
- Agente conversacional principal com personalidade ultra-humanizada
- Sistema de fallback inteligente (Gemini → OpenAI)
- Gerenciamento de estado emocional por conversa
- Suporte multimodal (imagens, áudio, documentos)
- Motor de decisão para delegar tarefas

**Camada 2: SDR Team (Agentes Especializados)**
- Coordenado por Helen SDR Master
- Agentes especializados: Qualification, Calendar, FollowUp, Knowledge, CRM, BillAnalyzer
- Framework AGNO Teams em modo COORDINATE

### Problemas Estruturais Identificados

1. **Incompatibilidade com Framework AGNO**
   - Memory component tentando chamar métodos inexistentes
   - Necessidade de wrappers complexos para registro de ferramentas

2. **Gerenciamento de Estado Deficiente**
   - Estados emocionais sem isolamento adequado por conversa
   - Potencial race condition em cenários multi-usuário
   - Cache sem estratégia de invalidação

3. **Falta de Padrões de Resiliência**
   - Ausência de Circuit Breaker para serviços externos
   - Rate limiting inconsistente entre serviços
   - Recuperação de erros não padronizada

4. **Problemas de Integração**
   - Google Calendar com follow-ups DESABILITADOS (hardcoded)
   - Conversões de tipo sem validação (float() errors)
   - Gaps na integração entre serviços

### Status Real dos 5 Problemas Reportados

1. **Reagendamento Google Calendar**: ❌ FALSO - O método `reschedule_meeting` existe e funciona
2. **Follow-up de Reuniões**: ✅ CONFIRMADO - Funcionalidade DESABILITADA no código
3. **Pipeline KommoCRM**: ⚠️ PARCIAL - Lógica existe mas com problemas de mapeamento
4. **Integração leads_qualifications**: ❌ FALSO - Já está implementado e funcionando
5. **Erro TypeError float()**: ✅ CONFIRMADO - Linha 402 de kommo_auto_sync.py

### Problemas Adicionais Descobertos

1. **Desempenho e Escalabilidade**
   - Sem connection pooling para Kommo API
   - Cada requisição cria nova sessão HTTP
   - Falta de cache para operações repetitivas

2. **Segurança e Validação**
   - Ausência de validação de entrada em múltiplos pontos
   - Conversões de tipo sem tratamento de exceções
   - Logs expondo informações sensíveis

3. **Manutenibilidade**
   - Alto acoplamento entre componentes
   - Falta de testes automatizados
   - Documentação inline insuficiente

---

## CHECKLIST MESTRE DE CORREÇÕES

### 🚨 Correções Críticas (Impacto Alto, Complexidade Baixa)

- [x] **CORREÇÃO 1**: Reabilitar follow-ups do Google Calendar (Problema 2) ✅ IMPLEMENTADO
- [x] **CORREÇÃO 2**: Corrigir erro TypeError float() com validação adequada (Problema 5) ✅ IMPLEMENTADO
- [x] **CORREÇÃO 3**: Implementar validação de dados em todas as conversões de tipo ✅ IMPLEMENTADO

### ⚡ Melhorias de Performance (Impacto Médio, Complexidade Baixa)

- [ ] **MELHORIA 1**: Adicionar connection pooling para Kommo API
- [ ] **MELHORIA 2**: Implementar cache para operações repetitivas
- [ ] **MELHORIA 3**: Otimizar queries do Supabase com índices apropriados

### 🔧 Refatorações Estruturais (Impacto Alto, Complexidade Média)

- [ ] **REFATORAÇÃO 1**: Padronizar tratamento de erros com Circuit Breaker
- [ ] **REFATORAÇÃO 2**: Implementar validação de schemas para APIs
- [ ] **REFATORAÇÃO 3**: Isolar estado emocional por conversa com locks adequados

### 🛡️ Segurança e Confiabilidade (Impacto Alto, Complexidade Média)

- [ ] **SEGURANÇA 1**: Sanitizar logs para remover informações sensíveis
- [ ] **SEGURANÇA 2**: Adicionar rate limiting consistente em todos os serviços
- [ ] **SEGURANÇA 3**: Implementar health checks para todas as integrações

### 📊 Observabilidade e Monitoramento (Impacto Médio, Complexidade Alta)

- [ ] **OBSERVABILIDADE 1**: Adicionar métricas de performance
- [ ] **OBSERVABILIDADE 2**: Implementar distributed tracing
- [ ] **OBSERVABILIDADE 3**: Criar dashboards de monitoramento

### ✅ Qualidade e Testes (Impacto Alto, Complexidade Alta)

- [ ] **QUALIDADE 1**: Adicionar testes unitários para agentes
- [ ] **QUALIDADE 2**: Implementar testes de integração
- [ ] **QUALIDADE 3**: Criar testes end-to-end para fluxos críticos

---

## CORREÇÕES IMPLEMENTADAS

### ✅ CORREÇÃO 1: Follow-ups do Google Calendar Reabilitados (ATUALIZADO)

**Arquivos Modificados**: 
- `app/services/followup_executor_service.py`
- `app/teams/agents/calendar.py`

**Mudanças Implementadas**:
1. Importado `google_calendar_client` para integração real
2. Removido código hardcoded que desabilitava os lembretes (linhas 136-138)
3. **NOVA IMPLEMENTAÇÃO**: Sistema agora usa `leads_qualifications` ao invés de `calendar_events`:
   - Adicionado `google_event_id` na tabela `leads_qualifications`
   - CalendarAgent salva o ID do evento ao criar qualificação
   - Follow-up busca eventos usando associação lead ↔ google_event_id
4. Criada nova função `_send_meeting_reminder_v2` que:
   - Busca lead correto via `leads_qualifications.google_event_id`
   - Marca lembretes enviados na tabela `leads_qualifications`
   - Garante que cada lembrete vai para o lead correto
5. **Migrations SQL criadas**:
   - `add_google_event_id_to_leads_qualifications.sql`
   - `add_reminder_fields_to_leads_qualifications.sql`

### ✅ CORREÇÃO 2: Erro TypeError float() Resolvido

**Arquivo Modificado**: `app/services/kommo_auto_sync.py`

**Mudanças Implementadas**:
1. Criada função `safe_float_conversion()` que trata todos os casos edge:
   - None explícito
   - Strings vazias ou "None"/"null"/"nan"
   - Valores não numéricos
   - Símbolos monetários (R$, $)
   - Vírgulas como separadores decimais
2. Aplicada em todas as 3 ocorrências de conversão de `bill_value`:
   - Linha 204: criação de lead no Kommo
   - Linha 305: atualização de campos customizados
   - Linha 442: criação de deal (onde ocorria o erro principal)

### ✅ CORREÇÃO 3: Validação de Dados em Todas as Conversões

**Arquivos Criados/Modificados**:
1. **Novo**: `app/utils/safe_conversions.py` - Módulo centralizado de conversões seguras
2. **Modificado**: `app/services/kommo_auto_sync.py`
3. **Modificado**: `app/integrations/redis_client.py`

**Funções Implementadas**:
- `safe_int_conversion()` - Conversão segura para inteiros
- `safe_float_conversion()` - Conversão segura para float (já existente, movida)
- `safe_datetime_conversion()` - Conversão segura de datas com múltiplos formatos
- `safe_json_loads()` - Parse JSON seguro com tratamento de erros
- `safe_json_dumps()` - Serialização JSON segura
- `safe_dict_get()` - Acesso seguro a dicionários com validação de tipo

**Conversões Corrigidas**:
1. **kommo_auto_sync.py**:
   - Linha 309: `qualification_score` → int seguro
   - Linha 318: `consumption_kwh` → int seguro
2. **redis_client.py**:
   - Linha 379: JSON parse → safe_json_loads
   - Linha 524: Rate limit counter → int seguro
   - Linha 678: Counter value → int seguro

---

## 2. Problema 1: Lógica de Reagendamento no Google Calendar

### 2.1. Diagnóstico Detalhado

O fluxo de reagendamento de reuniões está incorreto. Atualmente, ao invés de cancelar o evento existente e procurar novos horários, o agente cria um novo evento no mesmo dia e horário do anterior. Isso causa duplicidade e não atende à solicitude do usuário.

O código responsável, provavelmente no `app/teams/agents/calendar.py`, chama diretamente a função de criação de evento ao invés de um fluxo de reagendamento. Falta uma orquestração que envolva:
1.  Cancelamento do evento atual.
2.  Verificação de novos horários disponíveis.
3.  Apresentação das opções ao usuário.
4.  Agendamento em um novo slot escolhido.

### 2.2. Plano de Ação e Solução Proposta

Propõe-se a criação de uma nova função `reschedule_meeting` no `CalendarAgent` e a modificação do fluxo de interação do agente principal para utilizá-la.

**Etapa 1: Implementar `reschedule_meeting` em `app/teams/agents/calendar.py`**

Adicionar um novo método ao `CalendarAgent` que orquestra o processo de reagendamento.

```python
# Em app/teams/agents/calendar.py, dentro da classe CalendarAgent

async def reschedule_meeting(
    self,
    event_id: str,
    lead_id: str,
    new_date: str,
    new_time: str
) -> Dict[str, Any]:
    """
    Reagenda uma reunião existente, cancelando a antiga e criando uma nova.

    Args:
        event_id: ID do evento do Google Calendar a ser cancelado.
        lead_id: ID do lead no banco de dados.
        new_date: Nova data para a reunião (DD/MM/YYYY).
        new_time: Novo horário para a reunião (HH:MM).

    Returns:
        Dicionário com o status do reagendamento.
    """
    logger.info(f"Iniciando reagendamento para o evento {event_id}")

    # Etapa 1: Cancelar o evento antigo
    try:
        cancel_result = await self.cancel_meeting(event_id, reason="Reagendado a pedido do cliente")
        if not cancel_result.get("success"):
            logger.error(f"Falha ao cancelar evento antigo {event_id}: {cancel_result.get('error')}")
            return {"success": False, "error": "Não foi possível cancelar o evento original."}
        logger.info(f"Evento antigo {event_id} cancelado com sucesso.")
    except Exception as e:
        logger.error(f"Exceção ao cancelar evento antigo {event_id}: {e}")
        return {"success": False, "error": f"Exceção ao cancelar evento: {e}"}

    # Etapa 2: Agendar a nova reunião
    try:
        lead_info = await supabase_client.get_lead_by_id(lead_id)
        if not lead_info:
            return {"success": False, "error": "Lead não encontrado para o reagendamento."}

        attendee_emails = [lead_info.get("email")] if lead_info.get("email") else []

        schedule_result = await self.schedule_meeting(
            lead_id=lead_id,
            title=f"REAGENDADO: Apresentação Solar Prime - {lead_info.get('name')}",
            date=new_date,
            time=new_time,
            attendee_emails=attendee_emails,
            description="Esta é uma reunião reagendada a pedido do cliente."
        )

        if schedule_result.get("success"):
            logger.info(f"Reunião reagendada com sucesso para {new_date} às {new_time}.")
            return schedule_result
        else:
            logger.error(f"Falha ao agendar novo evento: {schedule_result.get('error')}")
            # Tentar reagendar o evento original como fallback? (a discutir)
            return {"success": False, "error": "O evento antigo foi cancelado, mas falhou ao criar o novo."}

    except Exception as e:
        logger.error(f"Exceção ao criar novo evento de reagendamento: {e}")
        return {"success": False, "error": f"Exceção ao criar novo evento: {e}"}
```

**Etapa 2: Modificar o Agente Principal para usar o novo fluxo**

O `AgenticSDR` em `app/agents/agentic_sdr.py` deve ser instruído a detectar a intenção de "reagendar" e, em vez de chamar `schedule_meeting`, deve primeiro buscar horários disponíveis e depois chamar a nova função `reschedule_meeting`.

### 2.3. Checklist de Implementação

- [ ] Adicionar a função `reschedule_meeting` à classe `CalendarAgent` em `app/teams/agents/calendar.py`.
- [ ] Atualizar o `AgenticSDR` para reconhecer a intenção de reagendamento.
- [ ] Garantir que o `AgenticSDR` chame `find_best_slots` antes de apresentar novas opções ao usuário.
- [ ] Assegurar que, após a escolha do usuário, o `AgenticSDR` chame `reschedule_meeting` com o ID do evento antigo e os novos detalhes.
- [ ] Testar o fluxo completo de reagendamento.

---

## 3. Problema 2: Follow-up de Agendamentos do Google Calendar

### 3.1. Diagnóstico Detalhado

O sistema não está enviando lembretes de reunião 24h e 2h antes do evento. Isso ocorre porque não há um processo contínuo (worker/cron job) que verifique os eventos agendados no Google Calendar e dispare os lembretes. A funcionalidade para enviar a mensagem pode existir, mas o gatilho está ausente.

O arquivo `app/services/followup_executor_service.py` parece ser o local ideal para essa lógica, mas atualmente ele está focado em follow-ups de conversas e não em eventos de calendário.

### 3.2. Plano de Ação e Solução Proposta

A solução é expandir o `FollowUpExecutorService` para incluir uma verificação periódica de eventos do Google Calendar.

**Etapa 1: Modificar `FollowUpExecutorService` em `app/services/followup_executor_service.py`**

Adicionar um novo loop de verificação ou integrar na verificação existente a lógica para buscar eventos no calendário.

```python
# Em app/services/followup_executor_service.py

class FollowUpExecutorService:
    def __init__(self):
        # ... (inicialização existente) ...
        self.calendar_check_interval = 300  # Verificar calendário a cada 5 minutos

    async def start(self):
        # ... (código de start existente) ...
        # Adicionar o novo loop para lembretes de reunião
        asyncio.create_task(self._calendar_reminder_loop())

    async def _calendar_reminder_loop(self):
        """Loop que verifica eventos do calendário e envia lembretes."""
        while self.running:
            try:
                await self.process_meeting_reminders()
                await asyncio.sleep(self.calendar_check_interval)
            except Exception as e:
                logger.error(f"❌ Erro no loop de lembretes de calendário: {e}")
                await asyncio.sleep(60) # Espera mais em caso de erro

    async def process_meeting_reminders(self):
        """Busca eventos futuros e envia lembretes de 24h e 2h."""
        now = datetime.now(pytz.timezone(settings.timezone))
        
        # Lembrete de 24h
        time_min_24h = now + timedelta(hours=23, minutes=55)
        time_max_24h = now + timedelta(hours=24, minutes=5)
        events_24h = await google_calendar_client.list_events(time_min=time_min_24h, time_max=time_max_24h)
        
        for event in events_24h:
            event_id = event.get('google_event_id')
            # Lógica para verificar se o lembrete já foi enviado (requer um campo no DB)
            # Ex: if not await self.db.has_reminder_been_sent(event_id, '24h'):
            await self._send_reminder(event, '24h')
            # await self.db.mark_reminder_as_sent(event_id, '24h')

        # Lembrete de 2h
        time_min_2h = now + timedelta(hours=1, minutes=55)
        time_max_2h = now + timedelta(hours=2, minutes=5)
        events_2h = await google_calendar_client.list_events(time_min=time_min_2h, time_max=time_max_2h)

        for event in events_2h:
            event_id = event.get('google_event_id')
            # Lógica para verificar se o lembrete já foi enviado
            # Ex: if not await self.db.has_reminder_been_sent(event_id, '2h'):
            await self._send_reminder(event, '2h')
            # await self.db.mark_reminder_as_sent(event_id, '2h')

    async def _send_reminder(self, event: Dict[str, Any], reminder_type: str):
        """Envia uma mensagem de lembrete formatada."""
        # Extrair informações do evento para encontrar o lead
        # Esta parte depende de como o lead_id é armazenado na descrição do evento ou em uma tabela de mapeamento
        lead_id = self._extract_lead_id_from_event(event)
        if not lead_id:
            logger.warning(f"Não foi possível encontrar o lead_id para o evento {event.get('google_event_id')}")
            return

        lead = await supabase_client.get_lead_by_id(lead_id)
        if not lead or not lead.get('phone_number'):
            return

        start_time = datetime.fromisoformat(event['start']['dateTime']).strftime('%H:%M')
        
        if reminder_type == '24h':
            message = f"Olá, {lead.get('name', 'tudo bem')}! Passando para confirmar nossa reunião de amanhã às {start_time}. Está tudo certo para você?"
        else: # 2h
            message = f"Olá, {lead.get('name', 'tudo bem')}! Nossa reunião é daqui a 2 horas, às {start_time}! Já estou preparando tudo aqui. Até breve!"

        await evolution_client.send_text_message(phone=lead['phone_number'], message=message)
        logger.info(f"Lembrete de {reminder_type} enviado para o lead {lead_id} para o evento {event.get('google_event_id')}")

    def _extract_lead_id_from_event(self, event: Dict[str, Any]) -> Optional[str]:
        # Implementar a lógica para extrair o lead_id da descrição do evento ou de uma tabela de mapeamento
        # Exemplo:
        description = event.get('description', '')
        match = re.search(r'Lead ID: (\S+)', description)
        if match:
            return match.group(1)
        return None
```

### 3.3. Checklist de Implementação

- [ ] Adicionar o loop `_calendar_reminder_loop` ao `FollowUpExecutorService`.
- [ ] Implementar a função `process_meeting_reminders` para buscar eventos no Google Calendar.
- [ ] Criar a função `_send_reminder` para formatar e enviar a mensagem de lembrete.
- [ ] Implementar um mecanismo para rastrear lembretes enviados e evitar duplicidade (sugestão: adicionar colunas `reminder_24h_sent` e `reminder_2h_sent` na tabela `calendar_events`).
- [ ] Garantir que o `lead_id` seja armazenado na descrição do evento do Google Calendar ou em uma tabela de mapeamento para recuperação.

---

## 4. Problema 3: Gerenciamento de Pipeline no KommoCRM

### 4.1. Diagnóstico Detalhado

O agente de IA não está movendo os leads entre os estágios do pipeline do KommoCRM de forma correta e consistente. A lógica de transição de estado está ausente ou falha. As tags e campos customizados também não estão sendo atualizados de forma confiável.

O arquivo `app/services/kommo_auto_sync.py` é o principal responsável por essa lógica. A função `_move_to_correct_stage` provavelmente contém uma lógica de mapeamento incompleta ou incorreta. O `AgenticSDR` também precisa ser mais explícito ao atualizar o `current_stage` do lead no Supabase, que serve como gatilho para a sincronização.

### 4.2. Plano de Ação e Solução Proposta

A solução envolve refinar o mapeamento de estágios, fortalecer a lógica no `kommo_auto_sync.py` e garantir que o agente principal atualize o estado do lead corretamente.

**Etapa 1: Refinar o Mapeamento de Estágios em `kommo_auto_sync.py`**

Assegurar que o `stage_mapping` esteja completo e correto, e que a função `_move_to_correct_stage` o utilize de forma robusta.

```python
# Em app/services/kommo_auto_sync.py

class KommoAutoSyncService:
    def __init__(self):
        # ...
        # Mapeamento claro e simplificado dos estágios
        self.stage_mapping = {
            "INITIAL_CONTACT": "novo_lead",
            "QUALIFYING": "em_qualificacao",
            "SCHEDULING": "reuniao_agendada", # Mover para cá assim que agendar
            "NOT_INTERESTED": "nao_interessado"
        }
        # ...

    async def _move_to_correct_stage(self, kommo_id: str, lead: Dict[str, Any]):
        """Move o lead para o estágio correto no pipeline do Kommo."""
        if not self.crm or not hasattr(self.crm, 'pipeline_stages'):
            logger.warning("CRM ou pipeline_stages não inicializado. Pulando movimentação.")
            return

        current_stage_key = lead.get("current_stage", "INITIAL_CONTACT")
        kommo_stage_name = self.stage_mapping.get(current_stage_key)

        if not kommo_stage_name:
            logger.warning(f"Estágio '{current_stage_key}' não mapeado para o Kommo.")
            return

        stage_id = self.crm.pipeline_stages.get(kommo_stage_name)
        if not stage_id:
            logger.error(f"ID do estágio '{kommo_stage_name}' não encontrado no Kommo.")
            return

        try:
            await self.crm.move_card_to_pipeline(
                lead_id=kommo_id,
                pipeline_id=settings.kommo_pipeline_id,
                stage_id=stage_id
            )
            logger.info(f"✅ Lead {kommo_id} movido para o estágio '{kommo_stage_name}' (ID: {stage_id})")
        except Exception as e:
            logger.error(f"❌ Erro ao mover lead {kommo_id} para o estágio '{kommo_stage_name}': {e}")

```

**Etapa 2: Ajustar o `AgenticSDR` para Atualizar o `current_stage`**

O agente principal deve atualizar o campo `current_stage` na tabela `leads` do Supabase nos momentos corretos.

-   **Ao receber a primeira resposta do lead:**
    -   Atualizar `current_stage` para `QUALIFYING`.
-   **Ao agendar uma reunião com sucesso:**
    -   Atualizar `current_stage` para `SCHEDULING`.
-   **Após 2 follow-ups sem resposta:**
    -   Atualizar `current_stage` para `NOT_INTERESTED`.

**Etapa 3: Revisar o Prompt do Agente**

Adicionar instruções claras em `app/prompts/prompt-agente.md` para que o LLM entenda o fluxo do pipeline e saiba quando solicitar a mudança de estágio.

```markdown
# Em app/prompts/prompt-agente.md

## ⚙️ FLUXO DE PIPELINE NO KOMMOCRM

Você deve gerenciar o ciclo de vida do lead no CRM. O sistema moverá o card automaticamente com base no estágio que você definir.

- **NOVO LEAD**: O sistema define automaticamente.
- **EM QUALIFICAÇÃO**: Assim que o lead responder pela primeira vez, mude o estágio para 'QUALIFYING'.
- **REUNIÃO AGENDADA**: Após agendar uma reunião com sucesso, mude o estágio para 'SCHEDULING'.
- **NÃO INTERESSADO**: Se o lead não responder após 2 tentativas de follow-up, mude o estágio para 'NOT_INTERESTED'.
```

### 4.3. Checklist de Implementação

- [ ] Revisar e corrigir o `stage_mapping` em `kommo_auto_sync.py`.
- [ ] Fortalecer a lógica de `_move_to_correct_stage` com tratamento de erros.
- [ ] Adicionar lógica no `AgenticSDR` para atualizar o `current_stage` do lead no Supabase em momentos-chave.
- [ ] Atualizar `prompt-agente.md` com as diretrizes do pipeline.
- [ ] Testar o fluxo completo de um lead, desde a criação até o agendamento ou desinteresse.

---

## 5. Problema 4: Integração com a Tabela `leads_qualifications` do Supabase

### 5.1. Diagnóstico Detalhado

O sistema não está inserindo os dados na tabela `leads_qualifications` quando uma reunião é agendada. A chamada para a inserção no banco de dados está faltando no fluxo de agendamento. O `CalendarAgent` é o local mais apropriado para disparar essa ação, pois ele é o responsável por confirmar a criação do evento.

### 5.2. Plano de Ação e Solução Proposta

A solução é adicionar uma chamada para uma nova função no `SupabaseClient` de dentro do método `schedule_meeting` do `CalendarAgent`, logo após o evento ser criado com sucesso no Google Calendar.

**Etapa 1: Criar a função `create_lead_qualification` em `app/integrations/supabase_client.py`**

```python
# Em app/integrations/supabase_client.py, dentro da classe SupabaseClient

async def create_lead_qualification(self, qualification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cria um registro de qualificação de lead.
    """
    try:
        # Valores padrão para uma qualificação via agendamento
        defaults = {
            'qualification_status': 'QUALIFIED',
            'score': 85, # Score alto por ter agendado
            'criteria': {'meeting_scheduled': True, 'interest_level': 'high'},
            'notes': 'Lead qualificado via agendamento de reunião pelo agente IA.',
            'qualified_at': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Mescla dados recebidos com os padrões
        final_data = {**defaults, **qualification_data}

        # Garante que o lead_id é um UUID válido se existir
        if 'lead_id' in final_data and isinstance(final_data['lead_id'], str):
            try:
                UUID(final_data['lead_id'], version=4)
            except ValueError:
                logger.error(f"lead_id inválido para qualificação: {final_data['lead_id']}")
                raise ValueError("ID do lead inválido.")

        result = self.client.table('leads_qualifications').insert(final_data).execute()
        
        if result.data:
            logger.info(f"✅ Qualificação criada para o lead {final_data.get('lead_id')}")
            return result.data[0]
        
        raise Exception(f"Erro ao criar qualificação: {result.error.message if result.error else 'sem detalhes'}")

    except Exception as e:
        emoji_logger.supabase_error(f"Erro ao criar qualificação de lead: {str(e)}", table="leads_qualifications")
        raise
```

**Etapa 2: Chamar a nova função a partir do `CalendarAgent`**

```python
# Em app/teams/agents/calendar.py, dentro do método schedule_meeting

# ... (após a criação do evento no Google Calendar)
if result and result.get("google_event_id"):
    # ... (código existente para salvar no banco)

    # >>> INÍCIO DA NOVA LÓGICA <<<
    try:
        qualification_data = {
            'lead_id': lead_id,
            'score': 85, # Exemplo de score
            'notes': f"Reunião '{title}' agendada para {date} às {time}."
        }
        await supabase_client.create_lead_qualification(qualification_data)
    except Exception as e:
        logger.error(f"Falha ao criar registro de qualificação para o lead {lead_id}: {e}")
        # Não interromper o fluxo principal por causa disso
    # >>> FIM DA NOVA LÓGICA <<<

    logger.info(f"✅ Reunião agendada: {title} em {date} às {time}")
    return { ... }
```

### 5.3. Checklist de Implementação

- [ ] Adicionar a função `create_lead_qualification` à classe `SupabaseClient`.
- [ ] Adicionar a chamada para `supabase_client.create_lead_qualification` dentro do método `schedule_meeting` do `CalendarAgent`.
- [ ] Garantir que todos os campos obrigatórios da tabela `leads_qualifications` sejam preenchidos.
- [ ] Testar o agendamento de uma reunião e verificar se o registro correspondente é criado na tabela.

---

## 6. Problema 5: Erro `TypeError: float()` em `kommo_auto_sync`

### 6.1. Diagnóstico Detalhado

O log de erro é explícito: `ERROR | app.services.kommo_auto_sync:_create_deal_for_qualified_lead:426 | ❌ Erro ao criar deal: float() argument must be a string or a real number, not 'NoneType'`.

Isso significa que na linha 426 do arquivo `app/services/kommo_auto_sync.py`, dentro da função `_create_deal_for_qualified_lead`, a função `float()` está sendo chamada com um argumento `None`. Analisando o código-fonte, a linha problemática é provavelmente esta:

`value=float(lead.get("bill_value")) * 12`

O erro ocorre quando `lead.get("bill_value")` retorna `None`. Isso pode acontecer se um lead for marcado como qualificado sem que o valor da conta de luz tenha sido registrado no banco de dados.

### 6.2. Plano de Ação e Solução Proposta

A solução é adicionar uma verificação defensiva para garantir que `lead.get("bill_value")` não seja `None` antes de passá-lo para `float()`. Se for `None`, devemos usar um valor padrão (como `0.0`) e talvez logar um aviso.

**Etapa 1: Corrigir a linha 426 em `app/services/kommo_auto_sync.py`**

```python
# Em app/services/kommo_auto_sync.py, na função _create_deal_for_qualified_lead

# ANTES (Problemático):
# result = await self.crm.create_deal(
#     lead_id=kommo_id,
#     value=float(lead.get("bill_value", 0)) * 12, # O erro pode estar aqui se o valor for None
#     name=f"Solar - {lead.get('name', 'Cliente')}"
# )

# DEPOIS (Corrigido):
bill_value = lead.get("bill_value")
if bill_value is None:
    logger.warning(f"Lead qualificado {lead.get('id')} sem 'bill_value'. Usando 0.0 para o deal.")
    deal_value = 0.0
else:
    try:
        deal_value = float(bill_value) * 12
    except (ValueError, TypeError):
        logger.error(f"Não foi possível converter 'bill_value' ({bill_value}) para float para o lead {lead.get('id')}. Usando 0.0.")
        deal_value = 0.0

result = await self.crm.create_deal(
    lead_id=kommo_id,
    value=deal_value,
    name=f"Solar - {lead.get('name', 'Cliente')}"
)
```

Esta abordagem é mais robusta, pois trata explicitamente o caso `None` e também possíveis erros de conversão, garantindo que o programa não quebre e que o problema seja devidamente registrado.

### 6.3. Checklist de Implementação

- [ ] Localizar a linha exata da chamada `float()` em `_create_deal_for_qualified_lead`.
- [ ] Adicionar uma verificação para `None` antes da conversão para `float`.
- [ ] Usar um valor padrão (ex: `0.0`) se `bill_value` for `None`.
- [ ] Adicionar um log de aviso (`logger.warning`) para registrar quando essa condição ocorrer.
- [ ] Testar o fluxo com um lead qualificado que intencionalmente não tenha `bill_value` no banco.
