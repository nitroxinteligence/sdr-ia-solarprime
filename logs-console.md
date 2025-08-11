2025-08-11 16:01:42.326 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 31}

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

2025-08-11 16:01:42.812 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-11 16:01:42.818 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-11 16:01:42.832 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-11 16:01:42.833 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-11 16:01:42.833 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-11 16:01:42.838 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-11 16:01:42.842 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-11 16:01:42.863 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-11 16:01:42.864 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

2025-08-11 16:01:43.295 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-11 16:01:43.298 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-11 16:01:43.298 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-11 16:01:43.299 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-11 16:01:43.301 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-11 16:01:43.301 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-11 16:01:43.305 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-11 16:01:43.306 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-11 16:01:43.306 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-11 16:01:43.330 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-11 16:01:43.331 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-11 16:01:43.345 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-11 16:01:43.345 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-11 16:01:43.346 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-11 16:01:43.347 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-11 16:01:43.352 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-11 16:01:43.352 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-11 16:01:43.352 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-11 16:01:43.353 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Nova instância do AgenticSDR criada! pronto
2025-08-11 16:01:43.353 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversa validada - ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f, Phone: 558182986181
2025-08-11 16:01:44.206 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 WEBHOOK: Usando conversation_id=09c7fc7e-a847-43c2-a06b-761a2acd493f para phone=558182986181
2025-08-11 16:01:44.207 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chamando process_message com conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-11 16:01:44.423 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=558182986181
2025-08-11 16:01:44.424 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-11 16:01:44.636 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-11 16:01:44.636 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-11 16:01:47.286 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-11 16:01:47.286 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-11 16:01:47.287 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 65
2025-08-11 16:01:47.287 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-11 16:01:47.287 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-11T16:01:43.354522+00:00 - user
2025-08-11 16:01:47.287 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-11 16:01:47.288 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 65 mensagens disponíveis (menos que o limite de 100)
2025-08-11 16:01:47.293 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-11 16:01:47.293 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-11 16:01:47.293 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-11 16:01:49.113 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-11 16:01:49.114 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-11 16:01:49.114 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 65
2025-08-11 16:01:49.114 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-11 16:01:49.114 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-11T16:01:43.354522+00:00 - user
2025-08-11 16:01:49.114 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-11 16:01:49.114 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 65 mensagens disponíveis (menos que o limite de 100)
2025-08-11 16:01:49.115 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ HISTÓRICO FINAL: 65 mensagens carregadas
2025-08-11 16:01:49.116 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: Chamar SDR Team - FollowUpAgent | Data: {'recommended_agent': 'FollowUpAgent', 'decision_score': 0.5}
2025-08-11 16:01:49.117 | INFO     | app.teams.sdr_team:process_message_with_context:668 | 📅 AGENT RECOMENDADO: FollowUpAgent
2025-08-11 16:01:49.117 | INFO     | app.teams.sdr_team:process_message_with_context:669 | 📅 Razão: Score de complexidade: 0.50. Lead de alto valor detectado - qualificação pelo AgenticSDR. Follow-up estratégico necessário
2025-08-11 16:01:49.625 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:48384 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:35362 - "GET /health HTTP/1.1" 200 OK
2025-08-11 16:02:21.658 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Timeout na personalização após 25s, usando resposta original
2025-08-11 16:02:21.905 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: O Calendar Manager está pronto para agendar a reunião, mas preciso de algumas informações adicionais...
2025-08-11 16:02:21.906 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=442, primeiros 200 chars: O Calendar Manager está pronto para agendar a reunião, mas preciso de algumas informações adicionais para prosseguir. Por favor, forneça os seguintes detalhes:

*   **Data da reunião:**
*   **Horário 
2025-08-11 16:02:21.914 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em extract_final_response: 🚨 TAGS <RESPOSTA_FINAL> NÃO ENCONTRADAS - BLOQUEANDO VAZAMENTO | Data: {'component': 'extract_final_response'}
2025-08-11 16:02:21.942 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em extract_final_response: 📝 Conteúdo original (primeiros 200 chars): O Calendar Manager está pronto para agendar a reunião, mas preciso de algumas informações adicionais para prosseguir. Por favor, forneça os seguintes detalhes:

*   **Data da reunião:**
*   **Horário ... | Data: {'component': 'extract_final_response'}
2025-08-11 16:02:21.943 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ 🔒 Usando resposta segura para evitar vazamento de raciocínio interno
2025-08-11 16:02:21.943 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=442, primeiros 200 chars: O Calendar Manager está pronto para agendar a reunião, mas preciso de algumas informações adicionais para prosseguir. Por favor, forneça os seguintes detalhes:

*   **Data da reunião:**
*   **Horário 
2025-08-11 16:02:21.943 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em extract_final_response: 🚨 TAGS <RESPOSTA_FINAL> NÃO ENCONTRADAS - BLOQUEANDO VAZAMENTO | Data: {'component': 'extract_final_response'}
2025-08-11 16:02:21.943 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em extract_final_response: 📝 Conteúdo original (primeiros 200 chars): O Calendar Manager está pronto para agendar a reunião, mas preciso de algumas informações adicionais para prosseguir. Por favor, forneça os seguintes detalhes:

*   **Data da reunião:**
*   **Horário ... | Data: {'component': 'extract_final_response'}
2025-08-11 16:02:21.944 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ 🔒 Usando resposta segura para evitar vazamento de raciocínio interno
2025-08-11 16:02:21.944 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Resposta completa antes de dividir: Oi! Me dê só um minutinho que já te respondo!