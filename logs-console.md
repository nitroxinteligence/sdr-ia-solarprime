✅ Usando variáveis de ambiente do servidor (EasyPanel)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-04 17:04:18.364 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-04 17:04:18.368 | WARNING  | app.integrations.redis_client:connect:35 | Redis não disponível: Error -2 connecting to redis:6379. -2.. Sistema funcionará sem cache.
2025-08-04 17:04:18.369 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-04 17:04:18.663 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-04 17:04:18.663 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Buffer inicializado (timeout=30.0s, max=10)
2025-08-04 17:04:18.663 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-04 17:04:18.664 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=250 chars, smart=ativada)
2025-08-04 17:04:18.664 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 250}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 17:04:18.686 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 17:04:18.686 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-04 17:04:18.687 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-04 17:04:18.687 | INFO     | app.teams.sdr_team:__init__:107 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-04 17:04:18.687 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-04 17:04:18.687 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-04 17:04:18.687 | INFO     | app.teams.sdr_team:_initialize_agents:163 | 📅 Verificando CalendarAgent - enable_calendar_agent: True, enable_calendar_integration: True
2025-08-04 17:04:18.687 | INFO     | app.teams.sdr_team:_initialize_agents:166 | 📅 ATIVANDO CalendarAgent...
2025-08-04 17:04:18.688 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-04 17:04:18.689 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-04 17:04:18.689 | INFO     | app.teams.sdr_team:_initialize_agents:174 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-04 17:04:18.689 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-04 17:04:18.689 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 17:04:19.078 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-04 17:04:19.078 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-04 17:04:19.079 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 17:04:19.079 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-04 17:04:19.079 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-04 17:04:19.079 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-04 17:04:19.079 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-04 17:04:19.079 | INFO     | app.teams.sdr_team:initialize:308 | Team configurado sem memória (melhor estabilidade)
2025-08-04 17:04:19.495 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 17:04:19.496 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 17:04:19.496 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 6}
2025-08-04 17:04:20.098 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-04 17:04:20.098 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-04 17:04:20.098 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-04 17:04:20.098 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-04 17:04:20.098 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Fonte' mapeado: ID 392810
2025-08-04 17:04:20.099 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-04 17:04:20.099 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-04 17:04:20.099 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-04 17:04:20.710 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-04 17:04:20.710 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Em Negociação' mapeado: ID 89709591
2025-08-04 17:04:20.711 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-04 17:04:20.711 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-04 17:04:20.711 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-04 17:04:20.711 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Reunião Finalizada' mapeado: ID 89947527
2025-08-04 17:04:20.711 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-04 17:04:20.712 | INFO     | app.teams.agents.crm:initialize:159 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-04 17:04:20.712 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-04 17:04:20.735 | INFO     | app.services.kommo_auto_sync:__init__:53 | ✅ KommoAutoSyncService inicializado
2025-08-04 17:04:20.736 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 17:04:20.736 | INFO     | app.teams.agents.crm_enhanced:__init__:43 | ✅ KommoEnhancedCRM inicializado com funcionalidades completas
2025-08-04 17:04:21.359 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-04 17:04:21.359 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-04 17:04:21.359 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-04 17:04:21.360 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-04 17:04:21.360 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Fonte' mapeado: ID 392810
2025-08-04 17:04:21.360 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-04 17:04:21.360 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-04 17:04:21.360 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-04 17:04:21.954 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-04 17:04:21.954 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Em Negociação' mapeado: ID 89709591
2025-08-04 17:04:21.955 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-04 17:04:21.955 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-04 17:04:21.955 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-04 17:04:21.955 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Reunião Finalizada' mapeado: ID 89947527
2025-08-04 17:04:21.955 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-04 17:04:21.956 | INFO     | app.teams.agents.crm:initialize:159 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-04 17:04:21.956 | INFO     | app.services.kommo_auto_sync:initialize:62 | ✅ CRM Enhanced inicializado para auto-sync
2025-08-04 17:04:21.956 | INFO     | app.services.kommo_auto_sync:start:75 | 🔄 Iniciando sincronização automática com Kommo CRM
2025-08-04 17:04:21.956 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo Auto Sync pronto | Data: {'sync_interval': '30s', 'features': 'leads, tags, pipeline, fields'}
2025-08-04 17:04:21.981 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Calendar Sync Service pronto | Data: {'sync_interval': '5min', 'reminders': '30min, 2h, 24h'}
2025-08-04 17:04:22.002 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto
2025-08-04 17:04:22.003 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto | Data: {'check_interval': '1min', 'types': '30min, 24h'}
2025-08-04 17:04:22.003 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:44486 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:04:38.755 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:55494 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-04 17:04:39.015 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 17:04:39.015 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:04:39.009Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:55494 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 17:04:39.035 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:55494 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 17:04:39.037 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'oi', 'sender': '558182986181', 'type': 'text'}
2025-08-04 17:04:39.398 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 17:04:39.399 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFAU1VUzH-vQ7XhuvDg4xqyTZWhzi38L-8zKwRpy_BGJw&oe=689DEA4D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:04:39.392Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:55494 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 17:04:39.447 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 17:04:39.448 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFAU1VUzH-vQ7XhuvDg4xqyTZWhzi38L-8zKwRpy_BGJw&oe=689DEA4D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:04:39.442Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:55494 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 17:04:40.395 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:55494 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 17:04:40.401 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 17:04:40.402 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:55494 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
INFO:     127.0.0.1:36826 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:05:09.041 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 2}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 17:05:10.152 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 17:05:10.153 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: agentic_sdr_sessions
2025-08-04 17:05:10.153 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-04 17:05:10.153 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-04 17:05:10.154 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-04 17:05:10.154 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-04 17:05:10.154 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 17:05:10.157 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base pronto | Data: {'status': 'ativo'}
2025-08-04 17:05:10.158 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-04 17:05:10.158 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-04 17:05:10.584 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 17:05:10.586 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 17:05:10.587 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-04 17:05:10.587 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-04 17:05:10.587 | INFO     | app.teams.sdr_team:__init__:107 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-04 17:05:10.588 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-04 17:05:10.588 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-04 17:05:10.588 | INFO     | app.teams.sdr_team:_initialize_agents:163 | 📅 Verificando CalendarAgent - enable_calendar_agent: True, enable_calendar_integration: True
2025-08-04 17:05:10.588 | INFO     | app.teams.sdr_team:_initialize_agents:166 | 📅 ATIVANDO CalendarAgent...
2025-08-04 17:05:10.590 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-04 17:05:10.590 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-04 17:05:10.590 | INFO     | app.teams.sdr_team:_initialize_agents:174 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-04 17:05:10.590 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-04 17:05:10.591 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 17:05:10.593 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-04 17:05:10.594 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-04 17:05:10.594 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 17:05:10.594 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-04 17:05:10.594 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-04 17:05:10.595 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-04 17:05:10.595 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-04 17:05:10.595 | INFO     | app.teams.sdr_team:initialize:308 | Team configurado sem memória (melhor estabilidade)
2025-08-04 17:05:11.004 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 17:05:11.005 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 17:05:11.005 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-04 17:05:11.005 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-04 17:05:11.507 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 17:05:11.733 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:05:11.734 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:05:12.528 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 45 mensagens encontradas
2025-08-04 17:05:12.530 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:05:12.530 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:05:13.296 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 45 mensagens encontradas
2025-08-04 17:05:13.296 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 45 mensagens
2025-08-04 17:05:13.296 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-04 17:05:13.297 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 45 mensagens, quality=excellent, score=0.64
2025-08-04 17:05:16.842 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
INFO:     127.0.0.1:60376 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 17:05:34.967 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Eita, Mateus, peço mil desculpas pelo nosso desencontro! Tive um imprevisto aqui e a nossa reunião d...
2025-08-04 17:05:34.986 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem dividida em 2 partes | Data: {'phone': '558182986181', 'original_length': 310}
2025-08-04 17:05:42.289 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 226, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:05:42.290 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Eita, Mateus, peço mil desculpas pelo nosso desenc', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:05:42.290 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 1/2 enviado. ID: 3EB07AF3925F71DACC199ED63CBBC8B740F7AE9E
2025-08-04 17:05:42.502 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 17:05:42.503 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:34568 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 17:05:43.264 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:34568 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 17:05:50.391 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 83, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:05:50.391 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Se ainda tiver um tempinho, podemos bater um papo ', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:05:50.391 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 2/2 enviado. ID: 3EB067B9AD029D86E46234CCAE2C06F533CE2B10
2025-08-04 17:05:51.092 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 17:05:51.093 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:34584 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 17:05:51.333 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:34584 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:38498 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:06:04.385 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:39416 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-04 17:06:14.598 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:35234 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-04 17:06:21.102 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 17:06:21.102 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:06:21.054Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:35250 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 17:06:21.123 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:35250 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 17:06:21.124 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'quero agendar uma reuniao imediatamente para hoje as 16h meu email é: matheuscdsgn@gmail.com AGENDE', 'sender': '558182986181', 'type': 'text'}
2025-08-04 17:06:21.442 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 17:06:21.442 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFAU1VUzH-vQ7XhuvDg4xqyTZWhzi38L-8zKwRpy_BGJw&oe=689DEA4D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:06:21.435Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:35250 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 17:06:21.522 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 17:06:21.522 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFAU1VUzH-vQ7XhuvDg4xqyTZWhzi38L-8zKwRpy_BGJw&oe=689DEA4D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:06:21.516Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:35250 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 17:06:22.503 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:35250 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 17:06:22.512 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 17:06:22.513 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:35250 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 17:06:22.520 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:35250 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 17:06:22.529 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 17:06:22.529 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:35250 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
INFO:     127.0.0.1:37952 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:06:51.126 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 99}
2025-08-04 17:06:57.395 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 17:06:57.641 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:06:57.641 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:06:58.426 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 47 mensagens encontradas
2025-08-04 17:06:58.428 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:06:58.428 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:06:59.221 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 47 mensagens encontradas
2025-08-04 17:06:59.221 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 47 mensagens
2025-08-04 17:06:59.222 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:771 | 📅 CALENDÁRIO DETECTADO - Score: 0.8
2025-08-04 17:06:59.222 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:772 | 📅 Mensagem: quero agendar uma reuniao imediatamente para hoje as 16h meu email é: matheuscdsgn@gmail.com AGENDE...
2025-08-04 17:06:59.222 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:773 | 📅 Agent recomendado: CalendarAgent
2025-08-04 17:06:59.222 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: Chamar SDR Team - CalendarAgent | Data: {'recommended_agent': 'CalendarAgent', 'decision_score': 0.8}
2025-08-04 17:06:59.223 | INFO     | app.teams.sdr_team:process_message_with_context:595 | 📅 AGENT RECOMENDADO: CalendarAgent
2025-08-04 17:06:59.223 | INFO     | app.teams.sdr_team:process_message_with_context:596 | 📅 Razão: Score de complexidade: 0.80. 🗓️ Solicitação de agendamento detectada - Ativando CalendarAgent
2025-08-04 17:06:59.223 | INFO     | app.teams.sdr_team:process_message_with_context:600 | 🗓️ ATIVANDO CalendarAgent para processar solicitação de agendamento!
2025-08-04 17:06:59.223 | INFO     | app.teams.sdr_team:process_message_with_context:602 | ✅ CalendarAgent está disponível e será usado
INFO:     127.0.0.1:56192 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:07:04.475 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 4.95, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
/root/.local/lib/python3.11/site-packages/agno/agent/agent.py:1213: RuntimeWarning: coroutine 'CalendarAgent._create_tool_wrappers.<locals>.check_availability_tool' was never awaited
  model_response: ModelResponse = await self.model.aresponse(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2025-08-04 17:07:23.238 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:320 | 📝 1 leads atualizados para sincronizar
2025-08-04 17:07:25.141 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:204 | ✅ Tags adicionadas ao lead 1871632: []
INFO:     10.11.0.4:54890 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-04 17:07:26.090 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:294 | 📍 Lead 1871632 movido para estágio novo_lead
2025-08-04 17:07:26.091 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:345 | 🔄 Lead ff634d3a-2c95-46d1-8e6e-c088f69529c0 atualizado no Kommo
INFO:     127.0.0.1:45050 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 17:07:37.376 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Perfeito, Mateus! Deixa só eu localizar seu cadastro aqui rapidinho com seu e-mail para a gente já c...
2025-08-04 17:07:44.687 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 186, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:07:44.688 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Perfeito, Mateus! Deixa só eu localizar seu cadast', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:07:44.688 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB0830E71D66917FA6245015EF6C8D00E6FDEC1
2025-08-04 17:07:45.373 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 17:07:45.373 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:35980 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 17:07:45.901 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:35980 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:54198 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:08:07.470 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:46148 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-04 17:08:08.004 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 17:08:08.005 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:08:07.995Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:46148 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 17:08:08.028 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:46148 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 17:08:08.029 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'ok', 'sender': '558182986181', 'type': 'text'}
2025-08-04 17:08:08.384 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 17:08:08.385 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFAU1VUzH-vQ7XhuvDg4xqyTZWhzi38L-8zKwRpy_BGJw&oe=689DEA4D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:08:08.378Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:46148 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 17:08:08.448 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 17:08:08.449 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFAU1VUzH-vQ7XhuvDg4xqyTZWhzi38L-8zKwRpy_BGJw&oe=689DEA4D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:08:08.442Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:46148 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 17:08:09.469 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:46148 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 17:08:09.475 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 17:08:09.475 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:46148 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 17:08:26.321 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:320 | 📝 1 leads atualizados para sincronizar
INFO:     10.11.0.4:42278 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-04 17:08:28.259 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:204 | ✅ Tags adicionadas ao lead 1871632: []
2025-08-04 17:08:28.989 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:294 | 📍 Lead 1871632 movido para estágio novo_lead
2025-08-04 17:08:28.990 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:345 | 🔄 Lead ff634d3a-2c95-46d1-8e6e-c088f69529c0 atualizado no Kommo
INFO:     127.0.0.1:50148 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:08:38.030 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 2}
2025-08-04 17:08:39.818 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 17:08:40.040 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:08:40.040 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:08:40.806 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 49 mensagens encontradas
2025-08-04 17:08:40.808 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:08:40.809 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:08:41.590 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 49 mensagens encontradas
2025-08-04 17:08:41.590 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 49 mensagens
2025-08-04 17:08:41.591 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-04 17:08:41.591 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 49 mensagens, quality=excellent, score=0.68
2025-08-04 17:08:44.831 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
WARNING  MemoryDb not provided.                                                 
INFO:     127.0.0.1:50042 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 17:09:14.569 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Prontinho Mateus, tudo certo agora! Nossa reunião está confirmadíssima para hoje às 16h. Peço descul...
2025-08-04 17:09:14.570 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem dividida em 2 partes | Data: {'phone': '558182986181', 'original_length': 375}
2025-08-04 17:09:21.878 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 222, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:09:21.879 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Prontinho Mateus, tudo certo agora! Nossa reunião ', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:09:21.879 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 1/2 enviado. ID: 3EB002F5B87F449FD8C6D96356B81BB764C6FD40
2025-08-04 17:09:22.093 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 17:09:22.093 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:51322 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 17:09:22.970 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:51322 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 17:09:29.213 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:320 | 📝 1 leads atualizados para sincronizar
INFO:     10.11.0.4:41280 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-04 17:09:31.023 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:204 | ✅ Tags adicionadas ao lead 1871632: []
2025-08-04 17:09:31.134 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 152, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:09:31.134 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Já estou enviando o convite do Google Calendar par', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:09:31.135 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 2/2 enviado. ID: 3EB08C4A04E4245F08F93E930996EE8AF1873DBD
2025-08-04 17:09:32.591 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 17:09:32.591 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:41280 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
INFO:     127.0.0.1:57606 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:09:33.204 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:41292 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 17:09:33.600 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:294 | 📍 Lead 1871632 movido para estágio novo_lead
2025-08-04 17:09:33.600 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:345 | 🔄 Lead ff634d3a-2c95-46d1-8e6e-c088f69529c0 atualizado no Kommo
INFO:     127.0.0.1:40844 - "GET /health HTTP/1.1" 200 OK