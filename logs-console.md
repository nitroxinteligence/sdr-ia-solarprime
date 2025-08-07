✅ Usando variáveis de ambiente do servidor (EasyPanel)
2025-08-07 16:39:41.538 | INFO     | app.services.knowledge_service:__init__:33 | ✅ KnowledgeService inicializado (versão simplificada)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-07 16:39:42.307 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-07 16:39:42.310 | INFO     | app.integrations.redis_client:connect:39 | ✅ Conectado ao Redis com sucesso! URL: redis_redis:6379
2025-08-07 16:39:42.310 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-07 16:39:42.809 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-07 16:39:42.810 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buffer Inteligente inicializado (timeout=30.0s, max=10)
2025-08-07 16:39:42.810 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-07 16:39:42.811 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=150 chars, smart=ativada)
2025-08-07 16:39:42.811 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 150}
2025-08-07 16:39:42.811 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 16:39:42.811 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 16:39:42.811 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 16:39:42.812 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 16:39:42.812 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 16:39:42.812 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 16:39:42.812 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 16:39:42.812 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 16:39:42.813 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 16:39:42.813 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 16:39:42.814 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 16:39:42.814 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 16:39:42.815 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 16:39:42.815 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 16:39:42.815 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 16:39:42.815 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 3}
2025-08-07 16:39:43.482 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-07 16:39:43.482 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-07 16:39:43.482 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-07 16:39:43.483 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-07 16:39:43.483 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Fonte' mapeado: ID 392810
2025-08-07 16:39:43.483 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-07 16:39:43.484 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-07 16:39:43.484 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-07 16:39:44.159 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-07 16:39:44.160 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-07 16:39:44.160 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-07 16:39:44.160 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-07 16:39:44.160 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-07 16:39:44.161 | INFO     | app.teams.agents.crm:initialize:195 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-07 16:39:44.162 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-07 16:39:44.183 | INFO     | app.services.kommo_auto_sync:__init__:94 | ✅ KommoAutoSyncService inicializado
2025-08-07 16:39:44.183 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 16:39:44.184 | INFO     | app.teams.agents.crm_enhanced:__init__:43 | ✅ KommoEnhancedCRM inicializado com funcionalidades completas
2025-08-07 16:39:44.741 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-07 16:39:44.742 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-07 16:39:44.742 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-07 16:39:44.742 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-07 16:39:44.743 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Fonte' mapeado: ID 392810
2025-08-07 16:39:44.743 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-07 16:39:44.743 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-07 16:39:44.743 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-07 16:39:45.319 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-07 16:39:45.320 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-07 16:39:45.320 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-07 16:39:45.320 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-07 16:39:45.320 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-07 16:39:45.321 | INFO     | app.teams.agents.crm:initialize:195 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-07 16:39:45.321 | INFO     | app.services.kommo_auto_sync:initialize:103 | ✅ CRM Enhanced inicializado para auto-sync
2025-08-07 16:39:45.321 | INFO     | app.services.kommo_auto_sync:start:116 | 🔄 Iniciando sincronização automática com Kommo CRM
2025-08-07 16:39:45.322 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo Auto Sync pronto | Data: {'sync_interval': '30s', 'features': 'leads, tags, pipeline, fields'}
2025-08-07 16:39:45.345 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto
2025-08-07 16:39:45.345 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto | Data: {'check_interval': '1min', 'types': '30min, 24h'}
2025-08-07 16:39:45.346 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔥 Pré-aquecendo AgenticSDR (tentativa 1/3)...
2025-08-07 16:39:45.346 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-07 16:39:45.346 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-07 16:39:45.346 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-07 16:39:45.347 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-07 16:39:45.347 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-07 16:39:45.347 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-07 16:39:45.347 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-07 16:39:45.376 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-07 16:39:45.376 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-07 16:39:45.784 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-07 16:39:45.785 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 16:39:45.785 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 16:39:45.785 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 16:39:45.786 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 16:39:45.786 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 16:39:45.786 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 16:39:45.786 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 16:39:45.786 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 16:39:45.787 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 16:39:45.787 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 16:39:45.787 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 16:39:45.788 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 16:39:45.788 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 16:39:45.788 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 16:39:45.788 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 16:39:45.789 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-07 16:39:45.789 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-07 16:39:45.789 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ AgenticSDR singleton criado e pronto! pronto
2025-08-07 16:39:45.789 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AgenticSDR pronto | Data: {'status': 'pré-aquecido com sucesso'}
2025-08-07 16:39:45.789 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:56056 - "GET /health HTTP/1.1" 200 OK
2025-08-07 16:39:53.209 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:49648 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-07 16:39:53.527 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 16:39:53.527 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:300 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:39:53.522Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49648 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 16:39:53.546 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 16:39:53.547 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:300 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:39:53.531Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49648 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 16:39:53.561 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:49648 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-07 16:39:53.562 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'oi', 'sender': '558182986181', 'type': 'text'}
2025-08-07 16:39:53.563 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 2}
2025-08-07 16:39:54.804 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:49648 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-07 16:39:55.670 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 16:39:55.671 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:305 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:39:53.843Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 16:39:57.076 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 16:39:57.076 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:305 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:39:53.893Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49674 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 16:39:57.077 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-07 16:39:57.324 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 16:39:57.902 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: e0be0811-045b-4936-818a-0a352e9e3cf7
2025-08-07 16:39:57.903 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: e0be0811-045b-4936-818a-0a352e9e3cf7
2025-08-07 16:39:58.121 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 1 mensagens encontradas (limite solicitado: 100)
2025-08-07 16:39:58.121 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 1 mensagens disponíveis (menos que o limite de 100)
2025-08-07 16:39:58.122 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: e0be0811-045b-4936-818a-0a352e9e3cf7
2025-08-07 16:39:58.122 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: e0be0811-045b-4936-818a-0a352e9e3cf7
2025-08-07 16:39:58.343 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 1 mensagens encontradas (limite solicitado: 100)
2025-08-07 16:39:58.343 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 1 mensagens disponíveis (menos que o limite de 100)
2025-08-07 16:39:58.343 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 1 mensagens
2025-08-07 16:39:58.344 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 16:39:58.344 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: INITIAL_CONTACT
                    - Status: PENDING
                    
                    USER: oi
                    
                    MENSAGEM ATUAL DO CLIENTE: oi
                    
                    
                    Análise Contextual:
                    - Contexto Principal: initial_contact
                    - Engajamento: lo...
2025-08-07 16:39:58.344 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 954 caracteres
2025-08-07 16:39:58.344 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ❌ Nenhum resultado multimodal incluído no prompt
2025-08-07 16:39:58.344 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun...
2025-08-07 16:39:58.344 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem instructions? True
2025-08-07 16:39:58.344 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem memory? True
2025-08-07 16:39:58.345 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem model? True
2025-08-07 16:39:59.783 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 16:39:59.783 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:300 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:39:59.776Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 16:39:59.813 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 16:39:59.813 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:300 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:39:59.798Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 16:39:59.827 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-07 16:39:59.828 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'quero saber mais sobre energia solar', 'sender': '558182986181', 'type': 'text'}
2025-08-07 16:40:00.097 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 16:40:00.098 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:305 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:40:00.089Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 16:40:00.191 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 16:40:00.191 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:305 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:40:00.185Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-07 16:40:15.630 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ agent.arun completou sem erro
2025-08-07 16:40:15.630 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Tipo do result: <class 'agno.run.response.RunResponse'>
2025-08-07 16:40:15.630 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result tem content? True
2025-08-07 16:40:15.630 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Atributos do result: ['content', 'content_type', 'thinking', 'reasoning_content', 'messages', 'metrics', 'model', 'model_provider', 'run_id', 'agent_id', 'agent_name', 'session_id', 'team_session_id', 'workflow_id', 'tools', 'formatted_tool_calls', 'images', 'videos', 'audio', 'response_audio', 'citations', 'extra_data', 'created_at', 'events', 'status']
2025-08-07 16:40:15.630 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Result não é None, tipo: RunResponse
2025-08-07 16:40:15.631 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 raw_response (primeiros 200 chars): Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?...
2025-08-07 16:40:15.631 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho raw_response: 141 caracteres
2025-08-07 16:40:16.288 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPr...
2025-08-07 16:40:16.288 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=174, primeiros 200 chars: <RESPOSTA_FINAL>Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?</RESPOSTA_FINAL>
2025-08-07 16:40:16.289 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=174, primeiros 200 chars: <RESPOSTA_FINAL>Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?</RESPOSTA_FINAL>
2025-08-07 16:40:16.523 | INFO     | app.services.kommo_auto_sync:sync_new_leads:187 | 📋 1 novos leads para sincronizar com Kommo
INFO:     127.0.0.1:41588 - "GET /health HTTP/1.1" 200 OK
INFO:     10.11.0.4:32978 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-07 16:40:19.753 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:346 | 📍 Lead 3812658 movido para estágio novo_lead
2025-08-07 16:40:19.754 | INFO     | app.services.kommo_auto_sync:_sync_single_lead:235 | ✅ Lead 5d9402a5-63b5-430b-9a1d-cb828cb7552c sincronizado com Kommo (ID: 3812658)
2025-08-07 16:40:21.534 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 2.65, 'message_length': 141, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 16:40:26.348 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 141, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 16:40:26.348 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Oii! Boa tarde! Meu nome é Helen Vieira, sou consu', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 16:40:26.349 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB09114E5E7D03CDBC5E5A4C972DB78C819FF8F
2025-08-07 16:40:27.034 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 16:40:27.035 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:309 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:44324 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 16:40:27.475 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Follow-up de 30min agendado para 558182986181 às 14:10
2025-08-07 16:40:27.475 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Follow-up sequencial: 24h será agendado apenas se usuário não responder ao de 30min
2025-08-07 16:40:27.601 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:44324 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 16:40:32.466 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:44324 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-07 16:40:35.792 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:44324 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-07 16:40:42.618 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 16:40:42.619 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:300 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:40:42.607Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:56548 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 16:40:42.633 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:56548 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-07 16:40:42.634 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'mateus', 'sender': '558182986181', 'type': 'text'}
2025-08-07 16:40:42.635 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 6}
2025-08-07 16:40:43.095 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 16:40:43.095 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:305 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:40:42.918Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:56548 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 16:40:43.096 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 16:40:43.096 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:305 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:40:42.958Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:56560 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 16:40:44.386 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 1 mensagens
2025-08-07 16:40:44.386 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 16:40:44.386 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: INITIAL_CONTACT
                    - Status: PENDING
                    
                    USER: oi
                    
                    MENSAGEM ATUAL DO CLIENTE: mateus
                    
                    
                    Análise Contextual:
                    - Contexto Principal: initial_contact
                    - Engajamento...
2025-08-07 16:40:44.387 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 958 caracteres
2025-08-07 16:40:44.387 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ❌ Nenhum resultado multimodal incluído no prompt
2025-08-07 16:40:44.387 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun...
2025-08-07 16:40:44.387 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem instructions? True
2025-08-07 16:40:44.387 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem memory? True
2025-08-07 16:40:44.388 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem model? True
2025-08-07 16:40:44.402 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:56560 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 16:40:44.402 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 16:40:44.403 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:309 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:56548 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-07 16:40:46.505 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:372 | 📝 1 leads atualizados para sincronizar
INFO:     10.11.0.4:56548 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-07 16:40:48.438 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:215 | ✅ Tags adicionadas ao lead 3812658: []
INFO:     127.0.0.1:39246 - "GET /health HTTP/1.1" 200 OK
2025-08-07 16:40:49.334 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:346 | 📍 Lead 3812658 movido para estágio novo_lead
2025-08-07 16:40:49.334 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:397 | 🔄 Lead 5d9402a5-63b5-430b-9a1d-cb828cb7552c atualizado no Kommo
WARNING  MemoryDb not provided.                                                 
2025-08-07 16:40:59.341 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ agent.arun completou sem erro
2025-08-07 16:40:59.341 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Tipo do result: <class 'agno.run.response.RunResponse'>
2025-08-07 16:40:59.341 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result tem content? True
2025-08-07 16:40:59.342 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Atributos do result: ['content', 'content_type', 'thinking', 'reasoning_content', 'messages', 'metrics', 'model', 'model_provider', 'run_id', 'agent_id', 'agent_name', 'session_id', 'team_session_id', 'workflow_id', 'tools', 'formatted_tool_calls', 'images', 'videos', 'audio', 'response_audio', 'citations', 'extra_data', 'created_at', 'events', 'status']
2025-08-07 16:40:59.342 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Result não é None, tipo: RunResponse
2025-08-07 16:40:59.342 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 raw_response (primeiros 200 chars): Prazer, Mateus! Então vamos lá! Hoje na SolarPrime nós temos 4 soluções energéticas... instalação de usina própria, aluguel de lote para instalação de usina própria, compra de energia com desconto e u...
2025-08-07 16:40:59.342 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho raw_response: 287 caracteres
2025-08-07 16:40:59.342 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ 🚨 ALERTA: Resposta contém solicitação de dados proibidos!
2025-08-07 16:40:59.342 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Resposta original: <RESPOSTA_FINAL>Prazer, Mateus! Então vamos lá! Hoje na SolarPrime nós temos 4 soluções energéticas... instalação de usina própria, aluguel de lote para instalação de usina própria, compra de energia com desconto e usina de investimento. Qual desses modelos seria do seu interesse? Ou seria outra opção?</RESPOSTA_FINAL>
2025-08-07 16:40:59.581 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>Ótimo! Para eu fazer uma proposta personalizada de economia, preciso apenas saber o ...
2025-08-07 16:40:59.581 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=178, primeiros 200 chars: <RESPOSTA_FINAL>Ótimo! Para eu fazer uma proposta personalizada de economia, preciso apenas saber o valor da sua conta de luz. Quanto você está pagando em média?</RESPOSTA_FINAL>
2025-08-07 16:40:59.582 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=178, primeiros 200 chars: <RESPOSTA_FINAL>Ótimo! Para eu fazer uma proposta personalizada de economia, preciso apenas saber o valor da sua conta de luz. Quanto você está pagando em média?</RESPOSTA_FINAL>
2025-08-07 16:41:04.597 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.05, 'message_length': 145, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 16:41:09.806 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 145, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 16:41:09.807 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Ótimo! Para eu fazer uma proposta personalizada de', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 16:41:09.807 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB01FA56AD3F0F50E4CE21E94AAE08001BD0B6E
2025-08-07 16:41:10.903 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 16:41:10.904 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:309 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:50812 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 16:41:10.905 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:50816 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 16:41:11.343 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Follow-up de 30min agendado para 558182986181 às 14:11
2025-08-07 16:41:11.344 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Follow-up sequencial: 24h será agendado apenas se usuário não responder ao de 30min
INFO:     127.0.0.1:42886 - "GET /health HTTP/1.1" 200 OK
2025-08-07 16:41:30.987 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 16:41:30.987 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:300 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:41:30.975Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:50032 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 16:41:31.261 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:50032 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-07 16:41:31.262 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Imagem recebida]', 'sender': '558182986181', 'type': 'text'}
2025-08-07 16:41:31.264 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 17}
2025-08-07 16:41:31.891 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 16:41:31.891 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:305 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:41:31.353Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:50032 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 16:41:31.892 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 16:41:31.893 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:305 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T13:41:31.586Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:50038 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 16:41:32.928 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:50038 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 16:41:32.928 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 16:41:32.929 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:309 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:50032 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-07 16:41:32.930 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📸 IMAGEM DETECTADA - Analisando estrutura...
2025-08-07 16:41:32.930 | INFO     | app.api.webhooks:process_message_with_agent:579 | Campos disponíveis na imageMessage: ['url', 'mimetype', 'fileSha256', 'fileLength', 'height', 'width', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'jpegThumbnail', 'contextInfo', 'firstScanSidecar', 'firstScanLength', 'scansSidecar', 'scanLengths', 'midQualityFileSha256', 'imageSourceType']
2025-08-07 16:41:32.930 | INFO     | app.api.webhooks:process_message_with_agent:586 | jpegThumbnail é string, tamanho: 960 chars
2025-08-07 16:41:32.930 | INFO     | app.api.webhooks:process_message_with_agent:587 | jpegThumbnail primeiros 50 chars: /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHB
2025-08-07 16:41:32.930 | INFO     | app.api.webhooks:process_message_with_agent:590 | jpegThumbnail parece ser base64 válido
2025-08-07 16:41:32.930 | INFO     | app.api.webhooks:process_message_with_agent:597 | mediaKey presente: 0pomlp/C41alGUXGXJRS...
2025-08-07 16:41:32.931 | INFO     | app.api.webhooks:process_message_with_agent:599 | directPath presente: /o1/v/t24/f2/m231/AQODWOx8Idn7nPIh46WNe6Ze7uKKlR81...
2025-08-07 16:41:32.931 | INFO     | app.api.webhooks:process_message_with_agent:601 | URL presente: https://mmg.whatsapp.net/o1/v/t24/f2/m231/AQODWOx8...
2025-08-07 16:41:32.931 | INFO     | app.api.webhooks:process_message_with_agent:622 | 🔐 Incluindo mediaKey para descriptografia
2025-08-07 16:41:32.931 | INFO     | app.integrations.evolution:download_media:1057 | Baixando mídia de: https://mmg.whatsapp.net/o1/v/t24/f2/m231/AQODWOx8...
2025-08-07 16:41:32.931 | INFO     | app.integrations.evolution:download_media:1059 | MediaKey presente - mídia será descriptografada (tipo: image)
2025-08-07 16:41:36.099 | INFO     | app.integrations.evolution:download_media:1079 | Mídia baixada com sucesso: 1008266 bytes
2025-08-07 16:41:36.100 | INFO     | app.integrations.evolution:download_media:1083 | Iniciando descriptografia da mídia...
2025-08-07 16:41:36.100 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:958 | MediaKey decodificada: 32 bytes
2025-08-07 16:41:36.101 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:991 | IV: 16 bytes, Cipher Key: 32 bytes, MAC Key: 32 bytes
2025-08-07 16:41:36.105 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:1027 | Mídia descriptografada com sucesso: 1008245 bytes
2025-08-07 16:41:36.105 | INFO     | app.integrations.evolution:download_media:1091 | Mídia descriptografada com sucesso: 1008245 bytes
2025-08-07 16:41:36.106 | INFO     | app.api.webhooks:process_message_with_agent:628 | Imagem baixada, primeiros 20 bytes (hex): ffd8ffe000104a46494600010100000100010000
2025-08-07 16:41:36.112 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-07 16:41:36.112 | INFO     | app.api.webhooks:process_message_with_agent:665 | 🔍 AGNO validou mídia: jpeg
2025-08-07 16:41:36.112 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Imagem validada (jpeg): 1344328 chars
2025-08-07 16:41:36.326 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 1 mensagens
2025-08-07 16:41:36.326 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-07 16:41:36.326 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: IMAGE
2025-08-07 16:41:36.326 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 1,344,328 caracteres
2025-08-07 16:41:36.326 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-07 16:41:36.326 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-07 16:41:36
2025-08-07 16:41:36.327 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 16:41:36.327 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-07 16:41:36.327 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 PROCESSAMENTO DE IMAGEM INICIADO
2025-08-07 16:41:36.327 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-07 16:41:36.327 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 IMAGEM - Formato detectado: base64
2025-08-07 16:41:36.327 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📈 IMAGEM - Métricas:
2025-08-07 16:41:36.327 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Base64: 1,344,328 caracteres
2025-08-07 16:41:36.327 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Estimado: 1,008,246 bytes (984.6 KB / 0.96 MB)
2025-08-07 16:41:36.340 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📐 IMAGEM - Dimensões: 2268x4032 pixels
2025-08-07 16:41:36.525 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 1/4: Decodificando base64...
2025-08-07 16:41:36.532 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Decodificação completa em 0.01s
2025-08-07 16:41:36.533 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tamanho real: 1,008,245 bytes
2025-08-07 16:41:36.533 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Taxa compressão: 25.0%
2025-08-07 16:41:36.533 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 2/4: Detectando formato da imagem...
2025-08-07 16:41:36.533 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-07 16:41:36.534 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato detectado: JPEG
2025-08-07 16:41:36.534 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Confiança: high
2025-08-07 16:41:36.534 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo detecção: 0.00s
2025-08-07 16:41:36.534 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔧 Usando PIL + Gemini direto (correção implementada)
2025-08-07 16:41:36.538 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📤 Enviando imagem para Gemini Vision com prompt otimizado...
2025-08-07 16:41:52.477 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ PIL + Gemini direto: Sucesso (latência otimizada)
2025-08-07 16:41:53.203 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:372 | 📝 1 leads atualizados para sincronizar
2025-08-07 16:41:53.421 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 16:41:53.421 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ MULTIMODAL: Processamento concluído
2025-08-07 16:41:53.421 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tipo: image
2025-08-07 16:41:53.422 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Status: success
2025-08-07 16:41:53.422 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo total: 17.09s
2025-08-07 16:41:53.422 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 16:41:53.422 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 16:41:53.422 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: INITIAL_CONTACT
                    - Status: PENDING
                    
                    USER: oi
                    
                    MENSAGEM ATUAL DO CLIENTE: [Imagem recebida]
                    
                    
                    Análise Contextual:
                    - Contexto Principal: initial_contact
                    - ...
2025-08-07 16:41:53.422 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 969 caracteres
2025-08-07 16:41:53.423 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Multimodal incluído no prompt: Claro, aqui está uma análise estruturada da imagem fornecida:

**Tipo de documento:** DANFE - Documento Auxiliar da Nota Fiscal de Energia Elétrica Eletrônica

**Valores encontrados:**

* **Total a pa...
2025-08-07 16:41:53.423 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🖼️ Multimodal incluído no prompt: tipo=bill_image, tem conteúdo=True
2025-08-07 16:41:53.423 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun...
2025-08-07 16:41:53.423 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem instructions? True
2025-08-07 16:41:53.423 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem memory? True
2025-08-07 16:41:53.423 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem model? True
INFO:     127.0.0.1:58274 - "GET /health HTTP/1.1" 200 OK
INFO:     10.11.0.4:42656 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-07 16:41:55.347 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:215 | ✅ Tags adicionadas ao lead 3812658: []
2025-08-07 16:41:55.906 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:346 | 📍 Lead 3812658 movido para estágio novo_lead
2025-08-07 16:41:55.907 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:397 | 🔄 Lead 5d9402a5-63b5-430b-9a1d-cb828cb7552c atualizado no Kommo
INFO:     127.0.0.1:34030 - "GET /health HTTP/1.1" 200 OK
/root/.local/lib/python3.11/site-packages/agno/agent/agent.py:1213: RuntimeWarning: coroutine 'AgenticSDR.process_multimodal_content' was never awaited
  model_response: ModelResponse = await self.model.aresponse(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
WARNING  MemoryDb not provided.                                                 
2025-08-07 16:42:27.499 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ agent.arun completou sem erro
2025-08-07 16:42:27.499 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Tipo do result: <class 'agno.run.response.RunResponse'>
2025-08-07 16:42:27.500 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result tem content? True
2025-08-07 16:42:27.500 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Atributos do result: ['content', 'content_type', 'thinking', 'reasoning_content', 'messages', 'metrics', 'model', 'model_provider', 'run_id', 'agent_id', 'agent_name', 'session_id', 'team_session_id', 'workflow_id', 'tools', 'formatted_tool_calls', 'images', 'videos', 'audio', 'response_audio', 'citations', 'extra_data', 'created_at', 'events', 'status']
2025-08-07 16:42:27.500 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Result não é None, tipo: RunResponse
2025-08-07 16:42:27.500 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 raw_response (primeiros 200 chars): Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?...
2025-08-07 16:42:27.500 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho raw_response: 141 caracteres
2025-08-07 16:42:27.720 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPr...
2025-08-07 16:42:27.720 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=174, primeiros 200 chars: <RESPOSTA_FINAL>Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?</RESPOSTA_FINAL>
2025-08-07 16:42:27.720 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=174, primeiros 200 chars: <RESPOSTA_FINAL>Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?</RESPOSTA_FINAL>
2025-08-07 16:42:28.594 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando emoji para reaction | Data: {'reaction': '✅', 'recipient': 'reaction', 'type': 'emoji'}
2025-08-07 16:42:28.594 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Reação '✅' enviada com sucesso. ID: 3EB0F60939790D1AE0D429015EE299832542CA5C
2025-08-07 16:42:28.806 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 16:42:28.806 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:309 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:42592 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 16:42:29.506 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:42592 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 16:42:29.510 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 16:42:29.510 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:309 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:42592 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-07 16:42:36.104 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.12, 'message_length': 141, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 16:42:41.592 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 141, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 16:42:41.592 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Oii! Boa tarde! Meu nome é Helen Vieira, sou consu', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 16:42:41.592 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB01BE8F91AD1CBD1804DA4834A97EEE48DCAAC
2025-08-07 16:42:41.600 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 16:42:41.600 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:309 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:37102 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 16:42:42.594 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:37102 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 16:42:42.601 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 16:42:42.601 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:309 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:37102 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-07 16:42:46.370 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Follow-up de 30min agendado para 558182986181 às 14:12
2025-08-07 16:42:46.371 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Follow-up sequencial: 24h será agendado apenas se usuário não responder ao de 30min
INFO:     127.0.0.1:59336 - "GET /health HTTP/1.1" 200 OK
2025-08-07 16:42:56.129 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:372 | 📝 1 leads atualizados para sincronizar
INFO:     10.11.0.4:40458 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-07 16:42:57.818 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:215 | ✅ Tags adicionadas ao lead 3812658: []
2025-08-07 16:42:58.488 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:346 | 📍 Lead 3812658 movido para estágio novo_lead
2025-08-07 16:42:58.488 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:397 | 🔄 Lead 5d9402a5-63b5-430b-9a1d-cb828cb7552c atualizado no Kommo