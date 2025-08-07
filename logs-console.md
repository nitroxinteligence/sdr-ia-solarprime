✅ Usando variáveis de ambiente do servidor (EasyPanel)
2025-08-07 17:45:16.074 | INFO     | app.services.knowledge_service:__init__:33 | ✅ KnowledgeService inicializado (versão simplificada)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-07 17:45:16.858 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-07 17:45:16.862 | INFO     | app.integrations.redis_client:connect:39 | ✅ Conectado ao Redis com sucesso! URL: redis_redis:6379
2025-08-07 17:45:16.862 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-07 17:45:17.299 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-07 17:45:17.300 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buffer Inteligente inicializado (timeout=30.0s, max=10)
2025-08-07 17:45:17.300 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-07 17:45:17.301 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=150 chars, smart=ativada)
2025-08-07 17:45:17.301 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 150}
2025-08-07 17:45:17.301 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 17:45:17.301 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 17:45:17.301 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 17:45:17.302 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 17:45:17.302 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 17:45:17.302 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 17:45:17.302 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 17:45:17.302 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 17:45:17.303 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 17:45:17.303 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 17:45:17.304 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 17:45:17.304 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 17:45:17.305 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 17:45:17.305 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 17:45:17.306 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 17:45:17.306 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 3}
2025-08-07 17:45:17.906 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-07 17:45:17.906 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-07 17:45:17.909 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-07 17:45:17.909 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-07 17:45:17.909 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Fonte' mapeado: ID 392810
2025-08-07 17:45:17.909 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-07 17:45:17.909 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-07 17:45:17.910 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-07 17:45:18.493 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-07 17:45:18.493 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-07 17:45:18.493 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-07 17:45:18.494 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-07 17:45:18.494 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-07 17:45:18.495 | INFO     | app.teams.agents.crm:initialize:195 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-07 17:45:18.495 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-07 17:45:18.522 | INFO     | app.services.kommo_auto_sync:__init__:94 | ✅ KommoAutoSyncService inicializado
2025-08-07 17:45:18.523 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 17:45:18.523 | INFO     | app.teams.agents.crm_enhanced:__init__:43 | ✅ KommoEnhancedCRM inicializado com funcionalidades completas
2025-08-07 17:45:19.118 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-07 17:45:19.119 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-07 17:45:19.119 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-07 17:45:19.119 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-07 17:45:19.119 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Fonte' mapeado: ID 392810
2025-08-07 17:45:19.119 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-07 17:45:19.120 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-07 17:45:19.120 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-07 17:45:19.662 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-07 17:45:19.663 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-07 17:45:19.663 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-07 17:45:19.663 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-07 17:45:19.663 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-07 17:45:19.664 | INFO     | app.teams.agents.crm:initialize:195 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-07 17:45:19.664 | INFO     | app.services.kommo_auto_sync:initialize:103 | ✅ CRM Enhanced inicializado para auto-sync
2025-08-07 17:45:19.665 | INFO     | app.services.kommo_auto_sync:start:116 | 🔄 Iniciando sincronização automática com Kommo CRM
2025-08-07 17:45:19.665 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo Auto Sync pronto | Data: {'sync_interval': '30s', 'features': 'leads, tags, pipeline, fields'}
2025-08-07 17:45:19.688 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto
2025-08-07 17:45:19.689 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto | Data: {'check_interval': '1min', 'types': '30min, 24h'}
2025-08-07 17:45:19.689 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔥 Pré-aquecendo AgenticSDR (tentativa 1/3)...
2025-08-07 17:45:19.689 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-07 17:45:19.690 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-07 17:45:19.690 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-07 17:45:19.690 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-07 17:45:19.690 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-07 17:45:19.691 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-07 17:45:19.691 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-07 17:45:19.717 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-07 17:45:19.717 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-07 17:45:20.136 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-07 17:45:20.137 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 17:45:20.137 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 17:45:20.137 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 17:45:20.137 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 17:45:20.137 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 17:45:20.138 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 17:45:20.138 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 17:45:20.138 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 17:45:20.138 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 17:45:20.139 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 17:45:20.139 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 17:45:20.139 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 17:45:20.140 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 17:45:20.140 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 17:45:20.140 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 17:45:20.141 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-07 17:45:20.141 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-07 17:45:20.141 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ AgenticSDR singleton criado e pronto! pronto
2025-08-07 17:45:20.142 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AgenticSDR pronto | Data: {'status': 'pré-aquecido com sucesso'}
2025-08-07 17:45:20.142 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:40700 - "GET /health HTTP/1.1" 200 OK
2025-08-07 17:45:42.264 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-07 17:45:46.208 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 17:45:46.209 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:308 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T14:45:46.204Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 17:45:46.231 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 17:45:46.231 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:308 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T14:45:46.226Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 17:45:46.252 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-07 17:45:46.253 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'opa, tudo bem?', 'sender': '558182986181', 'type': 'text'}
2025-08-07 17:45:46.255 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 14}
2025-08-07 17:45:46.720 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 17:45:46.721 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:313 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T14:45:46.539Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 17:45:47.168 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 17:45:47.168 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:313 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T14:45:46.577Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49672 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 17:45:47.824 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-07 17:45:48.049 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 17:45:48.300 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: be6197a6-af8d-4c6f-aba7-29b2f2202f7f
2025-08-07 17:45:48.300 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: be6197a6-af8d-4c6f-aba7-29b2f2202f7f
2025-08-07 17:45:48.509 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 1 mensagens encontradas (limite solicitado: 100)
2025-08-07 17:45:48.509 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 1 mensagens disponíveis (menos que o limite de 100)
2025-08-07 17:45:48.511 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: be6197a6-af8d-4c6f-aba7-29b2f2202f7f
2025-08-07 17:45:48.511 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: be6197a6-af8d-4c6f-aba7-29b2f2202f7f
2025-08-07 17:45:48.722 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 1 mensagens encontradas (limite solicitado: 100)
2025-08-07 17:45:48.722 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 1 mensagens disponíveis (menos que o limite de 100)
2025-08-07 17:45:48.722 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 1 mensagens
2025-08-07 17:45:48.723 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 17:45:48.723 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: INITIAL_CONTACT
                    - Status: PENDING
                    
                    USER: opa, tudo bem?
                    
                    MENSAGEM ATUAL DO CLIENTE: opa, tudo bem?
                    
                    
                    Análise Contextual:
                    - Contexto Principal: initial_contact
             ...
2025-08-07 17:45:48.723 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 978 caracteres
2025-08-07 17:45:48.723 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ❌ Nenhum resultado multimodal incluído no prompt
2025-08-07 17:45:48.724 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun...
2025-08-07 17:45:48.724 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem instructions? True
2025-08-07 17:45:48.724 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem memory? True
2025-08-07 17:45:48.724 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem model? True
2025-08-07 17:45:51.048 | INFO     | app.services.kommo_auto_sync:sync_new_leads:187 | 📋 1 novos leads para sincronizar com Kommo
INFO:     10.11.0.4:49664 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     127.0.0.1:55204 - "GET /health HTTP/1.1" 200 OK
2025-08-07 17:45:54.381 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:346 | 📍 Lead 3850452 movido para estágio novo_lead
2025-08-07 17:45:54.382 | INFO     | app.services.kommo_auto_sync:_sync_single_lead:235 | ✅ Lead ed8fa930-42a0-4ff5-a41e-1cf29c72ff5b sincronizado com Kommo (ID: 3850452)
2025-08-07 17:45:54.818 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 17:45:54.818 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:308 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T14:45:54.803Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 17:45:54.829 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 17:45:54.829 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:308 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T14:45:54.817Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 17:45:54.836 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-07 17:45:54.837 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'preciso saber mais sobre os serviços de energia soalr de voces', 'sender': '558182986181', 'type': 'text'}
2025-08-07 17:45:55.121 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 17:45:55.122 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:313 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T14:45:55.115Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 17:45:55.168 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 17:45:55.168 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:313 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T14:45:55.163Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49664 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-07 17:46:02.367 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ agent.arun completou sem erro
2025-08-07 17:46:02.367 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Tipo do result: <class 'agno.run.response.RunResponse'>
2025-08-07 17:46:02.367 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result tem content? True
2025-08-07 17:46:02.368 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Atributos do result: ['content', 'content_type', 'thinking', 'reasoning_content', 'messages', 'metrics', 'model', 'model_provider', 'run_id', 'agent_id', 'agent_name', 'session_id', 'team_session_id', 'workflow_id', 'tools', 'formatted_tool_calls', 'images', 'videos', 'audio', 'response_audio', 'citations', 'extra_data', 'created_at', 'events', 'status']
2025-08-07 17:46:02.368 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Result não é None, tipo: RunResponse
2025-08-07 17:46:02.368 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 raw_response (primeiros 200 chars): <RESPOSTA_FINAL>Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?</RESPOSTA_FINAL>...
2025-08-07 17:46:02.368 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho raw_response: 174 caracteres
2025-08-07 17:46:02.614 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPr...
2025-08-07 17:46:02.614 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=174, primeiros 200 chars: <RESPOSTA_FINAL>Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?</RESPOSTA_FINAL>
2025-08-07 17:46:02.615 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=174, primeiros 200 chars: <RESPOSTA_FINAL>Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?</RESPOSTA_FINAL>
2025-08-07 17:46:07.864 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.13, 'message_length': 141, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 17:46:13.159 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 141, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 17:46:13.160 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Oii! Boa tarde! Meu nome é Helen Vieira, sou consu', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 17:46:13.160 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB0375F3B8CEEA08F81502F1214E587DDCCE474
2025-08-07 17:46:15.020 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 17:46:15.020 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:317 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:52656 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 17:46:15.882 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Follow-up de 30min agendado para 558182986181 às 15:16
2025-08-07 17:46:15.882 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Follow-up sequencial: 24h será agendado apenas se usuário não responder ao de 30min
2025-08-07 17:46:21.293 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:372 | 📝 1 leads atualizados para sincronizar
INFO:     127.0.0.1:35774 - "GET /health HTTP/1.1" 200 OK
INFO:     10.11.0.4:51580 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-07 17:46:24.990 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:215 | ✅ Tags adicionadas ao lead 3850452: []
2025-08-07 17:46:25.586 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:346 | 📍 Lead 3850452 movido para estágio novo_lead
2025-08-07 17:46:25.586 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:397 | 🔄 Lead ed8fa930-42a0-4ff5-a41e-1cf29c72ff5b atualizado no Kommo
INFO:     127.0.0.1:45546 - "GET /health HTTP/1.1" 200 OK
INFO:     10.11.0.4:50322 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     10.11.0.4:50322 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     10.11.0.4:50322 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     10.11.0.4:50322 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     10.11.0.4:50322 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     10.11.0.4:50352 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     10.11.0.4:50368 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     10.11.0.4:50336 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-07 17:47:15.495 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:50376 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-07 17:47:16.334 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 17:47:16.335 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:308 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T14:47:16.327Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:50376 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 17:47:16.350 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:50376 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-07 17:47:16.351 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'oi???', 'sender': '558182986181', 'type': 'text'}
2025-08-07 17:47:16.352 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 5}
2025-08-07 17:47:17.648 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 17:47:17.649 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:313 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T14:47:16.673Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:50376 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 17:47:17.650 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 17:47:17.650 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:313 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoGvhk0f9fO9Zn66PzikXYkdZuEqmM8TsuwTOFUQKCew&oe=68A1DECD&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T14:47:16.843Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:56626 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 17:47:18.994 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 17:47:19.625 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: be6197a6-af8d-4c6f-aba7-29b2f2202f7f
2025-08-07 17:47:19.626 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: be6197a6-af8d-4c6f-aba7-29b2f2202f7f
2025-08-07 17:47:19.866 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 3 mensagens encontradas (limite solicitado: 100)
2025-08-07 17:47:19.867 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 3 mensagens disponíveis (menos que o limite de 100)
2025-08-07 17:47:19.867 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: be6197a6-af8d-4c6f-aba7-29b2f2202f7f
2025-08-07 17:47:19.868 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: be6197a6-af8d-4c6f-aba7-29b2f2202f7f
2025-08-07 17:47:20.486 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 3 mensagens encontradas (limite solicitado: 100)
2025-08-07 17:47:20.486 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 3 mensagens disponíveis (menos que o limite de 100)
2025-08-07 17:47:20.486 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 3 mensagens
2025-08-07 17:47:20.486 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 17:47:20.487 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: INITIAL_CONTACT
                    - Status: PENDING
                    
                    USER: opa, tudo bem?
ASSISTANT: Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?
USER: oi???
                    
                    MENSAGEM ATUAL DO CLIENTE: oi?...
2025-08-07 17:47:20.487 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 1134 caracteres
2025-08-07 17:47:20.487 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ❌ Nenhum resultado multimodal incluído no prompt
2025-08-07 17:47:20.487 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun...
2025-08-07 17:47:20.487 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem instructions? True
2025-08-07 17:47:20.487 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem memory? True
2025-08-07 17:47:20.488 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem model? True
INFO:     127.0.0.1:48680 - "GET /health HTTP/1.1" 200 OK
2025-08-07 17:47:26.213 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:372 | 📝 1 leads atualizados para sincronizar
2025-08-07 17:47:28.619 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:346 | 📍 Lead 3850452 movido para estágio novo_lead
2025-08-07 17:47:28.620 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:397 | 🔄 Lead ed8fa930-42a0-4ff5-a41e-1cf29c72ff5b atualizado no Kommo
WARNING  MemoryDb not provided.  