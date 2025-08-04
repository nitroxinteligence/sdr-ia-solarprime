✅ Usando variáveis de ambiente do servidor (EasyPanel)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-04 17:40:18.625 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-04 17:40:18.779 | WARNING  | app.integrations.redis_client:connect:35 | Redis não disponível: Error -2 connecting to redis:6379. -2.. Sistema funcionará sem cache.
2025-08-04 17:40:18.780 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-04 17:40:19.395 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-04 17:40:19.395 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Buffer inicializado (timeout=30.0s, max=10)
2025-08-04 17:40:19.395 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-04 17:40:19.396 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=250 chars, smart=ativada)
2025-08-04 17:40:19.396 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 250}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 17:40:19.416 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 17:40:19.417 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-04 17:40:19.417 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-04 17:40:19.417 | INFO     | app.teams.sdr_team:__init__:108 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-04 17:40:19.418 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-04 17:40:19.418 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-04 17:40:19.418 | INFO     | app.teams.sdr_team:_initialize_agents:164 | 📅 Verificando CalendarAgent - enable_calendar_agent: True, enable_calendar_integration: True
2025-08-04 17:40:19.418 | INFO     | app.teams.sdr_team:_initialize_agents:167 | 📅 ATIVANDO CalendarAgent...
2025-08-04 17:40:19.419 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-04 17:40:19.420 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-04 17:40:19.420 | INFO     | app.teams.sdr_team:_initialize_agents:175 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-04 17:40:19.420 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-04 17:40:19.421 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 17:40:19.769 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-04 17:40:19.769 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-04 17:40:19.769 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 17:40:19.770 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-04 17:40:19.770 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-04 17:40:19.770 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-04 17:40:19.770 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-04 17:40:19.771 | INFO     | app.teams.sdr_team:initialize:309 | Team configurado sem memória (melhor estabilidade)
2025-08-04 17:40:20.182 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 17:40:20.182 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 17:40:20.183 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 6}
2025-08-04 17:40:20.893 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-04 17:40:20.893 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-04 17:40:20.893 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-04 17:40:20.893 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-04 17:40:20.894 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Fonte' mapeado: ID 392810
2025-08-04 17:40:20.894 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-04 17:40:20.894 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-04 17:40:20.895 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-04 17:40:21.542 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-04 17:40:21.542 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Em Negociação' mapeado: ID 89709591
2025-08-04 17:40:21.542 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-04 17:40:21.542 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-04 17:40:21.543 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-04 17:40:21.543 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Reunião Finalizada' mapeado: ID 89947527
2025-08-04 17:40:21.543 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-04 17:40:21.543 | INFO     | app.teams.agents.crm:initialize:159 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-04 17:40:21.544 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-04 17:40:21.570 | INFO     | app.services.kommo_auto_sync:__init__:53 | ✅ KommoAutoSyncService inicializado
2025-08-04 17:40:21.571 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 17:40:21.571 | INFO     | app.teams.agents.crm_enhanced:__init__:43 | ✅ KommoEnhancedCRM inicializado com funcionalidades completas
2025-08-04 17:40:22.274 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-04 17:40:22.275 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-04 17:40:22.275 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-04 17:40:22.275 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-04 17:40:22.275 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Fonte' mapeado: ID 392810
2025-08-04 17:40:22.275 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-04 17:40:22.276 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-04 17:40:22.276 | INFO     | app.teams.agents.crm:_fetch_custom_fields:195 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-04 17:40:22.887 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-04 17:40:22.888 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Em Negociação' mapeado: ID 89709591
2025-08-04 17:40:22.888 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-04 17:40:22.888 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-04 17:40:22.888 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-04 17:40:22.888 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Reunião Finalizada' mapeado: ID 89947527
2025-08-04 17:40:22.889 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:230 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-04 17:40:22.889 | INFO     | app.teams.agents.crm:initialize:159 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-04 17:40:22.890 | INFO     | app.services.kommo_auto_sync:initialize:62 | ✅ CRM Enhanced inicializado para auto-sync
2025-08-04 17:40:22.890 | INFO     | app.services.kommo_auto_sync:start:75 | 🔄 Iniciando sincronização automática com Kommo CRM
2025-08-04 17:40:22.890 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo Auto Sync pronto | Data: {'sync_interval': '30s', 'features': 'leads, tags, pipeline, fields'}
2025-08-04 17:40:22.916 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Calendar Sync Service pronto | Data: {'sync_interval': '5min', 'reminders': '30min, 2h, 24h'}
2025-08-04 17:40:22.941 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto
2025-08-04 17:40:22.942 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto | Data: {'check_interval': '1min', 'types': '30min, 24h'}
2025-08-04 17:40:22.942 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:48450 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:40:34.481 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 17:40:34.637 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 17:40:34.637 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 17:40:34.775 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 17:40:34.775 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 17:40:35.108 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 17:40:35.196 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 17:40:35.419 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 17:40:35.419 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 17:40:38.940 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-04 17:40:40.438 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-04 17:40:42.214 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 17:40:42.214 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, {'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:40:27.873Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 17:40:42.740 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 17:40:42.740 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFAU1VUzH-vQ7XhuvDg4xqyTZWhzi38L-8zKwRpy_BGJw&oe=689DEA4D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:40:28.319Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 17:40:42.840 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 17:40:42.841 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFAU1VUzH-vQ7XhuvDg4xqyTZWhzi38L-8zKwRpy_BGJw&oe=689DEA4D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:40:28.253Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 17:40:42.910 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:55446 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 17:40:42.911 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'Quero agendar uma reuniao imediatamente para hoje as 16h meu email é: matheuscdsgn@gmail.com AGENDE', 'sender': '558182986181', 'type': 'text'}
INFO:     127.0.0.1:40772 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:41:12.912 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 99}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 17:41:14.519 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 17:41:14.519 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: agentic_sdr_sessions
2025-08-04 17:41:14.519 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-04 17:41:14.520 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-04 17:41:14.520 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-04 17:41:14.520 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-04 17:41:14.520 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 17:41:14.523 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base pronto | Data: {'status': 'ativo'}
2025-08-04 17:41:14.524 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-04 17:41:14.525 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-04 17:41:14.929 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 17:41:14.931 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 17:41:14.931 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-04 17:41:14.931 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-04 17:41:14.931 | INFO     | app.teams.sdr_team:__init__:108 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-04 17:41:14.932 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-04 17:41:14.932 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-04 17:41:14.932 | INFO     | app.teams.sdr_team:_initialize_agents:164 | 📅 Verificando CalendarAgent - enable_calendar_agent: True, enable_calendar_integration: True
2025-08-04 17:41:14.932 | INFO     | app.teams.sdr_team:_initialize_agents:167 | 📅 ATIVANDO CalendarAgent...
2025-08-04 17:41:14.933 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-04 17:41:14.933 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-04 17:41:14.933 | INFO     | app.teams.sdr_team:_initialize_agents:175 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-04 17:41:14.934 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-04 17:41:14.934 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 17:41:14.936 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-04 17:41:14.937 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-04 17:41:14.937 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 17:41:14.937 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-04 17:41:14.937 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-04 17:41:14.937 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-04 17:41:14.938 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-04 17:41:14.938 | INFO     | app.teams.sdr_team:initialize:309 | Team configurado sem memória (melhor estabilidade)
2025-08-04 17:41:15.369 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 17:41:15.369 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 17:41:15.369 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-04 17:41:15.370 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-04 17:41:19.079 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 17:41:19.306 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:41:19.306 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:41:20.093 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 53 mensagens encontradas
2025-08-04 17:41:20.095 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:41:20.095 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:41:20.881 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 53 mensagens encontradas
2025-08-04 17:41:20.881 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 53 mensagens
2025-08-04 17:41:20.882 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:773 | 📅 CALENDÁRIO DETECTADO - Score: 0.8
2025-08-04 17:41:20.882 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:774 | 📅 Mensagem: Quero agendar uma reuniao imediatamente para hoje as 16h meu email é: matheuscdsgn@gmail.com AGENDE...
2025-08-04 17:41:20.882 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:775 | 📅 Agent recomendado: CalendarAgent
2025-08-04 17:41:20.882 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: Chamar SDR Team - CalendarAgent | Data: {'recommended_agent': 'CalendarAgent', 'decision_score': 0.8}
2025-08-04 17:41:20.882 | INFO     | app.teams.sdr_team:process_message_with_context:596 | 📅 AGENT RECOMENDADO: CalendarAgent
2025-08-04 17:41:20.882 | INFO     | app.teams.sdr_team:process_message_with_context:597 | 📅 Razão: Score de complexidade: 0.80. 🗓️ Solicitação de agendamento detectada - Ativando CalendarAgent
2025-08-04 17:41:20.883 | INFO     | app.teams.sdr_team:process_message_with_context:601 | 🗓️ ATIVANDO CalendarAgent para processar solicitação de agendamento!
2025-08-04 17:41:20.883 | INFO     | app.teams.sdr_team:process_message_with_context:603 | ✅ CalendarAgent está disponível e será usado
2025-08-04 17:41:26.164 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 4.95, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
INFO:     127.0.0.1:57350 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 17:41:57.156 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Que massa! Vamos agendar isso agora mesmo para hoje às 16h. Para eu enviar o convite certinho, me co...
2025-08-04 17:42:01.209 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 215, 'delay_used': 1.73, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:42:01.210 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Que massa! Vamos agendar isso agora mesmo para hoj', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:42:01.210 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB03A150B7C4D5BCD9684B99AE3E3153A102CA7
2025-08-04 17:42:01.923 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 17:42:01.923 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:49854 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 17:42:02.314 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:49854 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:51414 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:42:16.760 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:51052 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-04 17:42:18.127 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 17:42:18.127 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, {'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:42:18.120Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:51052 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 17:42:18.143 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:51052 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 17:42:18.144 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'está certo', 'sender': '558182986181', 'type': 'text'}
2025-08-04 17:42:18.506 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 17:42:18.506 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFAU1VUzH-vQ7XhuvDg4xqyTZWhzi38L-8zKwRpy_BGJw&oe=689DEA4D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:42:18.500Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:51052 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 17:42:18.539 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 17:42:18.540 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AFAU1VUzH-vQ7XhuvDg4xqyTZWhzi38L-8zKwRpy_BGJw&oe=689DEA4D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T14:42:18.534Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:51052 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 17:42:19.533 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:51052 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 17:42:19.540 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 17:42:19.541 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:51052 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 17:42:24.683 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:320 | 📝 1 leads atualizados para sincronizar
2025-08-04 17:42:26.913 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:204 | ✅ Tags adicionadas ao lead 1871632: []
INFO:     10.11.0.4:45930 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-04 17:42:27.743 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:294 | 📍 Lead 1871632 movido para estágio novo_lead
2025-08-04 17:42:27.743 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:345 | 🔄 Lead ff634d3a-2c95-46d1-8e6e-c088f69529c0 atualizado no Kommo
INFO:     127.0.0.1:53292 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:42:48.144 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 10}
2025-08-04 17:42:49.741 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 17:42:49.957 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:42:49.957 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:42:50.729 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 55 mensagens encontradas
2025-08-04 17:42:50.731 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:42:50.731 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 17:42:51.513 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 55 mensagens encontradas
2025-08-04 17:42:51.513 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 55 mensagens
2025-08-04 17:42:51.514 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-04 17:42:51.514 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 50 mensagens, quality=excellent, score=0.61
2025-08-04 17:42:54.758 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
INFO:     127.0.0.1:52138 - "GET /health HTTP/1.1" 200 OK
2025-08-04 17:43:27.957 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:320 | 📝 1 leads atualizados para sincronizar
2025-08-04 17:43:30.197 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:204 | ✅ Tags adicionadas ao lead 1871632: []
INFO:     10.11.0.4:35712 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-04 17:43:30.783 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:294 | 📍 Lead 1871632 movido para estágio novo_lead
2025-08-04 17:43:30.784 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:345 | 🔄 Lead ff634d3a-2c95-46d1-8e6e-c088f69529c0 atualizado no Kommo
INFO:     127.0.0.1:40582 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 17:43:45.296 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Nenhuma resposta gerada, usando fallback
2025-08-04 17:43:45.297 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Olá! Sou a Helen da Solar Prime 😊 Vi sua mensagem e adoraria ajudar! Você tem interesse em economiza...
2025-08-04 17:43:52.599 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 136, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:43:52.600 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Olá! Sou a Helen da Solar Prime 😊 Vi sua mensagem ', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 17:43:52.600 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB0DFE45C384E5469DB99177A2A8825BBB5E8F1
2025-08-04 17:43:53.478 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 17:43:53.478 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:46778 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 17:43:53.550 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:46778 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK