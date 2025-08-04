✅ Usando variáveis de ambiente do servidor (EasyPanel)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-04 03:29:11.664 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-04 03:29:11.668 | WARNING  | app.integrations.redis_client:connect:35 | Redis não disponível: Error -2 connecting to redis:6379. -2.. Sistema funcionará sem cache.
2025-08-04 03:29:11.668 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-04 03:29:11.947 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-04 03:29:11.947 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Buffer inicializado (timeout=30.0s, max=10)
2025-08-04 03:29:11.947 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-04 03:29:11.947 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=250 chars, smart=ativada)
2025-08-04 03:29:11.948 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 250}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 03:29:11.968 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 03:29:11.968 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-04 03:29:11.968 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-04 03:29:11.968 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-04 03:29:11.969 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-04 03:29:11.969 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-04 03:29:11.969 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-04 03:29:11.969 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-04 03:29:11.970 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-04 03:29:11.970 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 03:29:12.295 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-04 03:29:12.296 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-04 03:29:12.296 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 03:29:12.296 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-04 03:29:12.296 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-04 03:29:12.296 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-04 03:29:12.296 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-04 03:29:12.714 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 03:29:12.714 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 03:29:12.714 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 6}
2025-08-04 03:29:13.675 | INFO     | app.teams.agents.crm:initialize:159 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-04 03:29:13.675 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-04 03:29:13.676 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:49328 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:29:21.680 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 03:29:21.681 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:29:21.443Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49692 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 03:29:21.682 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 03:29:21.683 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:29:21.467Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49696 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 03:29:21.702 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:49696 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 03:29:21.703 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Imagem recebida]', 'sender': '558182986181', 'type': 'text'}
2025-08-04 03:29:21.853 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:29:21.853 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:29:21.844Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49696 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 03:29:22.100 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:29:22.100 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:29:22.092Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49696 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 03:29:22.852 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:49696 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:29:22.857 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:29:22.857 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:49696 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 03:29:22.870 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:49696 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:29:22.874 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:29:22.875 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:49696 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INFO:     127.0.0.1:43392 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:29:51.704 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 17}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 03:29:53.474 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 03:29:53.475 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: agentic_sdr_sessions
2025-08-04 03:29:53.475 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-04 03:29:53.476 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-04 03:29:53.476 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-04 03:29:53.476 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-04 03:29:53.476 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 03:29:53.479 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base pronto | Data: {'status': 'ativo'}
2025-08-04 03:29:53.479 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-04 03:29:53.480 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-04 03:29:53.895 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 03:29:53.898 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 03:29:53.898 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-04 03:29:53.899 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-04 03:29:53.899 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-04 03:29:53.899 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-04 03:29:53.900 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-04 03:29:53.900 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-04 03:29:53.900 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-04 03:29:53.900 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-04 03:29:53.901 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 03:29:53.903 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-04 03:29:53.904 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-04 03:29:53.904 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 03:29:53.904 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-04 03:29:53.904 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-04 03:29:53.905 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-04 03:29:53.905 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-04 03:29:54.323 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 03:29:54.324 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 03:29:54.324 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-04 03:29:54.324 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-04 03:29:54.825 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📸 IMAGEM DETECTADA - Analisando estrutura...
2025-08-04 03:29:54.825 | INFO     | app.api.webhooks:process_message_with_agent:415 | Campos disponíveis na imageMessage: ['url', 'mimetype', 'fileSha256', 'fileLength', 'height', 'width', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'jpegThumbnail', 'contextInfo', 'firstScanSidecar', 'firstScanLength', 'scansSidecar', 'scanLengths', 'midQualityFileSha256', 'imageSourceType']
2025-08-04 03:29:54.825 | INFO     | app.api.webhooks:process_message_with_agent:422 | jpegThumbnail é string, tamanho: 868 chars
2025-08-04 03:29:54.825 | INFO     | app.api.webhooks:process_message_with_agent:423 | jpegThumbnail primeiros 50 chars: /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHB
2025-08-04 03:29:54.826 | INFO     | app.api.webhooks:process_message_with_agent:426 | jpegThumbnail parece ser base64 válido
2025-08-04 03:29:54.826 | INFO     | app.api.webhooks:process_message_with_agent:433 | mediaKey presente: bKAgOYLhpEHewOz/Fcfb...
2025-08-04 03:29:54.826 | INFO     | app.api.webhooks:process_message_with_agent:435 | directPath presente: /v/t62.7118-24/11281308_731162479780705_8333746825...
2025-08-04 03:29:54.826 | INFO     | app.api.webhooks:process_message_with_agent:437 | URL presente: https://mmg.whatsapp.net/v/t62.7118-24/11281308_73...
2025-08-04 03:29:54.826 | INFO     | app.api.webhooks:detect_media_format:63 | Formato detectado: Base64 válido
2025-08-04 03:29:54.827 | INFO     | app.api.webhooks:process_message_with_agent:445 | 📸 jpegThumbnail formato detectado: base64
2025-08-04 03:29:54.827 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ jpegThumbnail validado como base64: 868 chars
2025-08-04 03:29:54.827 | WARNING  | app.api.webhooks:process_message_with_agent:504 | Erro na validação AGNO: cannot access local variable 'base64' where it is not associated with a value
2025-08-04 03:29:54.827 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Imagem pronta (sem validação AGNO): 868 chars
2025-08-04 03:29:54.828 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 03:29:55.054 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:29:55.054 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:29:55.661 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 9 mensagens encontradas
2025-08-04 03:29:55.662 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:29:55.662 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:29:56.266 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 9 mensagens encontradas
2025-08-04 03:29:56.267 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 9 mensagens
2025-08-04 03:29:56.267 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:29:56.267 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-04 03:29:56.267 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: IMAGE
2025-08-04 03:29:56.267 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 868 caracteres
2025-08-04 03:29:56.267 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-04 03:29:56.267 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-04 03:29:56
2025-08-04 03:29:56.268 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:29:56.268 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-04 03:29:56.268 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 PROCESSAMENTO DE IMAGEM INICIADO
2025-08-04 03:29:56.268 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-04 03:29:56.268 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 IMAGEM - Formato detectado: base64
2025-08-04 03:29:56.268 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📈 IMAGEM - Métricas:
2025-08-04 03:29:56.268 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Base64: 868 caracteres
2025-08-04 03:29:56.268 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Estimado: 651 bytes (0.6 KB / 0.00 MB)
2025-08-04 03:29:56.268 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⚠️ IMAGEM: Possível thumbnail detectada (<50KB)
2025-08-04 03:29:56.627 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 1/4: Decodificando base64...
2025-08-04 03:29:56.628 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Decodificação completa em 0.00s
2025-08-04 03:29:56.628 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tamanho real: 649 bytes
2025-08-04 03:29:56.628 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Taxa compressão: 25.2%
2025-08-04 03:29:56.628 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 2/4: Detectando formato da imagem...
2025-08-04 03:29:56.628 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-04 03:29:56.628 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato detectado: JPEG
2025-08-04 03:29:56.629 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Confiança: high
2025-08-04 03:29:56.629 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo detecção: 0.00s
2025-08-04 03:29:56.629 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha | Data: {'decision_score': 0.3}
2025-08-04 03:29:56.629 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 9 mensagens, quality=fair, score=0.40
2025-08-04 03:29:59.966 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
INFO:     127.0.0.1:50354 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 03:30:21.900 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Vou analisar essa outra imagem que você mandou, Mateus, um segundo... Ah, agora sim, com essa outra ...
2025-08-04 03:30:23.912 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem dividida em 3 partes | Data: {'phone': '558182986181', 'original_length': 587}
2025-08-04 03:30:31.210 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 227, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:30:31.211 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Vou analisar essa outra imagem que você mandou, Ma', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:30:31.211 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 1/3 enviado. ID: 3EB0B6F83E20048D125C284EC666488450396367
2025-08-04 03:30:31.422 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 03:30:31.422 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:50084 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 03:30:32.339 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:50084 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:30:37.048 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 154, 'delay_used': 2.74, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:30:37.050 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Com uma conta de *R$4.500*, a gente tá falando de ', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:30:37.051 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 2/3 enviado. ID: 3EB076CF60E292E3AB0B112C13A3A1AE8E576B85
2025-08-04 03:30:37.059 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 03:30:37.061 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:50084 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 03:30:37.980 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:50084 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:30:45.134 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 204, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:30:45.135 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'E o mais interessante é que você não precisa inves', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:30:45.135 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 3/3 enviado. ID: 3EB09267DC9CBD3B829941E9F3B761130C6971EA
2025-08-04 03:30:45.140 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 03:30:45.140 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:53924 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 03:30:46.165 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:53924 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:44428 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:31:00.506 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 03:31:00.506 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:31:00.492Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:37508 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 03:31:00.538 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:37508 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 03:31:00.539 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Documento recebido: Boleto.pdf]', 'sender': '558182986181', 'type': 'text'}
2025-08-04 03:31:00.874 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:31:00.875 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:31:00.869Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:37508 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 03:31:00.933 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:31:00.933 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:31:00.927Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:37508 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 03:31:01.867 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:37508 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:31:01.874 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:31:01.874 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:37508 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 03:31:01.890 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:37508 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:31:01.899 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:37508 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:31:01.905 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:31:01.905 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:37508 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 03:31:01.909 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:31:01.909 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:37508 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INFO:     127.0.0.1:36630 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:31:30.539 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 32}
2025-08-04 03:31:34.265 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 DOCUMENTO DETECTADO - Analisando estrutura...
2025-08-04 03:31:34.265 | INFO     | app.api.webhooks:process_message_with_agent:520 | Campos disponíveis no documentMessage: ['url', 'mimetype', 'title', 'fileSha256', 'fileLength', 'pageCount', 'mediaKey', 'fileName', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'contactVcard', 'jpegThumbnail']
2025-08-04 03:31:34.265 | INFO     | app.api.webhooks:process_message_with_agent:521 | Nome do arquivo: Boleto.pdf
2025-08-04 03:31:34.266 | INFO     | app.api.webhooks:process_message_with_agent:522 | Mimetype: application/pdf
2025-08-04 03:31:34.266 | INFO     | app.api.webhooks:process_message_with_agent:528 | Documento tem thumbnail string: 872 chars
2025-08-04 03:31:34.266 | INFO     | app.integrations.evolution:download_media:853 | Baixando mídia de: https://mmg.whatsapp.net/v/t62.7119-24/11246508_22...
2025-08-04 03:31:34.311 | INFO     | app.integrations.evolution:download_media:873 | Mídia baixada com sucesso: 78410 bytes
2025-08-04 03:31:34.312 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 03:31:34.906 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:31:34.906 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:31:35.703 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 11 mensagens encontradas
2025-08-04 03:31:35.704 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:31:35.704 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:31:36.500 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 11 mensagens encontradas
2025-08-04 03:31:36.500 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 11 mensagens
2025-08-04 03:31:36.500 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:31:36.501 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-04 03:31:36.501 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: DOCUMENT
2025-08-04 03:31:36.501 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 104,548 caracteres
2025-08-04 03:31:36.501 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-04 03:31:36.502 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-04 03:31:36
2025-08-04 03:31:36.502 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:31:36.503 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: 4c57185dbd36f3b9ab4c2492
2025-08-04 03:31:36.503 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Formato de documento não reconhecido pelo AGNO: 4c57185dbd36f3b9ab4c2492
2025-08-04 03:31:36.503 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha | Data: {'decision_score': 0.3}
2025-08-04 03:31:36.504 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 11 mensagens, quality=fair, score=0.43
2025-08-04 03:31:39.746 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}