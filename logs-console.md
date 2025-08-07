✅ Usando variáveis de ambiente do servidor (EasyPanel)
2025-08-07 19:38:33.093 | INFO     | app.services.knowledge_service:__init__:33 | ✅ KnowledgeService inicializado (versão simplificada)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-07 19:38:33.892 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-07 19:38:33.896 | INFO     | app.integrations.redis_client:connect:39 | ✅ Conectado ao Redis com sucesso! URL: redis_redis:6379
2025-08-07 19:38:33.896 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-07 19:38:34.519 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-07 19:38:34.520 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buffer Inteligente inicializado (timeout=30.0s, max=10)
2025-08-07 19:38:34.520 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-07 19:38:34.520 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=150 chars, smart=ativada)
2025-08-07 19:38:34.520 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 150}
2025-08-07 19:38:34.521 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 19:38:34.521 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 19:38:34.521 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 19:38:34.521 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 19:38:34.522 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 19:38:34.522 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 19:38:34.522 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 19:38:34.522 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 19:38:34.523 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 19:38:34.523 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 19:38:34.523 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 19:38:34.524 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 19:38:34.524 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 19:38:34.524 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 19:38:34.524 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 19:38:34.525 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 3}
2025-08-07 19:38:35.189 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-07 19:38:35.189 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-07 19:38:35.190 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-07 19:38:35.190 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-07 19:38:35.190 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Fonte' mapeado: ID 392810
2025-08-07 19:38:35.190 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-07 19:38:35.190 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-07 19:38:35.191 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-07 19:38:35.735 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-07 19:38:35.735 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-07 19:38:35.735 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-07 19:38:35.736 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-07 19:38:35.736 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-07 19:38:35.736 | INFO     | app.teams.agents.crm:initialize:195 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-07 19:38:35.737 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-07 19:38:35.765 | INFO     | app.services.kommo_auto_sync:__init__:94 | ✅ KommoAutoSyncService inicializado
2025-08-07 19:38:35.765 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 19:38:35.766 | INFO     | app.teams.agents.crm_enhanced:__init__:43 | ✅ KommoEnhancedCRM inicializado com funcionalidades completas
2025-08-07 19:38:36.401 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'WhatsApp' mapeado: ID 392802
2025-08-07 19:38:36.402 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Valor Conta Energia' mapeado: ID 392804
2025-08-07 19:38:36.402 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Score Qualificação' mapeado: ID 392806
2025-08-07 19:38:36.402 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Solução Solar' mapeado: ID 392808
2025-08-07 19:38:36.402 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Fonte' mapeado: ID 392810
2025-08-07 19:38:36.402 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'ID Conversa' mapeado: ID 392860
2025-08-07 19:38:36.402 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Link do evento no Google Calendar' mapeado: ID 395520
2025-08-07 19:38:36.403 | INFO     | app.teams.agents.crm:_fetch_custom_fields:231 | Campo 'Status atual da reunião' mapeado: ID 395522
2025-08-07 19:38:37.030 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Novo Lead' mapeado: ID 89709459
2025-08-07 19:38:37.030 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Em Qualificação' mapeado: ID 89709463
2025-08-07 19:38:37.030 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Qualificado' mapeado: ID 89709467
2025-08-07 19:38:37.030 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Reunião Agendada' mapeado: ID 89709595
2025-08-07 19:38:37.031 | INFO     | app.teams.agents.crm:_fetch_pipeline_stages:266 | Stage 'Não Interessado' mapeado: ID 89709599
2025-08-07 19:38:37.031 | INFO     | app.teams.agents.crm:initialize:195 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-07 19:38:37.032 | INFO     | app.services.kommo_auto_sync:initialize:103 | ✅ CRM Enhanced inicializado para auto-sync
2025-08-07 19:38:37.032 | INFO     | app.services.kommo_auto_sync:start:116 | 🔄 Iniciando sincronização automática com Kommo CRM
2025-08-07 19:38:37.032 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo Auto Sync pronto | Data: {'sync_interval': '30s', 'features': 'leads, tags, pipeline, fields'}
2025-08-07 19:38:37.056 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto
2025-08-07 19:38:37.057 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUp Executor pronto | Data: {'check_interval': '1min', 'types': '30min, 24h'}
2025-08-07 19:38:37.057 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔥 Pré-aquecendo AgenticSDR (tentativa 1/3)...
2025-08-07 19:38:37.057 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-07 19:38:37.057 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-07 19:38:37.058 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-07 19:38:37.058 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-07 19:38:37.058 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-07 19:38:37.058 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-07 19:38:37.058 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-07 19:38:37.090 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-07 19:38:37.090 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-07 19:38:37.504 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-07 19:38:37.504 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 19:38:37.505 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 19:38:37.505 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 19:38:37.505 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 19:38:37.505 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 19:38:37.505 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 19:38:37.505 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 19:38:37.505 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 19:38:37.506 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 19:38:37.506 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 19:38:37.506 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 19:38:37.506 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 19:38:37.507 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 19:38:37.507 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 19:38:37.507 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 19:38:37.508 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-07 19:38:37.508 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-07 19:38:37.508 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Nova instância do AgenticSDR criada! pronto
2025-08-07 19:38:37.508 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AgenticSDR pronto | Data: {'status': 'pré-aquecido com sucesso'}
2025-08-07 19:38:37.508 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
2025-08-07 19:38:40.368 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: agentic_sdr_sessions
2025-08-07 19:38:40.369 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-07 19:38:40.369 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-07 19:38:40.369 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-07 19:38:40.369 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-07 19:38:40.370 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Memory pronto | Data: {'status': 'configurada (in-memory)'}
2025-08-07 19:38:40.370 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge pronto | Data: {'status': 'local ativo'}
2025-08-07 19:38:40.370 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-07 19:38:40.371 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-07 19:38:40.791 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
2025-08-07 19:38:40.791 | INFO     | app.utils.optional_storage:__init__:43 | ✅ SupabaseStorage inicializado para: sdr_team_sessions
2025-08-07 19:38:40.791 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-flash'}
2025-08-07 19:38:40.792 | INFO     | app.teams.sdr_team:__init__:112 | Team funcionará sem memória persistente (AgentMemory desabilitado)
2025-08-07 19:38:40.792 | INFO     | app.teams.sdr_team:_initialize_agents:155 | 📅 Verificando CalendarAgent - enable_calendar_agent: True
2025-08-07 19:38:40.792 | INFO     | app.teams.sdr_team:_initialize_agents:158 | 📅 ATIVANDO CalendarAgent...
2025-08-07 19:38:40.792 | INFO     | app.teams.agents.calendar:__init__:98 | ✅ CalendarAgent inicializado
2025-08-07 19:38:40.792 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-07 19:38:40.793 | INFO     | app.teams.sdr_team:_initialize_agents:166 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-07 19:38:40.793 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-07 19:38:40.793 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
2025-08-07 19:38:40.794 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-07 19:38:40.794 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-07 19:38:40.795 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-07 19:38:40.795 | INFO     | app.teams.sdr_team:initialize:284 | Team configurado sem memória (melhor estabilidade)
2025-08-07 19:38:40.795 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 3, 'startup_ms': 1000.0}
2025-08-07 19:38:40.796 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-07 19:38:40.796 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-07 19:38:40.799 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💰 Valor da conta extraído: R$ 350.81
2025-08-07 19:38:40.799 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Novo estágio identificado: EM_NEGOCIACAO
2025-08-07 19:38:41.023 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Lead atualizado no Supabase: {'bill_value': 350.81, 'current_stage': 'EM_NEGOCIACAO', 'updated_at': '2025-08-07T19:38:40.800153'}
2025-08-07 19:38:41.023 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=558182986181
2025-08-07 19:38:41.024 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 19:38:41.249 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:38:41.249 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:38:42.892 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 19:38:42.893 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:38:42.893 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 14
2025-08-07 19:38:42.893 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 19:38:42.893 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T19:07:39.173933+00:00 - assistant
2025-08-07 19:38:42.893 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 19:38:42.894 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 14 mensagens disponíveis (menos que o limite de 100)
2025-08-07 19:38:42.895 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:38:42.895 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:38:42.895 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:38:43.289 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 19:38:43.290 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 19:38:43.290 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 14
2025-08-07 19:38:43.290 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 19:38:43.290 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T19:07:39.173933+00:00 - assistant
2025-08-07 19:38:43.291 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 19:38:43.291 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 14 mensagens disponíveis (menos que o limite de 100)
2025-08-07 19:38:43.291 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ HISTÓRICO FINAL: 14 mensagens carregadas
2025-08-07 19:38:43.291 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:976 | 🔄 FOLLOW-UP DETECTADO - Evitando CalendarAgent
2025-08-07 19:38:43.292 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:977 | 🔄 Mensagem: REENGAJAMENTO DE LEAD - NÃO É AGENDAMENTO:

⚠️ IMPORTANTE: Esta é uma mensagem de follow-up/reengaja...
2025-08-07 19:38:43.292 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha | Data: {'decision_score': 0.5}
2025-08-07 19:38:43.292 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: EM_NEGOCIACAO
                    - Status: PENDING
                    
                    USER: oi
ASSISTANT: Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?
USER: mateus
ASSISTANT: Então vamos lá, Mateus! Hoje na SolarPrime nós temos 4 soluções energétic...
2025-08-07 19:38:43.293 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 4062 caracteres
2025-08-07 19:38:43.293 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ❌ Nenhum resultado multimodal incluído no prompt
2025-08-07 19:38:43.293 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun com timeout de 30s (modo complexo)...
INFO:     127.0.0.1:55414 - "GET /health HTTP/1.1" 200 OK
2025-08-07 19:39:13.293 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Agent Timeout: ❌ Timeout em agent.arun após 30s (modo complexo) | Data: {'component': 'Agent Timeout'}
2025-08-07 19:39:13.294 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Tipo do result: <class 'NoneType'>
2025-08-07 19:39:13.294 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result tem content? False
2025-08-07 19:39:13.295 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result como string: None...
2025-08-07 19:39:13.295 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⚠️ Result é None ou vazio!
2025-08-07 19:39:13.295 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 raw_response (primeiros 200 chars): None...
2025-08-07 19:39:13.295 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho raw_response: 4 caracteres
2025-08-07 19:39:13.530 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>None</RESPOSTA_FINAL>...
INFO:     127.0.0.1:39292 - "GET /health HTTP/1.1" 200 OK
2025-08-07 19:39:15.557 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 2.01, 'message_length': 4, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 19:39:19.758 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 4, 'delay_used': 1.77, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 19:39:20.374 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 WhatsApp: Follow-up enviado para None
2025-08-07 19:39:20.593 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📅 Follow-up sequencial de 24h agendado para 558182986181 às 08/08 16:39
2025-08-07 19:39:20.594 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 19:39:20.595 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:43880 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-07 19:39:20.741 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:43880 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 19:39:38.245 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:372 | 📝 1 leads atualizados para sincronizar
2025-08-07 19:39:40.605 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:215 | ✅ Tags adicionadas ao lead 3866108: []
2025-08-07 19:39:40.606 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:397 | 🔄 Lead d665126a-6e16-4839-a91c-bd1e4fca23f5 atualizado no Kommo
INFO:     10.11.0.4:48828 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     127.0.0.1:59126 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:46100 - "GET /health HTTP/1.1" 200 OK
2025-08-07 19:40:40.831 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:372 | 📝 1 leads atualizados para sincronizar
2025-08-07 19:40:42.605 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:215 | ✅ Tags adicionadas ao lead 3866108: []
INFO:     10.11.0.4:33922 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-07 19:40:42.607 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:397 | 🔄 Lead d665126a-6e16-4839-a91c-bd1e4fca23f5 atualizado no Kommo
INFO:     127.0.0.1:39152 - "GET /health HTTP/1.1" 200 OK
2025-08-07 19:41:01.904 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 19:41:01.904 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:45704 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-07 19:41:01.905 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:45706 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:55358 - "GET /health HTTP/1.1" 200 OK