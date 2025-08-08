2025-08-08 03:26:23.530 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 15}
2025-08-08 03:26:23.977 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-08 03:26:23.977 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-08 03:26:23.977 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-08 03:26:23.977 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-08 03:26:23.979 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-08 03:26:23.979 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-08 03:26:23.979 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-08 03:26:23.980 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-08 03:26:23.980 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-08 03:26:24.383 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-08 03:26:24.384 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-08 03:26:24.384 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-08 03:26:24.384 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-08 03:26:24.385 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-08 03:26:24.385 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-08 03:26:24.385 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-08 03:26:24.385 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-08 03:26:24.385 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-08 03:26:24.386 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-08 03:26:24.386 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-08 03:26:24.387 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-08 03:26:24.387 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-08 03:26:24.387 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-08 03:26:24.388 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-08 03:26:24.388 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-08 03:26:24.388 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-08 03:26:24.388 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-08 03:26:24.389 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Nova instância do AgenticSDR criada! pronto
2025-08-08 03:26:24.389 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversa validada - ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f, Phone: 558182986181
2025-08-08 03:26:25.389 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 WEBHOOK: Usando conversation_id=09c7fc7e-a847-43c2-a06b-761a2acd493f para phone=558182986181
2025-08-08 03:26:25.389 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chamando process_message com conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 03:26:25.962 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=558182986181
2025-08-08 03:26:25.962 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-08 03:26:26.539 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 03:26:26.539 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 03:26:28.163 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-08 03:26:28.163 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 03:26:28.163 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 59
2025-08-08 03:26:28.163 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-08 03:26:28.164 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-08T03:26:24.389593+00:00 - user
2025-08-08 03:26:28.164 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-08 03:26:28.165 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 59 mensagens disponíveis (menos que o limite de 100)
2025-08-08 03:26:28.168 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 03:26:28.168 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 03:26:28.168 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 03:26:29.776 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-08 03:26:29.776 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 03:26:29.777 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 59
2025-08-08 03:26:29.777 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-08 03:26:29.777 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-08T03:26:24.389593+00:00 - user
2025-08-08 03:26:29.777 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-08 03:26:29.777 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 59 mensagens disponíveis (menos que o limite de 100)
2025-08-08 03:26:29.777 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ HISTÓRICO FINAL: 59 mensagens carregadas
2025-08-08 03:26:29.778 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:1035 | 📅 CALENDÁRIO DETECTADO - Score: 0.8
2025-08-08 03:26:29.778 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:1036 | 📅 Mensagem: pode ser as 10h...
2025-08-08 03:26:29.778 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:1037 | 📅 Agent recomendado: CalendarAgent
2025-08-08 03:26:29.778 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: Chamar SDR Team - CalendarAgent | Data: {'recommended_agent': 'CalendarAgent', 'decision_score': 1.1}
2025-08-08 03:26:29.778 | INFO     | app.teams.sdr_team:process_message_with_context:668 | 📅 AGENT RECOMENDADO: CalendarAgent
2025-08-08 03:26:29.779 | INFO     | app.teams.sdr_team:process_message_with_context:669 | 📅 Razão: Score de complexidade: 1.10. 🗓️ Solicitação de agendamento detectada - Ativando CalendarAgent. Lead de alto valor detectado - qualificação pelo AgenticSDR
2025-08-08 03:26:29.779 | INFO     | app.teams.sdr_team:process_message_with_context:673 | 🗓️ ATIVANDO CalendarAgent para EXECUÇÃO REAL de agendamento!
2025-08-08 03:26:29.779 | INFO     | app.teams.sdr_team:process_message_with_context:676 | ✅ CalendarAgent disponível - EXECUTANDO AGENDAMENTO REAL...
2025-08-08 03:26:29.780 | INFO     | app.teams.sdr_team:process_message_with_context:690 | 🚀 CRIANDO EVENTO REAL: 08/08/2025 às 10:00
2025-08-08 03:26:31.306 | INFO     | app.integrations.supabase_client:create_lead_qualification:558 | ✅ Qualificação criada para lead d665126a-6e16-4839-a91c-bd1e4fca23f5
2025-08-08 03:26:31.307 | INFO     | app.teams.agents.calendar:schedule_meeting:277 | ✅ Lead d665126a-6e16-4839-a91c-bd1e4fca23f5 qualificado ANTES do agendamento
⚠️ Service Account não pode convidar participantes sem Domain-Wide Delegation. Ignorando attendees.
2025-08-08 03:26:32.328 | INFO     | app.teams.agents.calendar:_save_meeting_to_db:1117 | ✅ Reunião salva no lead d665126a-6e16-4839-a91c-bd1e4fca23f5
2025-08-08 03:26:32.548 | ERROR    | app.teams.agents.calendar:schedule_meeting:327 | Erro ao atualizar qualificação com google_event_id: object APIResponse[~_ReturnT] can't be used in 'await' expression
2025-08-08 03:26:32.760 | INFO     | app.teams.agents.calendar:schedule_meeting:336 | ✅ Lead d665126a-6e16-4839-a91c-bd1e4fca23f5 atualizado com dados da reunião
2025-08-08 03:26:32.978 | ERROR    | app.integrations.supabase_client:create_follow_up:301 | Erro ao criar follow-up: {'message': 'new row for relation "follow_ups" violates check constraint "follow_ups_status_check"', 'code': '23514', 'hint': None, 'details': 'Failing row contains (11eba7f5-ea95-44fd-9f7e-002e694a0f41, d665126a-6e16-4839-a91c-bd1e4fca23f5, 2025-08-07 10:00:00+00, MEETING_REMINDER, Lembrete 24h - Reunião "☀️ Solar Prime - Reunião com None"..., PENDING, null, null, 2025-08-08 03:26:32.761258+00, 2025-08-08 03:26:32.761261+00, {"hours_before": 24, "meeting_time": "2025-08-08T10:00:00", "goo..., CUSTOM, null, high, 0, null, null, null, null).'}
2025-08-08 03:26:32.979 | ERROR    | app.teams.agents.calendar:schedule_meeting:376 | Erro ao criar lembretes de reunião: {'message': 'new row for relation "follow_ups" violates check constraint "follow_ups_status_check"', 'code': '23514', 'hint': None, 'details': 'Failing row contains (11eba7f5-ea95-44fd-9f7e-002e694a0f41, d665126a-6e16-4839-a91c-bd1e4fca23f5, 2025-08-07 10:00:00+00, MEETING_REMINDER, Lembrete 24h - Reunião "☀️ Solar Prime - Reunião com None"..., PENDING, null, null, 2025-08-08 03:26:32.761258+00, 2025-08-08 03:26:32.761261+00, {"hours_before": 24, "meeting_time": "2025-08-08T10:00:00", "goo..., CUSTOM, null, high, 0, null, null, null, null).'}
2025-08-08 03:26:32.979 | INFO     | app.teams.agents.calendar:schedule_meeting:378 | ✅ Reunião agendada: ☀️ Solar Prime - Reunião com None em 08/08/2025 às 10:00
2025-08-08 03:26:32.979 | INFO     | app.teams.sdr_team:process_message_with_context:709 | ✅ REUNIÃO AGENDADA COM SUCESSO! Event ID: kfnqoa4hmiiivpv998jch1de70
2025-08-08 03:26:33.274 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:379 | 📝 1 leads atualizados para sincronizar
2025-08-08 03:26:35.110 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:353 | 📍 Lead 3866108 movido para estágio reuniao_agendada
2025-08-08 03:26:35.110 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:404 | 🔄 Lead d665126a-6e16-4839-a91c-bd1e4fca23f5 atualizado no Kommo
2025-08-08 03:26:35.808 | INFO     | app.services.kommo_auto_sync:sync_qualifications:429 | 🎯 1 leads qualificados para criar deals
INFO:     10.11.0.4:59652 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-08 03:26:37.688 | INFO     | app.teams.agents.crm_enhanced:create_deal:810 | ✅ Deal criado: Solar - None - ID: 3989736
2025-08-08 03:26:37.689 | INFO     | app.services.kommo_auto_sync:_create_deal_for_qualified_lead:463 | ✅ Deal criado para lead d665126a-6e16-4839-a91c-bd1e4fca23f5 - Deal ID: 3989736
2025-08-08 03:26:38.268 | INFO     | app.services.kommo_auto_sync:_create_deal_for_qualified_lead:477 | 💰 Deal criado para lead qualificado d665126a-6e16-4839-a91c-bd1e4fca23f5
INFO:     127.0.0.1:41000 - "GET /health HTTP/1.1" 200 OK
2025-08-08 03:26:47.979 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Timeout na personalização após 15s, usando resposta original
2025-08-08 03:26:48.208 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RACIOCINIO>
CalendarAgent executou agendamento real no Google Calendar
Event ID: kfnqoa4hmiiivpv998...
2025-08-08 03:26:48.216 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=387, primeiros 200 chars: <RACIOCINIO>
CalendarAgent executou agendamento real no Google Calendar
Event ID: kfnqoa4hmiiivpv998jch1de70
Meet Link: None
</RACIOCINIO>

<RESPOSTA_FINAL>
✅ Perfeito! Sua reunião está confirmada!

📅
2025-08-08 03:26:48.217 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=387, primeiros 200 chars: <RACIOCINIO>
CalendarAgent executou agendamento real no Google Calendar
Event ID: kfnqoa4hmiiivpv998jch1de70
Meet Link: None
</RACIOCINIO>

<RESPOSTA_FINAL>
✅ Perfeito! Sua reunião está confirmada!

📅
2025-08-08 03:26:48.218 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Resposta completa antes de dividir: Perfeito! Sua reunião está confirmada! Data: 08/08/2025 às 10:00 Duração: 1 hora Convite: matheuscdsgn@gmail.com Google Meet: None Você receberá lembretes: • 24 horas antes • 2 horas antes Até lá!
2025-08-08 03:26:48.218 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho: 196 chars