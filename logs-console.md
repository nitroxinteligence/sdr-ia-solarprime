✅ Usando variáveis de ambiente do servidor (EasyPanel)
2025-08-08 02:45:31.240 | INFO     | app.services.knowledge_service:__init__:33 | ✅ KnowledgeService inicializado (versão simplificada)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-08 02:45:32.064 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-08 02:45:32.069 | INFO     | app.integrations.redis_client:connect:39 | ✅ Conectado ao Redis com sucesso! URL: redis_redis:6379
2025-08-08 02:45:32.069 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-08 02:45:32.889 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-08 02:45:32.890 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buffer Inteligente inicializado (timeout=30.0s, max=10)
2025-08-08 02:45:32.890 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-08 02:45:32.890 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=200 chars, smart=ativada)
2025-08-08 02:45:32.890 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 200}
2025-08-08 02:45:32.890 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-08 02:45:32.891 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-08 02:45:32.891 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-08 02:45:32.891 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-08 02:45:32.891 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-08 02:45:32.891 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-08 02:45:32.891 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-08 02:45:32.891 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-08 02:45:32.892 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-08 02:45:32.892 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-08 02:45:32.892 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-08 02:45:32.893 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-08 02:45:32.893 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-08 02:45:32.893 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-08 02:45:32.893 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-08 02:45:32.893 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 3}
2025-08-08 02:45:33.519 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-08 02:45:33.519 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-08 02:45:33.519 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-08 02:45:33.520 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-08 02:45:33.520 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Fonte' mapeado: ID 392810
2025-08-08 02:45:33.520 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-08 02:45:33.520 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-08 02:45:33.520 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-08 02:45:34.018 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-08 02:45:34.019 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-08 02:45:34.019 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-08 02:45:34.019 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-08 02:45:34.019 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-08 02:45:34.020 | INFO     | app.teams.agents.crm:initialize:195 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-08 02:45:34.020 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-08 02:45:34.047 | INFO     | app.services.kommo_auto_sync:__init__:101 | ✅ KommoAutoSyncService inicializado
2025-08-08 02:45:34.048 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-08 02:45:34.048 | INFO     | app.teams.agents.crm_enhanced:__init__:43 | ✅ KommoEnhancedCRM inicializado com funcionalidades completas
2025-08-08 02:45:34.673 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-08 02:45:34.673 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-08 02:45:34.673 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-08 02:45:34.673 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-08 02:45:34.674 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Fonte' mapeado: ID 392810
2025-08-08 02:45:34.674 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-08 02:45:34.674 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-08 02:45:34.674 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-08 02:45:35.201 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-08 02:45:35.201 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-08 02:45:35.202 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-08 02:45:35.202 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-08 02:45:35.202 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-08 02:45:35.202 | INFO     | app.teams.agents.crm:initialize:195 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-08 02:45:35.203 | INFO     | app.services.kommo_auto_sync:initialize:110 | ✅ CRM Enhanced inicializado para auto-sync
2025-08-08 02:45:35.203 | INFO     | app.services.kommo_auto_sync:start:123 | 🔄 Iniciando sincronização automática com Kommo CRM
2025-08-08 02:45:35.203 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo Auto Sync pronto | Data: {'sync_interval': '30s', 'features': 'leads, tags, pipeline, fields'}
2025-08-08 02:45:35.226 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto
2025-08-08 02:45:35.227 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto | Data: {'check_interval': '1min', 'types': '30min, 24h'}
2025-08-08 02:45:35.227 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔥 Pré-aquecendo AgenticSDR (tentativa 1/3)...
2025-08-08 02:45:35.227 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-08 02:45:35.227 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-08 02:45:35.228 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-08 02:45:35.228 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-08 02:45:35.228 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-08 02:45:35.228 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-08 02:45:35.228 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-08 02:45:35.252 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-08 02:45:35.253 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-08 02:45:36.057 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-08 02:45:36.058 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-08 02:45:36.058 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-08 02:45:36.058 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-08 02:45:36.058 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-08 02:45:36.058 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-08 02:45:36.059 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-08 02:45:36.059 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-08 02:45:36.059 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-08 02:45:36.059 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-08 02:45:36.060 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-08 02:45:36.060 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-08 02:45:36.060 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-08 02:45:36.061 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-08 02:45:36.061 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-08 02:45:36.061 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-08 02:45:36.061 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-08 02:45:36.061 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-08 02:45:36.061 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Nova instância do AgenticSDR criada! pronto
2025-08-08 02:45:36.062 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AgenticSDR pronto | Data: {'status': 'pré-aquecido com sucesso'}
2025-08-08 02:45:36.062 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:55710 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:38586 - "GET /health HTTP/1.1" 200 OK
2025-08-08 02:46:13.644 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:45916 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-08 02:46:15.455 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-08 02:46:15.456 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:336 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, {'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T23:46:15.433Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:45916 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-08 02:46:15.479 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:45916 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-08 02:46:15.480 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'Tem pra amanha?', 'sender': '558182986181', 'type': 'text'}
2025-08-08 02:46:15.733 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-08 02:46:15.734 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:341 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AH6vasNHrtoUw3MmEyhcmd9kKEwfs1uxceNxiQtxTNZPw&oe=68A2878D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T23:46:15.726Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:45916 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-08 02:46:15.780 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-08 02:46:15.780 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:341 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AH6vasNHrtoUw3MmEyhcmd9kKEwfs1uxceNxiQtxTNZPw&oe=68A2878D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T23:46:15.774Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:45916 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-08 02:46:22.484 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 15}
2025-08-08 02:46:23.678 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-08 02:46:23.679 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-08 02:46:23.679 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-08 02:46:23.679 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-08 02:46:23.680 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-08 02:46:23.680 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-08 02:46:23.680 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-08 02:46:23.681 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-08 02:46:23.681 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-08 02:46:24.097 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-08 02:46:24.098 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-08 02:46:24.098 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-08 02:46:24.098 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-08 02:46:24.098 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-08 02:46:24.098 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-08 02:46:24.098 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-08 02:46:24.098 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-08 02:46:24.098 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-08 02:46:24.099 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-08 02:46:24.099 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-08 02:46:24.099 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-08 02:46:24.099 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-08 02:46:24.100 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-08 02:46:24.100 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-08 02:46:24.100 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-08 02:46:24.100 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-08 02:46:24.100 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-08 02:46:24.100 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Nova instância do AgenticSDR criada! pronto
2025-08-08 02:46:24.101 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversa validada - ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f, Phone: 558182986181
2025-08-08 02:46:25.669 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 WEBHOOK: Usando conversation_id=09c7fc7e-a847-43c2-a06b-761a2acd493f para phone=558182986181
2025-08-08 02:46:25.669 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chamando process_message com conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 02:46:25.885 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=558182986181
2025-08-08 02:46:25.885 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-08 02:46:26.110 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 02:46:26.110 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 02:46:27.823 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-08 02:46:27.823 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 02:46:27.823 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 55
2025-08-08 02:46:27.823 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-08 02:46:27.823 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-08T02:46:24.101261+00:00 - user
2025-08-08 02:46:27.824 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-08 02:46:27.824 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 55 mensagens disponíveis (menos que o limite de 100)
2025-08-08 02:46:27.828 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 02:46:27.828 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 02:46:27.828 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 02:46:29.815 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-08 02:46:29.815 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-08 02:46:29.815 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 55
2025-08-08 02:46:29.815 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-08 02:46:29.816 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-08T02:46:24.101261+00:00 - user
2025-08-08 02:46:29.816 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-08 02:46:29.816 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 55 mensagens disponíveis (menos que o limite de 100)
2025-08-08 02:46:29.816 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ HISTÓRICO FINAL: 55 mensagens carregadas
2025-08-08 02:46:29.816 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: Chamar SDR Team - QualificationAgent | Data: {'recommended_agent': 'QualificationAgent', 'decision_score': 0.3}
2025-08-08 02:46:29.817 | INFO     | app.teams.sdr_team:process_message_with_context:668 | 📅 AGENT RECOMENDADO: QualificationAgent
2025-08-08 02:46:29.817 | INFO     | app.teams.sdr_team:process_message_with_context:669 | 📅 Razão: Score de complexidade: 0.30. Lead de alto valor detectado
2025-08-08 02:46:37.501 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:379 | 📝 1 leads atualizados para sincronizar
2025-08-08 02:46:40.087 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:353 | 📍 Lead 3866108 movido para estágio novo_lead
2025-08-08 02:46:40.088 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:404 | 🔄 Lead d665126a-6e16-4839-a91c-bd1e4fca23f5 atualizado no Kommo
INFO:     127.0.0.1:47262 - "GET /health HTTP/1.1" 200 OK
2025-08-08 02:46:50.192 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Timeout na personalização após 15s, usando resposta original
2025-08-08 02:46:50.440 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: A equipe do SDR Solar Prime Team está verificando a disponibilidade para amanhã.

Para que eu possa ...
2025-08-08 02:46:50.442 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=250, primeiros 200 chars: A equipe do SDR Solar Prime Team está verificando a disponibilidade para amanhã.

Para que eu possa verificar a disponibilidade para amanhã, por favor, me informe a data completa de amanhã (incluindo 
2025-08-08 02:46:50.443 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em extract_final_response: 🚨 TAGS <RESPOSTA_FINAL> NÃO ENCONTRADAS - BLOQUEANDO VAZAMENTO | Data: {'component': 'extract_final_response'}
2025-08-08 02:46:50.443 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em extract_final_response: 📝 Conteúdo original (primeiros 200 chars): A equipe do SDR Solar Prime Team está verificando a disponibilidade para amanhã.

Para que eu possa verificar a disponibilidade para amanhã, por favor, me informe a data completa de amanhã (incluindo ... | Data: {'component': 'extract_final_response'}
2025-08-08 02:46:50.443 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ 🔒 Usando resposta segura para evitar vazamento de raciocínio interno
2025-08-08 02:46:50.444 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=250, primeiros 200 chars: A equipe do SDR Solar Prime Team está verificando a disponibilidade para amanhã.

Para que eu possa verificar a disponibilidade para amanhã, por favor, me informe a data completa de amanhã (incluindo 
2025-08-08 02:46:50.445 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em extract_final_response: 🚨 TAGS <RESPOSTA_FINAL> NÃO ENCONTRADAS - BLOQUEANDO VAZAMENTO | Data: {'component': 'extract_final_response'}
2025-08-08 02:46:50.445 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em extract_final_response: 📝 Conteúdo original (primeiros 200 chars): A equipe do SDR Solar Prime Team está verificando a disponibilidade para amanhã.

Para que eu possa verificar a disponibilidade para amanhã, por favor, me informe a data completa de amanhã (incluindo ... | Data: {'component': 'extract_final_response'}
2025-08-08 02:46:50.445 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ 🔒 Usando resposta segura para evitar vazamento de raciocínio interno
2025-08-08 02:46:50.445 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Resposta completa antes de dividir: Oi! Desculpe, estou processando sua mensagem. Me dê só um minutinho que já te respondo!
2025-08-08 02:46:50.446 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho: 87 chars