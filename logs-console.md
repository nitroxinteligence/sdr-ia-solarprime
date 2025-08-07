2025-08-07 18:59:03.966 | INFO     | app.services.knowledge_service:__init__:33 | ✅ KnowledgeService inicializado (versão simplificada)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-07 18:59:04.826 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-07 18:59:04.830 | INFO     | app.integrations.redis_client:connect:39 | ✅ Conectado ao Redis com sucesso! URL: redis_redis:6379
2025-08-07 18:59:04.831 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-07 18:59:05.287 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-07 18:59:05.287 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buffer Inteligente inicializado (timeout=30.0s, max=10)
2025-08-07 18:59:05.287 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-07 18:59:05.287 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=150 chars, smart=ativada)
2025-08-07 18:59:05.288 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 150}
2025-08-07 18:59:05.288 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 18:59:05.288 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 18:59:05.288 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 18:59:05.288 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 18:59:05.288 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 18:59:05.289 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 18:59:05.289 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 18:59:05.289 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 18:59:05.289 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 18:59:05.289 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 18:59:05.290 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 18:59:05.290 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 18:59:05.290 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 18:59:05.290 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 18:59:05.290 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 18:59:05.291 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 3}
2025-08-07 18:59:06.025 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-07 18:59:06.025 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-07 18:59:06.025 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-07 18:59:06.025 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-07 18:59:06.026 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Fonte' mapeado: ID 392810
2025-08-07 18:59:06.026 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-07 18:59:06.026 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-07 18:59:06.026 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-07 18:59:06.671 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-07 18:59:06.671 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-07 18:59:06.671 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-07 18:59:06.671 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-07 18:59:06.672 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-07 18:59:06.672 | INFO     | app.teams.agents.crm:initialize:195 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-07 18:59:06.673 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-07 18:59:06.698 | INFO     | app.services.kommo_auto_sync:__init__:94 | ✅ KommoAutoSyncService inicializado
2025-08-07 18:59:06.698 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 18:59:06.698 | INFO     | app.teams.agents.crm_enhanced:__init__:43 | ✅ KommoEnhancedCRM inicializado com funcionalidades completas
2025-08-07 18:59:07.421 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-07 18:59:07.421 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-07 18:59:07.421 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-07 18:59:07.422 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-07 18:59:07.422 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Fonte' mapeado: ID 392810
2025-08-07 18:59:07.422 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-07 18:59:07.422 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-07 18:59:07.422 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-07 18:59:07.951 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-07 18:59:07.952 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-07 18:59:07.952 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-07 18:59:07.952 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-07 18:59:07.952 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-07 18:59:07.953 | INFO     | app.teams.agents.crm:initialize:195 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-07 18:59:07.953 | INFO     | app.services.kommo_auto_sync:initialize:103 | ✅ CRM Enhanced inicializado para auto-sync
2025-08-07 18:59:07.954 | INFO     | app.services.kommo_auto_sync:start:116 | 🔄 Iniciando sincronização automática com Kommo CRM
2025-08-07 18:59:07.954 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo Auto Sync pronto | Data: {'sync_interval': '30s', 'features': 'leads, tags, pipeline, fields'}
2025-08-07 18:59:07.976 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto
2025-08-07 18:59:07.976 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto | Data: {'check_interval': '1min', 'types': '30min, 24h'}
2025-08-07 18:59:07.976 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔥 Pré-aquecendo AgenticSDR (tentativa 1/3)...
2025-08-07 18:59:07.977 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-07 18:59:07.977 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-07 18:59:07.977 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-07 18:59:07.978 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-07 18:59:07.978 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-07 18:59:07.978 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-07 18:59:07.978 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-07 18:59:08.005 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-07 18:59:08.005 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-07 18:59:08.422 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-07 18:59:08.423 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 18:59:08.423 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 18:59:08.423 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 18:59:08.424 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 18:59:08.424 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 18:59:08.424 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 18:59:08.424 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 18:59:08.424 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 18:59:08.425 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 18:59:08.425 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 18:59:08.425 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 18:59:08.426 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 18:59:08.426 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 18:59:08.426 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 18:59:08.426 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 18:59:08.426 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-07 18:59:08.427 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-07 18:59:08.427 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Nova instância do AgenticSDR criada! pronto
2025-08-07 18:59:08.427 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AgenticSDR pronto | Data: {'status': 'pré-aquecido com sucesso'}
2025-08-07 18:59:08.427 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:53100 - "GET /health HTTP/1.1" 200 OK
2025-08-07 18:59:13.626 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:34284 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-07 18:59:16.193 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 18:59:16.193 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:325 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T15:59:16.178Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:34284 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 18:59:16.236 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 18:59:16.236 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:325 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T15:59:16.229Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:34284 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 18:59:16.257 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:34284 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-07 18:59:16.258 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'energia com desconto, ja disse', 'sender': '558182986181', 'type': 'text'}
2025-08-07 18:59:16.260 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 30}
2025-08-07 18:59:16.715 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-07 18:59:16.715 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-07 18:59:16.715 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-07 18:59:16.715 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-07 18:59:16.715 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-07 18:59:16.716 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-07 18:59:16.716 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-07 18:59:16.717 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-07 18:59:16.717 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-07 18:59:17.495 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-07 18:59:17.496 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 18:59:17.496 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 18:59:17.496 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 18:59:17.497 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 18:59:17.497 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 18:59:17.497 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 18:59:17.497 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 18:59:17.497 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 18:59:17.498 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 18:59:17.498 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 18:59:17.498 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 18:59:17.499 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 18:59:17.499 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 18:59:17.499 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 18:59:17.499 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 18:59:17.499 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-07 18:59:17.500 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-07 18:59:17.500 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Nova instância do AgenticSDR criada! pronto
2025-08-07 18:59:17.501 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 18:59:17.501 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:330 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5VTTOyOZQzymi_JL1mKswk-gV0bgynKBjXnlereNYMw&oe=68A2170D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T15:59:16.543Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:34284 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 18:59:17.502 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversa validada - ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f, Phone: 558182986181
2025-08-07 18:59:17.502 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 18:59:17.502 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:330 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5VTTOyOZQzymi_JL1mKswk-gV0bgynKBjXnlereNYMw&oe=68A2170D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T15:59:16.584Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:34300 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 18:59:18.519 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 WEBHOOK: Usando conversation_id=09c7fc7e-a847-43c2-a06b-761a2acd493f para phone=558182986181
2025-08-07 18:59:18.519 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chamando process_message com conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:59:18.766 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=558182986181
2025-08-07 18:59:18.766 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 18:59:19.373 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:59:19.373 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:59:19.585 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 18:59:19.585 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:59:19.585 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 7
2025-08-07 18:59:19.586 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 18:59:19.586 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T18:59:17.503153+00:00 - user
2025-08-07 18:59:19.586 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 18:59:19.586 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 7 mensagens disponíveis (menos que o limite de 100)
2025-08-07 18:59:19.587 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:59:19.587 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:59:19.587 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:59:20.172 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 18:59:20.172 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:59:20.173 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 7
2025-08-07 18:59:20.173 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 18:59:20.173 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T18:59:17.503153+00:00 - user
2025-08-07 18:59:20.176 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 18:59:20.176 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 7 mensagens disponíveis (menos que o limite de 100)
2025-08-07 18:59:20.176 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ HISTÓRICO FINAL: 7 mensagens carregadas
2025-08-07 18:59:20.176 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 18:59:20.177 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: EM_QUALIFICACAO
                    - Status: PENDING
                    
                    USER: oi
ASSISTANT: Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?
USER: mateus
ASSISTANT: Então vamos lá, Mateus! Hoje na SolarPrime nós temos 4 soluções energét...
2025-08-07 18:59:20.177 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 1825 caracteres
2025-08-07 18:59:20.177 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ❌ Nenhum resultado multimodal incluído no prompt
2025-08-07 18:59:20.177 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Preparando para chamar agent.arun...
2025-08-07 18:59:20.177 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem instructions? True
2025-08-07 18:59:20.178 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem memory? True
2025-08-07 18:59:20.178 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem model? True
2025-08-07 18:59:20.178 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun com timeout de 30s...
WARNING  MemoryDb not provided.                                                 
INFO:     127.0.0.1:37166 - "GET /health HTTP/1.1" 200 OK
2025-08-07 18:59:40.934 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ agent.arun completou com sucesso
2025-08-07 18:59:40.934 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Tipo do result: <class 'agno.run.response.RunResponse'>
2025-08-07 18:59:40.934 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result tem content? True
2025-08-07 18:59:40.935 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Atributos do result: ['content', 'content_type', 'thinking', 'reasoning_content', 'messages', 'metrics', 'model', 'model_provider', 'run_id', 'agent_id', 'agent_name', 'session_id', 'team_session_id', 'workflow_id', 'tools', 'formatted_tool_calls', 'images', 'videos', 'audio', 'response_audio', 'citations', 'extra_data', 'created_at', 'events', 'status']
2025-08-07 18:59:40.935 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Result não é None, tipo: RunResponse
2025-08-07 18:59:40.935 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 raw_response (primeiros 200 chars): Mil perdões, meu sistema falhou aqui por um momento. Perfeito! Vamos resolver definitivamente o peso da conta de luz! Para eu entender o seu cenário, qual o valor aproximado da sua conta de luz mensal...
2025-08-07 18:59:40.935 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho raw_response: 201 caracteres
2025-08-07 18:59:41.152 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>Mil perdões, meu sistema falhou aqui por um momento. Perfeito! Vamos resolver defini...
2025-08-07 18:59:41.152 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=234, primeiros 200 chars: <RESPOSTA_FINAL>Mil perdões, meu sistema falhou aqui por um momento. Perfeito! Vamos resolver definitivamente o peso da conta de luz! Para eu entender o seu cenário, qual o valor aproximado da sua con
2025-08-07 18:59:41.153 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=234, primeiros 200 chars: <RESPOSTA_FINAL>Mil perdões, meu sistema falhou aqui por um momento. Perfeito! Vamos resolver definitivamente o peso da conta de luz! Para eu entender o seu cenário, qual o valor aproximado da sua con
2025-08-07 18:59:41.163 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem dividida em 2 partes | Data: {'phone': '558182986181', 'original_length': 201}
2025-08-07 18:59:43.519 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 2.72, 'message_length': 117, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 18:59:48.410 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 117, 'delay_used': 2.11, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 18:59:48.411 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Mil perdões, meu sistema falhou aqui por um moment', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 18:59:48.411 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 1/2 enviado. ID: 3EB0427838C2B122BC263131802582E1F63DFAC4
2025-08-07 18:59:48.416 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 18:59:48.417 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:58602 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 18:59:54.220 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.25, 'message_length': 83, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 18:59:59.641 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 83, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 18:59:59.642 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Para eu entender o seu cenário, qual o valor aprox', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 18:59:59.642 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 2/2 enviado. ID: 3EB05B79389ADF9C0874362CD649FDB53C46B00C
2025-08-07 19:00:00.342 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 19:00:00.343 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:52668 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 19:00:01.228 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Follow-up de 30min agendado para 558182986181 às 16:30
2025-08-07 19:00:01.228 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Follow-up sequencial: 24h será agendado apenas se usuário não responder ao de 30min
2025-08-07 19:00:01.229 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:52668 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:47360 - "GET /health HTTP/1.1" 200 OK
2025-08-07 19:00:20.196 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:48312 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:00:20.197 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 19:00:20.198 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:48316 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-07 19:00:20.198 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:48322 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:00:20.200 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 19:00:20.200 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:48338 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
INFO:     127.0.0.1:49146 - "GET /health HTTP/1.1" 200 OK
2025-08-07 19:01:06.378 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:49490 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:01:06.385 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 19:01:06.385 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:49490 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
INFO:     127.0.0.1:33050 - "GET /health HTTP/1.1" 200 OK
2025-08-07 19:01:12.321 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 19:01:12.321 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:325 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T16:01:12.308Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:47356 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 19:01:12.627 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 19:01:12.628 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:330 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5VTTOyOZQzymi_JL1mKswk-gV0bgynKBjXnlereNYMw&oe=68A2170D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T16:01:12.621Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:47356 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 19:01:14.397 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:47356 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-07 19:01:14.398 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Imagem recebida]', 'sender': '558182986181', 'type': 'text'}
2025-08-07 19:01:14.400 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 17}
2025-08-07 19:01:14.870 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-07 19:01:14.870 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-07 19:01:14.870 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-07 19:01:14.871 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-07 19:01:14.871 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-07 19:01:14.871 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-07 19:01:14.871 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-07 19:01:14.872 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-07 19:01:14.872 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-07 19:01:15.289 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-07 19:01:15.289 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 19:01:15.290 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 19:01:15.290 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 19:01:15.290 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 19:01:15.290 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 19:01:15.291 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 19:01:15.291 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 19:01:15.291 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 19:01:15.291 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 19:01:15.292 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 19:01:15.292 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 19:01:15.292 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 19:01:15.293 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 19:01:15.293 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 19:01:15.293 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 19:01:15.294 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-07 19:01:15.294 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-07 19:01:15.294 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Nova instância do AgenticSDR criada! pronto
2025-08-07 19:01:15.295 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 19:01:15.295 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:330 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5VTTOyOZQzymi_JL1mKswk-gV0bgynKBjXnlereNYMw&oe=68A2170D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T16:01:14.735Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:47356 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 19:01:15.296 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversa validada - ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f, Phone: 558182986181
2025-08-07 19:01:18.313 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📸 IMAGEM DETECTADA - Analisando estrutura...
2025-08-07 19:01:18.313 | INFO     | app.api.webhooks:process_message_with_agent:612 | Campos disponíveis na imageMessage: ['url', 'mimetype', 'fileSha256', 'fileLength', 'height', 'width', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'jpegThumbnail', 'contextInfo', 'firstScanSidecar', 'firstScanLength', 'scansSidecar', 'scanLengths', 'midQualityFileSha256', 'imageSourceType']
2025-08-07 19:01:18.314 | INFO     | app.api.webhooks:process_message_with_agent:619 | jpegThumbnail é string, tamanho: 960 chars
2025-08-07 19:01:18.314 | INFO     | app.api.webhooks:process_message_with_agent:620 | jpegThumbnail primeiros 50 chars: /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHB
2025-08-07 19:01:18.314 | INFO     | app.api.webhooks:process_message_with_agent:623 | jpegThumbnail parece ser base64 válido
2025-08-07 19:01:18.315 | INFO     | app.api.webhooks:process_message_with_agent:630 | mediaKey presente: 0pomlp/C41alGUXGXJRS...
2025-08-07 19:01:18.315 | INFO     | app.api.webhooks:process_message_with_agent:632 | directPath presente: /o1/v/t24/f2/m231/AQODWOx8Idn7nPIh46WNe6Ze7uKKlR81...
2025-08-07 19:01:18.315 | INFO     | app.api.webhooks:process_message_with_agent:634 | URL presente: https://mmg.whatsapp.net/o1/v/t24/f2/m231/AQODWOx8...
2025-08-07 19:01:18.316 | INFO     | app.api.webhooks:process_message_with_agent:655 | 🔐 Incluindo mediaKey para descriptografia
2025-08-07 19:01:18.316 | INFO     | app.integrations.evolution:download_media:1057 | Baixando mídia de: https://mmg.whatsapp.net/o1/v/t24/f2/m231/AQODWOx8...
2025-08-07 19:01:18.316 | INFO     | app.integrations.evolution:download_media:1059 | MediaKey presente - mídia será descriptografada (tipo: image)
2025-08-07 19:01:20.287 | INFO     | app.integrations.evolution:download_media:1079 | Mídia baixada com sucesso: 1008266 bytes
2025-08-07 19:01:20.287 | INFO     | app.integrations.evolution:download_media:1083 | Iniciando descriptografia da mídia...
2025-08-07 19:01:20.288 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:958 | MediaKey decodificada: 32 bytes
2025-08-07 19:01:20.288 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:991 | IV: 16 bytes, Cipher Key: 32 bytes, MAC Key: 32 bytes
2025-08-07 19:01:20.292 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:1027 | Mídia descriptografada com sucesso: 1008245 bytes
2025-08-07 19:01:20.292 | INFO     | app.integrations.evolution:download_media:1091 | Mídia descriptografada com sucesso: 1008245 bytes
2025-08-07 19:01:20.293 | INFO     | app.api.webhooks:process_message_with_agent:661 | Imagem baixada, primeiros 20 bytes (hex): ffd8ffe000104a46494600010100000100010000
2025-08-07 19:01:20.301 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-07 19:01:20.301 | INFO     | app.api.webhooks:process_message_with_agent:698 | 🔍 AGNO validou mídia: jpeg
2025-08-07 19:01:20.302 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Imagem validada (jpeg): 1344328 chars
2025-08-07 19:01:20.302 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 WEBHOOK: Usando conversation_id=09c7fc7e-a847-43c2-a06b-761a2acd493f para phone=558182986181
2025-08-07 19:01:20.302 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chamando process_message com conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:01:20.505 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=558182986181
2025-08-07 19:01:20.505 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 19:01:20.719 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:01:20.720 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:01:22.148 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 19:01:22.149 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:01:22.149 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 9
2025-08-07 19:01:22.149 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 19:01:22.149 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T19:01:15.296312+00:00 - user
2025-08-07 19:01:22.149 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 19:01:22.149 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 9 mensagens disponíveis (menos que o limite de 100)
2025-08-07 19:01:22.150 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:01:22.150 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:01:22.150 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:01:23.530 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 19:01:23.530 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:01:23.531 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 9
2025-08-07 19:01:23.531 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 19:01:23.531 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T19:01:15.296312+00:00 - user
2025-08-07 19:01:23.531 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 19:01:23.531 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 9 mensagens disponíveis (menos que o limite de 100)
2025-08-07 19:01:23.531 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ HISTÓRICO FINAL: 9 mensagens carregadas
2025-08-07 19:01:23.532 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-07 19:01:23.532 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: IMAGE
2025-08-07 19:01:23.532 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 1,344,328 caracteres
2025-08-07 19:01:23.532 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-07 19:01:23.533 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-07 19:01:23
2025-08-07 19:01:23.533 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 19:01:23.533 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-07 19:01:23.533 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 PROCESSAMENTO DE IMAGEM INICIADO
2025-08-07 19:01:23.533 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-07 19:01:23.533 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 IMAGEM - Formato detectado: base64
2025-08-07 19:01:23.533 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📈 IMAGEM - Métricas:
2025-08-07 19:01:23.534 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Base64: 1,344,328 caracteres
2025-08-07 19:01:23.534 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Estimado: 1,008,246 bytes (984.6 KB / 0.96 MB)
2025-08-07 19:01:23.549 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📐 IMAGEM - Dimensões: 2268x4032 pixels
2025-08-07 19:01:23.727 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 1/4: Decodificando base64...
2025-08-07 19:01:23.730 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Decodificação completa em 0.00s
2025-08-07 19:01:23.730 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tamanho real: 1,008,245 bytes
2025-08-07 19:01:23.730 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Taxa compressão: 25.0%
2025-08-07 19:01:23.731 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 2/4: Detectando formato da imagem...
2025-08-07 19:01:23.731 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-07 19:01:23.731 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato detectado: JPEG
2025-08-07 19:01:23.731 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Confiança: high
2025-08-07 19:01:23.731 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo detecção: 0.00s
2025-08-07 19:01:23.731 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔧 Usando PIL + Gemini direto (correção implementada)
2025-08-07 19:01:23.734 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📤 Enviando imagem para Gemini Vision com prompt otimizado...
2025-08-07 19:01:40.243 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ PIL + Gemini direto: Sucesso (latência otimizada)
2025-08-07 19:01:40.244 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💰 Valor da conta detectado: R$ 350.81
2025-08-07 19:01:40.250 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 19:01:40.251 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ MULTIMODAL: Processamento concluído
2025-08-07 19:01:40.251 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tipo: image
2025-08-07 19:01:40.251 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Status: success
2025-08-07 19:01:40.252 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo total: 16.72s
2025-08-07 19:01:40.252 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 19:01:40.252 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 19:01:40.252 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Análise multimodal incluída no contexto formatado
2025-08-07 19:01:40.253 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: EM_QUALIFICACAO
                    - Status: PENDING
                    
                    === ANÁLISE MULTIMODAL RECEBIDA ===
TIPO: BILL_IMAGE
ANÁLISE: Aqui estão as informações extraídas da imagem fornecida, em formato estruturado:

**- Tipo de documento:** DANFE - Documento Auxiliar da Nota Fiscal de Energia Elétrica Eletrônica

**- Valores en...
2025-08-07 19:01:40.253 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 5764 caracteres
2025-08-07 19:01:40.253 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Multimodal incluído no prompt: Aqui estão as informações extraídas da imagem fornecida, em formato estruturado:

**- Tipo de documento:** DANFE - Documento Auxiliar da Nota Fiscal de Energia Elétrica Eletrônica

**- Valores encontr...
2025-08-07 19:01:40.253 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🖼️ Multimodal incluído no prompt: tipo=bill_image, tem conteúdo=True
2025-08-07 19:01:40.254 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Preparando para chamar agent.arun...
2025-08-07 19:01:40.254 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem instructions? True
2025-08-07 19:01:40.254 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem memory? True
2025-08-07 19:01:40.254 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem model? True
2025-08-07 19:01:40.255 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun com timeout de 30s...
INFO:     127.0.0.1:33594 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-07 19:02:00.161 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ agent.arun completou com sucesso
2025-08-07 19:02:00.162 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Tipo do result: <class 'agno.run.response.RunResponse'>
2025-08-07 19:02:00.162 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result tem content? True
2025-08-07 19:02:00.162 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Atributos do result: ['content', 'content_type', 'thinking', 'reasoning_content', 'messages', 'metrics', 'model', 'model_provider', 'run_id', 'agent_id', 'agent_name', 'session_id', 'team_session_id', 'workflow_id', 'tools', 'formatted_tool_calls', 'images', 'videos', 'audio', 'response_audio', 'citations', 'extra_data', 'created_at', 'events', 'status']
2025-08-07 19:02:00.162 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Result não é None, tipo: RunResponse
2025-08-07 19:02:00.162 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 raw_response (primeiros 200 chars): Perfeito, vi aqui sua conta da Neoenergia no valor de R$350,81. Para a nossa solução de assinatura com desconto, a fatura precisa ser a partir de R$400. Você teria outra conta de luz que possamos soma...
2025-08-07 19:02:00.162 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho raw_response: 252 caracteres
2025-08-07 19:02:00.398 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>Perfeito, vi aqui sua conta da Neoenergia no valor de R$350,81. Para a nossa solução...
2025-08-07 19:02:00.398 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=285, primeiros 200 chars: <RESPOSTA_FINAL>Perfeito, vi aqui sua conta da Neoenergia no valor de R$350,81. Para a nossa solução de assinatura com desconto, a fatura precisa ser a partir de R$400. Você teria outra conta de luz q
2025-08-07 19:02:00.399 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=285, primeiros 200 chars: <RESPOSTA_FINAL>Perfeito, vi aqui sua conta da Neoenergia no valor de R$350,81. Para a nossa solução de assinatura com desconto, a fatura precisa ser a partir de R$400. Você teria outra conta de luz q
2025-08-07 19:02:01.274 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando emoji para reaction | Data: {'reaction': '✅', 'recipient': 'reaction', 'type': 'emoji'}
2025-08-07 19:02:01.274 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Reação '✅' enviada com sucesso. ID: 3EB0F876778AEF2C1A630DEFDD0A6C50F69E056C
2025-08-07 19:02:01.487 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 19:02:01.487 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:53702 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 19:02:02.298 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:53702 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:02:03.776 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem dividida em 3 partes | Data: {'phone': '558182986181', 'original_length': 252}
2025-08-07 19:02:05.965 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.08, 'message_length': 63, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 19:02:11.203 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 63, 'delay_used': 2.18, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:02:11.204 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Perfeito, vi aqui sua conta da Neoenergia no valor', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:02:11.204 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 1/3 enviado. ID: 3EB052306C69426A1DB8B18192CBEF82AB1E2E71
2025-08-07 19:02:11.209 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 19:02:11.210 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:52260 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 19:02:12.125 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:52260 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:51866 - "GET /health HTTP/1.1" 200 OK
2025-08-07 19:02:14.978 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.37, 'message_length': 88, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 19:02:20.505 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 88, 'delay_used': 2.97, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:02:20.505 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Para a nossa solução de assinatura com desconto, a', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:02:20.506 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 2/3 enviado. ID: 3EB005785C5ADE79C4D6D45395734BEF2EB78471
2025-08-07 19:02:20.511 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 19:02:20.511 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:40682 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 19:02:21.412 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:40682 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:02:26.313 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.31, 'message_length': 99, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 19:02:31.775 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 99, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:02:31.775 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Você teria outra conta de luz que possamos somar p', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:02:31.775 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 3/3 enviado. ID: 3EB0E0430A5EC298C9D4F3703522C30700047609
2025-08-07 19:02:31.782 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 19:02:31.782 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:59864 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 19:02:32.721 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:59864 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:02:37.466 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Follow-up de 30min agendado para 558182986181 às 16:32
2025-08-07 19:02:37.467 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Follow-up sequencial: 24h será agendado apenas se usuário não responder ao de 30min
INFO:     127.0.0.1:49286 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:47674 - "GET /health HTTP/1.1" 200 OK
2025-08-07 19:03:23.709 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:57288 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-07 19:03:26.310 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 19:03:26.310 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:325 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T16:03:26.303Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:57288 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 19:03:26.316 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 19:03:26.317 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:325 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T16:03:26.312Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:57288 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 19:03:26.326 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:57288 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-07 19:03:26.327 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'tenho sim', 'sender': '558182986181', 'type': 'text'}
2025-08-07 19:03:26.329 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 9}
2025-08-07 19:03:26.786 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-07 19:03:26.787 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-07 19:03:26.787 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-07 19:03:26.787 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-07 19:03:26.787 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-07 19:03:26.788 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-07 19:03:26.788 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-07 19:03:26.788 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-07 19:03:26.789 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-07 19:03:27.190 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-07 19:03:27.191 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 19:03:27.191 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 19:03:27.191 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 19:03:27.191 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 19:03:27.191 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 19:03:27.192 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 19:03:27.192 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 19:03:27.192 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 19:03:27.192 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 19:03:27.192 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 19:03:27.193 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 19:03:27.193 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 19:03:27.193 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 19:03:27.193 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 19:03:27.193 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 19:03:27.193 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-07 19:03:27.193 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-07 19:03:27.194 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Nova instância do AgenticSDR criada! pronto
2025-08-07 19:03:27.194 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 19:03:27.194 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:330 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5VTTOyOZQzymi_JL1mKswk-gV0bgynKBjXnlereNYMw&oe=68A2170D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T16:03:26.615Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:57288 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 19:03:27.195 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversa validada - ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f, Phone: 558182986181
2025-08-07 19:03:27.196 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 19:03:27.196 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:330 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5VTTOyOZQzymi_JL1mKswk-gV0bgynKBjXnlereNYMw&oe=68A2170D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T16:03:26.652Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:57304 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 19:03:27.852 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:57304 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:03:27.853 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 19:03:27.853 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:57288 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-07 19:03:27.854 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:57310 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:03:27.855 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 19:03:27.855 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:57322 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-07 19:03:27.856 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:57332 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:03:27.856 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 WEBHOOK: Usando conversation_id=09c7fc7e-a847-43c2-a06b-761a2acd493f para phone=558182986181
2025-08-07 19:03:27.856 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chamando process_message com conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:03:28.083 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=558182986181
2025-08-07 19:03:28.083 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 19:03:28.296 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:03:28.296 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:03:29.686 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 19:03:29.687 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:03:29.687 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 11
2025-08-07 19:03:29.687 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 19:03:29.687 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T19:03:27.196892+00:00 - user
2025-08-07 19:03:29.688 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 19:03:29.688 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 11 mensagens disponíveis (menos que o limite de 100)
2025-08-07 19:03:29.689 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:03:29.689 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:03:29.689 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:03:31.058 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 19:03:31.058 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:03:31.059 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 11
2025-08-07 19:03:31.059 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 19:03:31.059 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T19:03:27.196892+00:00 - user
2025-08-07 19:03:31.059 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 19:03:31.059 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 11 mensagens disponíveis (menos que o limite de 100)
2025-08-07 19:03:31.059 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ HISTÓRICO FINAL: 11 mensagens carregadas
2025-08-07 19:03:31.060 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 19:03:31.060 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: EM_QUALIFICACAO
                    - Status: PENDING
                    
                    USER: oi
ASSISTANT: Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?
USER: mateus
ASSISTANT: Então vamos lá, Mateus! Hoje na SolarPrime nós temos 4 soluções energét...
2025-08-07 19:03:31.060 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 2324 caracteres
2025-08-07 19:03:31.060 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ❌ Nenhum resultado multimodal incluído no prompt
2025-08-07 19:03:31.061 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Preparando para chamar agent.arun...
2025-08-07 19:03:31.061 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem instructions? True
2025-08-07 19:03:31.061 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem memory? True
2025-08-07 19:03:31.061 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem model? True
2025-08-07 19:03:31.061 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun com timeout de 30s...
2025-08-07 19:03:31.062 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 19:03:31.062 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:57336 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-07 19:03:31.139 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:57352 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:03:31.141 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 19:03:31.142 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:57362 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
INFO:     127.0.0.1:44548 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-07 19:03:55.338 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ agent.arun completou com sucesso
2025-08-07 19:03:55.338 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Tipo do result: <class 'agno.run.response.RunResponse'>
2025-08-07 19:03:55.338 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result tem content? True
2025-08-07 19:03:55.338 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Atributos do result: ['content', 'content_type', 'thinking', 'reasoning_content', 'messages', 'metrics', 'model', 'model_provider', 'run_id', 'agent_id', 'agent_name', 'session_id', 'team_session_id', 'workflow_id', 'tools', 'formatted_tool_calls', 'images', 'videos', 'audio', 'response_audio', 'citations', 'extra_data', 'created_at', 'events', 'status']
2025-08-07 19:03:55.339 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Result não é None, tipo: RunResponse
2025-08-07 19:03:55.339 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 raw_response (primeiros 200 chars): <RESPOSTA_FINAL>Ótimo! Pode me enviar a outra conta então? Assim que me enviar eu já somo os valores na hora e te mostro o tamanho da sua economia.</RESPOSTA_FINAL>...
2025-08-07 19:03:55.339 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho raw_response: 164 caracteres
2025-08-07 19:03:55.571 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>Ótimo! Pode me enviar a outra conta então? Assim que me enviar eu já somo os valores...
2025-08-07 19:03:55.572 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=164, primeiros 200 chars: <RESPOSTA_FINAL>Ótimo! Pode me enviar a outra conta então? Assim que me enviar eu já somo os valores na hora e te mostro o tamanho da sua economia.</RESPOSTA_FINAL>
2025-08-07 19:03:55.572 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=164, primeiros 200 chars: <RESPOSTA_FINAL>Ótimo! Pode me enviar a outra conta então? Assim que me enviar eu já somo os valores na hora e te mostro o tamanho da sua economia.</RESPOSTA_FINAL>
2025-08-07 19:04:00.795 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 2.77, 'message_length': 131, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 19:04:05.730 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 131, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:04:05.730 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Ótimo! Pode me enviar a outra conta então? Assim q', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:04:05.730 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB048F9DCBA9958FCB1EDBF1383596CC37BFB86
2025-08-07 19:04:06.769 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 19:04:06.770 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:51458 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 19:04:07.204 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Follow-up de 30min agendado para 558182986181 às 16:34
2025-08-07 19:04:07.204 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Follow-up sequencial: 24h será agendado apenas se usuário não responder ao de 30min
2025-08-07 19:04:07.205 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:51458 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:55344 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:39094 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:45092 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:47410 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:57874 - "GET /health HTTP/1.1" 200 OK
2025-08-07 19:06:22.301 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-07 19:06:22.301 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:325 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T16:06:22.069Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:44662 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-07 19:06:22.307 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:44660 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-07 19:06:22.308 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Imagem recebida] Aqui está', 'sender': '558182986181', 'type': 'text'}
2025-08-07 19:06:22.309 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 27}
2025-08-07 19:06:23.193 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-07 19:06:23.194 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-07 19:06:23.194 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-07 19:06:23.194 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-07 19:06:23.194 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-07 19:06:23.195 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-07 19:06:23.195 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-07 19:06:23.196 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-07 19:06:23.196 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-07 19:06:23.611 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-07 19:06:23.612 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 19:06:23.612 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 19:06:23.612 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 19:06:23.612 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 19:06:23.612 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 19:06:23.613 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 19:06:23.613 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 19:06:23.613 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 19:06:23.614 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 19:06:23.614 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 19:06:23.614 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 19:06:23.615 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 19:06:23.615 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 19:06:23.615 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 19:06:23.615 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 19:06:23.616 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-07 19:06:23.616 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-07 19:06:23.616 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Nova instância do AgenticSDR criada! pronto
2025-08-07 19:06:23.617 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 19:06:23.617 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:330 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5VTTOyOZQzymi_JL1mKswk-gV0bgynKBjXnlereNYMw&oe=68A2170D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T16:06:22.381Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:44660 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 19:06:23.617 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-07 19:06:23.618 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:330 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5VTTOyOZQzymi_JL1mKswk-gV0bgynKBjXnlereNYMw&oe=68A2170D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-07T16:06:22.527Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:44662 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-07 19:06:23.618 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversa validada - ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f, Phone: 558182986181
2025-08-07 19:06:23.619 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:44680 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:06:27.174 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 19:06:27.175 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:44692 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-07 19:06:27.176 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📸 IMAGEM DETECTADA - Analisando estrutura...
2025-08-07 19:06:27.177 | INFO     | app.api.webhooks:process_message_with_agent:612 | Campos disponíveis na imageMessage: ['url', 'mimetype', 'caption', 'fileSha256', 'fileLength', 'height', 'width', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'jpegThumbnail', 'contextInfo', 'firstScanSidecar', 'firstScanLength', 'scansSidecar', 'scanLengths', 'midQualityFileSha256', 'imageSourceType']
2025-08-07 19:06:27.177 | INFO     | app.api.webhooks:process_message_with_agent:619 | jpegThumbnail é string, tamanho: 960 chars
2025-08-07 19:06:27.177 | INFO     | app.api.webhooks:process_message_with_agent:620 | jpegThumbnail primeiros 50 chars: /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHB
2025-08-07 19:06:27.177 | INFO     | app.api.webhooks:process_message_with_agent:623 | jpegThumbnail parece ser base64 válido
2025-08-07 19:06:27.177 | INFO     | app.api.webhooks:process_message_with_agent:630 | mediaKey presente: 0pomlp/C41alGUXGXJRS...
2025-08-07 19:06:27.177 | INFO     | app.api.webhooks:process_message_with_agent:632 | directPath presente: /o1/v/t24/f2/m231/AQODWOx8Idn7nPIh46WNe6Ze7uKKlR81...
2025-08-07 19:06:27.178 | INFO     | app.api.webhooks:process_message_with_agent:634 | URL presente: https://mmg.whatsapp.net/o1/v/t24/f2/m231/AQODWOx8...
2025-08-07 19:06:27.178 | INFO     | app.api.webhooks:process_message_with_agent:655 | 🔐 Incluindo mediaKey para descriptografia
2025-08-07 19:06:27.178 | INFO     | app.integrations.evolution:download_media:1057 | Baixando mídia de: https://mmg.whatsapp.net/o1/v/t24/f2/m231/AQODWOx8...
2025-08-07 19:06:27.178 | INFO     | app.integrations.evolution:download_media:1059 | MediaKey presente - mídia será descriptografada (tipo: image)
2025-08-07 19:06:27.234 | INFO     | app.integrations.evolution:download_media:1079 | Mídia baixada com sucesso: 1008266 bytes
2025-08-07 19:06:27.234 | INFO     | app.integrations.evolution:download_media:1083 | Iniciando descriptografia da mídia...
2025-08-07 19:06:27.234 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:958 | MediaKey decodificada: 32 bytes
2025-08-07 19:06:27.235 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:991 | IV: 16 bytes, Cipher Key: 32 bytes, MAC Key: 32 bytes
2025-08-07 19:06:27.236 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:1027 | Mídia descriptografada com sucesso: 1008245 bytes
2025-08-07 19:06:27.236 | INFO     | app.integrations.evolution:download_media:1091 | Mídia descriptografada com sucesso: 1008245 bytes
2025-08-07 19:06:27.236 | INFO     | app.api.webhooks:process_message_with_agent:661 | Imagem baixada, primeiros 20 bytes (hex): ffd8ffe000104a46494600010100000100010000
2025-08-07 19:06:27.240 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-07 19:06:27.241 | INFO     | app.api.webhooks:process_message_with_agent:698 | 🔍 AGNO validou mídia: jpeg
2025-08-07 19:06:27.241 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Imagem validada (jpeg): 1344328 chars
2025-08-07 19:06:27.241 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 WEBHOOK: Usando conversation_id=09c7fc7e-a847-43c2-a06b-761a2acd493f para phone=558182986181
2025-08-07 19:06:27.241 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chamando process_message com conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:06:27.847 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=558182986181
2025-08-07 19:06:27.847 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 19:06:28.088 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:06:28.089 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:06:29.710 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 19:06:29.711 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:06:29.711 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 13
2025-08-07 19:06:29.711 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 19:06:29.711 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T19:06:23.619514+00:00 - user
2025-08-07 19:06:29.711 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 19:06:29.712 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 13 mensagens disponíveis (menos que o limite de 100)
2025-08-07 19:06:29.712 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:06:29.713 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:06:29.713 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:06:31.345 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 19:06:31.346 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:06:31.346 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 13
2025-08-07 19:06:31.346 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 19:06:31.346 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T19:06:23.619514+00:00 - user
2025-08-07 19:06:31.346 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 19:06:31.347 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 13 mensagens disponíveis (menos que o limite de 100)
2025-08-07 19:06:31.347 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ HISTÓRICO FINAL: 13 mensagens carregadas
2025-08-07 19:06:31.347 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-07 19:06:31.348 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: IMAGE
2025-08-07 19:06:31.348 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 1,344,328 caracteres
2025-08-07 19:06:31.348 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Aqui está
2025-08-07 19:06:31.348 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-07 19:06:31
2025-08-07 19:06:31.348 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 19:06:31.348 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-07 19:06:31.349 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 PROCESSAMENTO DE IMAGEM INICIADO
2025-08-07 19:06:31.349 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-07 19:06:31.349 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 IMAGEM - Formato detectado: base64
2025-08-07 19:06:31.349 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📈 IMAGEM - Métricas:
2025-08-07 19:06:31.349 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Base64: 1,344,328 caracteres
2025-08-07 19:06:31.350 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Estimado: 1,008,246 bytes (984.6 KB / 0.96 MB)
2025-08-07 19:06:31.354 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📐 IMAGEM - Dimensões: 2268x4032 pixels
2025-08-07 19:06:31.354 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 1/4: Decodificando base64...
2025-08-07 19:06:31.357 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Decodificação completa em 0.00s
2025-08-07 19:06:31.358 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tamanho real: 1,008,245 bytes
2025-08-07 19:06:31.358 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Taxa compressão: 25.0%
2025-08-07 19:06:31.358 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 2/4: Detectando formato da imagem...
2025-08-07 19:06:31.358 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-07 19:06:31.358 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato detectado: JPEG
2025-08-07 19:06:31.358 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Confiança: high
2025-08-07 19:06:31.359 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo detecção: 0.00s
2025-08-07 19:06:31.359 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔧 Usando PIL + Gemini direto (correção implementada)
2025-08-07 19:06:31.363 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📤 Enviando imagem para Gemini Vision com prompt otimizado...
2025-08-07 19:06:46.688 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ PIL + Gemini direto: Sucesso (latência otimizada)
2025-08-07 19:06:46.688 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💰 Valor da conta detectado: R$ 350.81
2025-08-07 19:06:47.152 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 19:06:47.153 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ MULTIMODAL: Processamento concluído
2025-08-07 19:06:47.153 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tipo: image
2025-08-07 19:06:47.154 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Status: success
2025-08-07 19:06:47.154 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo total: 15.81s
2025-08-07 19:06:47.154 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 19:06:47.154 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 19:06:47.155 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Análise multimodal incluída no contexto formatado
2025-08-07 19:06:47.155 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: EM_QUALIFICACAO
                    - Status: PENDING
                    
                    === ANÁLISE MULTIMODAL RECEBIDA ===
TIPO: BILL_IMAGE
ANÁLISE: Aqui está uma análise estruturada da imagem fornecida:

**- Tipo de documento:** DANFE - Documento Auxiliar da Nota Fiscal de Energia Elétrica Eletrônica

**- Valores encontrados:**

* Total a pa...
2025-08-07 19:06:47.155 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 6335 caracteres
2025-08-07 19:06:47.155 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Multimodal incluído no prompt: Aqui está uma análise estruturada da imagem fornecida:

**- Tipo de documento:** DANFE - Documento Auxiliar da Nota Fiscal de Energia Elétrica Eletrônica

**- Valores encontrados:**

* Total a pagar: ...
2025-08-07 19:06:47.155 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🖼️ Multimodal incluído no prompt: tipo=bill_image, tem conteúdo=True
2025-08-07 19:06:47.156 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Preparando para chamar agent.arun...
2025-08-07 19:06:47.156 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem instructions? True
2025-08-07 19:06:47.156 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem memory? True
2025-08-07 19:06:47.156 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem model? True
2025-08-07 19:06:47.156 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun com timeout de 30s...
INFO:     127.0.0.1:56750 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-07 19:07:06.968 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ agent.arun completou com sucesso
2025-08-07 19:07:06.968 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Tipo do result: <class 'agno.run.response.RunResponse'>
2025-08-07 19:07:06.968 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result tem content? True
2025-08-07 19:07:06.968 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Atributos do result: ['content', 'content_type', 'thinking', 'reasoning_content', 'messages', 'metrics', 'model', 'model_provider', 'run_id', 'agent_id', 'agent_name', 'session_id', 'team_session_id', 'workflow_id', 'tools', 'formatted_tool_calls', 'images', 'videos', 'audio', 'response_audio', 'citations', 'extra_data', 'created_at', 'events', 'status']
2025-08-07 19:07:06.968 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Result não é None, tipo: RunResponse
2025-08-07 19:07:06.968 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 raw_response (primeiros 200 chars): <RESPOSTA_FINAL>
Maravilha! Somando as duas contas chegamos a um total de R$701,62. Com esse valor, já conseguimos te incluir na nossa modalidade de assinatura residencial, que te garante *15% de desc...
2025-08-07 19:07:06.969 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho raw_response: 318 caracteres
2025-08-07 19:07:07.373 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>
Maravilha! Somando as duas contas chegamos a um total de R$701,62. Com esse valor, ...
2025-08-07 19:07:07.373 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=318, primeiros 200 chars: <RESPOSTA_FINAL>
Maravilha! Somando as duas contas chegamos a um total de R$701,62. Com esse valor, já conseguimos te incluir na nossa modalidade de assinatura residencial, que te garante *15% de desc
2025-08-07 19:07:07.374 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=318, primeiros 200 chars: <RESPOSTA_FINAL>
Maravilha! Somando as duas contas chegamos a um total de R$701,62. Com esse valor, já conseguimos te incluir na nossa modalidade de assinatura residencial, que te garante *15% de desc
2025-08-07 19:07:08.449 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando emoji para reaction | Data: {'reaction': '✅', 'recipient': 'reaction', 'type': 'emoji'}
2025-08-07 19:07:08.449 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Reação '✅' enviada com sucesso. ID: 3EB063E439C491FDB2CE9958DADA23EEA71BFCC9
2025-08-07 19:07:08.455 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 19:07:08.455 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:59794 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 19:07:09.369 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:59794 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:07:10.952 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem dividida em 3 partes | Data: {'phone': '558182986181', 'original_length': 301}
2025-08-07 19:07:13.295 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.44, 'message_length': 66, 'recipient': '558182986181', 'type': 'typing'}
INFO:     127.0.0.1:57946 - "GET /health HTTP/1.1" 200 OK
2025-08-07 19:07:19.119 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 66, 'delay_used': 2.14, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:07:19.120 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Maravilha! Somando as duas contas chegamos a um to', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:07:19.120 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 1/3 enviado. ID: 3EB02663F2F07AFB23274778FB4EE08633FC3E6E
2025-08-07 19:07:19.126 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 19:07:19.126 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:45802 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 19:07:20.098 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:45802 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:07:20.104 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 19:07:20.104 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:45802 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-07 19:07:21.739 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.05, 'message_length': 131, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 19:07:26.959 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 131, 'delay_used': 1.81, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:07:26.959 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Com esse valor, já conseguimos te incluir na nossa', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:07:26.959 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 2/3 enviado. ID: 3EB0754317D08DDAE99D30B43ADFED3674FC6553
2025-08-07 19:07:27.170 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 19:07:27.170 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:43792 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 19:07:27.896 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:43792 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:07:30.643 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.38, 'message_length': 102, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 19:07:36.173 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 102, 'delay_used': 2.87, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:07:36.174 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Isso dá uma economia de mais de *R$105,00* mensais', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:07:36.174 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 3/3 enviado. ID: 3EB0115A19776E0E57E5F282FA85DB4CCB8E5222
2025-08-07 19:07:36.180 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 19:07:36.181 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:43450 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 19:07:37.096 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:43450 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:07:40.768 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Follow-up de 30min agendado para 558182986181 às 16:37
2025-08-07 19:07:40.769 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Follow-up sequencial: 24h será agendado apenas se usuário não responder ao de 30min