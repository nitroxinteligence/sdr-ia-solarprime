✅ Usando variáveis de ambiente do servidor (EasyPanel)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-04 03:14:50.014 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-04 03:14:50.021 | WARNING  | app.integrations.redis_client:connect:35 | Redis não disponível: Error -2 connecting to redis:6379. -2.. Sistema funcionará sem cache.
2025-08-04 03:14:50.022 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-04 03:14:50.891 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-04 03:14:50.892 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Buffer inicializado (timeout=30.0s, max=10)
2025-08-04 03:14:50.892 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-04 03:14:50.892 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=250 chars, smart=ativada)
2025-08-04 03:14:50.892 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 250}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 03:14:50.912 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 03:14:50.912 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-04 03:14:50.912 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-04 03:14:50.913 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-04 03:14:50.913 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-04 03:14:50.913 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-04 03:14:50.913 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-04 03:14:50.913 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-04 03:14:50.914 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-04 03:14:50.914 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 03:14:51.204 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-04 03:14:51.204 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-04 03:14:51.204 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 03:14:51.204 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-04 03:14:51.205 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-04 03:14:51.205 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-04 03:14:51.205 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-04 03:14:51.999 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 03:14:51.999 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 03:14:51.999 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 6}
2025-08-04 03:14:52.998 | INFO     | app.teams.agents.crm:initialize:159 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-04 03:14:52.999 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-04 03:14:52.999 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:44398 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:15:05.920 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 03:15:05.920 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:174 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:15:05.711Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:60988 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 03:15:05.922 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 03:15:05.922 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:174 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:15:05.680Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:32768 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 03:15:06.094 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:15:06.094 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:179 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:15:06.088Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:32768 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 03:15:06.916 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:32768 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:15:06.928 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:15:06.929 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:32768 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 03:15:07.175 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:32768 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 03:15:07.176 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Imagem recebida]', 'sender': '558182986181', 'type': 'text'}
2025-08-04 03:15:07.575 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:15:07.576 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:179 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:15:07.569Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:32768 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:38394 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:15:37.177 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 17}

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 03:15:40.439 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 03:15:40.439 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: agentic_sdr_sessions
2025-08-04 03:15:40.439 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-04 03:15:40.440 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-04 03:15:40.440 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-04 03:15:40.440 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-04 03:15:40.440 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 03:15:40.443 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base pronto | Data: {'status': 'ativo'}
2025-08-04 03:15:40.444 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-04 03:15:40.444 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-04 03:15:41.238 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 03:15:41.241 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 03:15:41.241 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-04 03:15:41.241 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-04 03:15:41.242 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-04 03:15:41.242 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-04 03:15:41.242 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-04 03:15:41.242 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-04 03:15:41.242 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-04 03:15:41.242 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-04 03:15:41.243 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 03:15:41.245 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-04 03:15:41.246 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-04 03:15:41.246 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 03:15:41.246 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-04 03:15:41.246 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-04 03:15:41.246 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-04 03:15:41.247 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-04 03:15:41.670 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 03:15:41.671 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 03:15:41.671 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-04 03:15:41.671 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-04 03:15:42.279 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📸 IMAGEM DETECTADA - Analisando estrutura...
2025-08-04 03:15:42.279 | INFO     | app.api.webhooks:process_message_with_agent:414 | Campos disponíveis na imageMessage: ['url', 'mimetype', 'fileSha256', 'fileLength', 'height', 'width', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'jpegThumbnail', 'contextInfo', 'firstScanSidecar', 'firstScanLength', 'scansSidecar', 'scanLengths', 'midQualityFileSha256', 'imageSourceType']
2025-08-04 03:15:42.280 | INFO     | app.api.webhooks:process_message_with_agent:421 | jpegThumbnail é string, tamanho: 1088 chars
2025-08-04 03:15:42.280 | INFO     | app.api.webhooks:process_message_with_agent:422 | jpegThumbnail primeiros 50 chars: /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHB
2025-08-04 03:15:42.280 | INFO     | app.api.webhooks:process_message_with_agent:425 | jpegThumbnail parece ser base64 válido
2025-08-04 03:15:42.280 | INFO     | app.api.webhooks:process_message_with_agent:432 | mediaKey presente: 7GQyoDY8MkBZJA6SOeTq...
2025-08-04 03:15:42.280 | INFO     | app.api.webhooks:process_message_with_agent:434 | directPath presente: /v/t62.7118-24/25387842_752696437341201_4493947754...
2025-08-04 03:15:42.281 | INFO     | app.api.webhooks:process_message_with_agent:436 | URL presente: https://mmg.whatsapp.net/v/t62.7118-24/25387842_75...
2025-08-04 03:15:42.281 | INFO     | app.api.webhooks:detect_media_format:62 | Formato detectado: Base64 válido
2025-08-04 03:15:42.281 | INFO     | app.api.webhooks:process_message_with_agent:444 | 📸 jpegThumbnail formato detectado: base64
2025-08-04 03:15:42.281 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ jpegThumbnail validado como base64: 1088 chars
2025-08-04 03:15:42.281 | WARNING  | app.api.webhooks:process_message_with_agent:502 | Erro na validação AGNO: cannot access local variable 'base64' where it is not associated with a value
2025-08-04 03:15:42.281 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Imagem pronta (sem validação AGNO): 1088 chars
2025-08-04 03:15:42.282 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 03:15:42.513 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:15:42.513 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:15:44.358 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 100 mensagens encontradas
2025-08-04 03:15:44.362 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:15:44.362 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:15:46.207 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 100 mensagens encontradas
2025-08-04 03:15:46.208 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 100 mensagens
2025-08-04 03:15:46.208 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:15:46.208 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-04 03:15:46.208 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: IMAGE
2025-08-04 03:15:46.208 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 1,088 caracteres
2025-08-04 03:15:46.208 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-04 03:15:46.208 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-04 03:15:46
2025-08-04 03:15:46.209 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:15:46.209 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-04 03:15:46.209 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 PROCESSAMENTO DE IMAGEM INICIADO
2025-08-04 03:15:46.209 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-04 03:15:46.210 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 IMAGEM - Formato detectado: base64
2025-08-04 03:15:46.210 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📈 IMAGEM - Métricas:
2025-08-04 03:15:46.210 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Base64: 1,088 caracteres
2025-08-04 03:15:46.210 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Estimado: 816 bytes (0.8 KB / 0.00 MB)
2025-08-04 03:15:46.210 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⚠️ IMAGEM: Possível thumbnail detectada (<50KB)
2025-08-04 03:15:46.572 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 1/4: Decodificando base64...
2025-08-04 03:15:46.573 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Decodificação completa em 0.00s
2025-08-04 03:15:46.573 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tamanho real: 815 bytes
2025-08-04 03:15:46.573 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Taxa compressão: 25.1%
2025-08-04 03:15:46.573 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 2/4: Detectando formato da imagem...
2025-08-04 03:15:46.573 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-04 03:15:46.573 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato detectado: JPEG
2025-08-04 03:15:46.573 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Confiança: high
2025-08-04 03:15:46.574 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo detecção: 0.00s
2025-08-04 03:15:46.574 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-04 03:15:46.575 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 50 mensagens, quality=excellent, score=0.60
2025-08-04 03:15:49.914 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
INFO:     127.0.0.1:50676 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 03:16:08.009 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Mateus, este atendimento foi encerrado de forma definitiva e não será retomado. A sua conduta violou...
2025-08-04 03:16:15.076 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 223, 'delay_used': 2.77, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:16:15.077 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Mateus, este atendimento foi encerrado de forma de', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:16:15.077 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB0C7D2CD59DB1C53B0D5F78B2567B283C469BD
2025-08-04 03:16:15.287 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 03:16:15.287 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:56424 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 03:16:16.375 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:56424 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:57750 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:40112 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:17:00.414 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 03:17:00.414 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:174 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, {'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:17:00.399Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:37120 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 03:17:00.781 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:17:00.782 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:179 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:17:00.777Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:37120 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 03:17:01.352 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:37120 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 03:17:01.354 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Imagem recebida] Analise esta imagem', 'sender': '558182986181', 'type': 'text'}
2025-08-04 03:17:01.574 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:37120 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:17:01.580 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:17:01.581 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:37120 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 03:17:01.795 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:17:01.796 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:179 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:17:01.789Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:37120 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INFO:     127.0.0.1:57792 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:17:31.354 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 37}
2025-08-04 03:17:35.718 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📸 IMAGEM DETECTADA - Analisando estrutura...
2025-08-04 03:17:35.719 | INFO     | app.api.webhooks:process_message_with_agent:414 | Campos disponíveis na imageMessage: ['url', 'mimetype', 'caption', 'fileSha256', 'fileLength', 'height', 'width', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'jpegThumbnail', 'contextInfo', 'firstScanSidecar', 'firstScanLength', 'scansSidecar', 'scanLengths', 'midQualityFileSha256', 'imageSourceType']
2025-08-04 03:17:35.719 | INFO     | app.api.webhooks:process_message_with_agent:421 | jpegThumbnail é string, tamanho: 868 chars
2025-08-04 03:17:35.719 | INFO     | app.api.webhooks:process_message_with_agent:422 | jpegThumbnail primeiros 50 chars: /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHB
2025-08-04 03:17:35.719 | INFO     | app.api.webhooks:process_message_with_agent:425 | jpegThumbnail parece ser base64 válido
2025-08-04 03:17:35.719 | INFO     | app.api.webhooks:process_message_with_agent:432 | mediaKey presente: bKAgOYLhpEHewOz/Fcfb...
2025-08-04 03:17:35.719 | INFO     | app.api.webhooks:process_message_with_agent:434 | directPath presente: /v/t62.7118-24/11281308_731162479780705_8333746825...
2025-08-04 03:17:35.719 | INFO     | app.api.webhooks:process_message_with_agent:436 | URL presente: https://mmg.whatsapp.net/v/t62.7118-24/11281308_73...
2025-08-04 03:17:35.720 | INFO     | app.api.webhooks:detect_media_format:62 | Formato detectado: Base64 válido
2025-08-04 03:17:35.720 | INFO     | app.api.webhooks:process_message_with_agent:444 | 📸 jpegThumbnail formato detectado: base64
2025-08-04 03:17:35.720 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ jpegThumbnail validado como base64: 868 chars
2025-08-04 03:17:35.720 | WARNING  | app.api.webhooks:process_message_with_agent:502 | Erro na validação AGNO: cannot access local variable 'base64' where it is not associated with a value
2025-08-04 03:17:35.720 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Imagem pronta (sem validação AGNO): 868 chars
2025-08-04 03:17:35.720 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 03:17:36.285 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:17:36.286 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:17:37.069 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 1 mensagens encontradas
2025-08-04 03:17:37.070 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:17:37.070 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:17:37.304 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 1 mensagens encontradas
2025-08-04 03:17:37.305 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 1 mensagens
2025-08-04 03:17:37.305 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:17:37.305 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-04 03:17:37.305 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: IMAGE
2025-08-04 03:17:37.306 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 868 caracteres
2025-08-04 03:17:37.306 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Analise esta imagem
2025-08-04 03:17:37.306 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-04 03:17:37
2025-08-04 03:17:37.306 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:17:37.306 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-04 03:17:37.307 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 PROCESSAMENTO DE IMAGEM INICIADO
2025-08-04 03:17:37.307 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-04 03:17:37.307 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 IMAGEM - Formato detectado: base64
2025-08-04 03:17:37.307 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📈 IMAGEM - Métricas:
2025-08-04 03:17:37.308 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Base64: 868 caracteres
2025-08-04 03:17:37.308 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Estimado: 651 bytes (0.6 KB / 0.00 MB)
2025-08-04 03:17:37.308 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⚠️ IMAGEM: Possível thumbnail detectada (<50KB)
2025-08-04 03:17:37.308 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 1/4: Decodificando base64...
2025-08-04 03:17:37.309 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Decodificação completa em 0.00s
2025-08-04 03:17:37.309 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tamanho real: 649 bytes
2025-08-04 03:17:37.309 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Taxa compressão: 25.2%
2025-08-04 03:17:37.309 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 2/4: Detectando formato da imagem...
2025-08-04 03:17:37.309 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-04 03:17:37.310 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato detectado: JPEG
2025-08-04 03:17:37.310 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Confiança: high
2025-08-04 03:17:37.310 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo detecção: 0.00s
2025-08-04 03:17:37.310 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-04 03:17:37.310 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 1 mensagens, quality=minimal, score=0.36
2025-08-04 03:17:40.548 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
INFO:     127.0.0.1:42494 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 03:18:05.650 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Oii! Seja muito bem-vindo à Solar Prime! Meu nome é Helen Vieira, sou consultora especialista aqui e...
2025-08-04 03:18:07.661 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem dividida em 2 partes | Data: {'phone': '558182986181', 'original_length': 299}
2025-08-04 03:18:14.961 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 215, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:18:14.962 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Oii! Seja muito bem-vindo à Solar Prime! Meu nome ', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:18:14.962 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 1/2 enviado. ID: 3EB0FFE632FE3384B9A61501B7A3B5AD67336073
2025-08-04 03:18:15.175 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 03:18:15.175 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:36380 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 03:18:16.016 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:36380 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:18:23.051 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 83, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:18:23.051 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Fique tranquilo que a gente vai resolver isso. Ant', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:18:23.052 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 2/2 enviado. ID: 3EB097CED41DDAE45E0C9290D302273D8FC53BC7
2025-08-04 03:18:23.058 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 03:18:23.058 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:55568 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 03:18:23.947 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:55568 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:55064 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:18:43.623 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 03:18:43.623 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:174 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:18:43.610Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:40438 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 03:18:43.664 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:40438 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 03:18:43.665 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Documento recebido: Boleto.pdf]', 'sender': '558182986181', 'type': 'text'}
2025-08-04 03:18:43.993 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:18:43.994 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:179 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:18:43.988Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:40438 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 03:18:44.056 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:18:44.056 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:179 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:18:44.050Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:40438 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 03:18:44.892 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:40438 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:18:44.898 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:18:44.898 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:40438 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 03:18:44.922 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:40438 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:18:44.928 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:18:44.929 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:40438 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INFO:     127.0.0.1:47966 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:19:13.666 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 32}
2025-08-04 03:19:16.733 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 DOCUMENTO DETECTADO - Analisando estrutura...
2025-08-04 03:19:16.733 | INFO     | app.api.webhooks:process_message_with_agent:518 | Campos disponíveis no documentMessage: ['url', 'mimetype', 'title', 'fileSha256', 'fileLength', 'pageCount', 'mediaKey', 'fileName', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'contactVcard', 'jpegThumbnail']
2025-08-04 03:19:16.734 | INFO     | app.api.webhooks:process_message_with_agent:519 | Nome do arquivo: Boleto.pdf
2025-08-04 03:19:16.734 | INFO     | app.api.webhooks:process_message_with_agent:520 | Mimetype: application/pdf
2025-08-04 03:19:16.734 | INFO     | app.api.webhooks:process_message_with_agent:526 | Documento tem thumbnail string: 872 chars
2025-08-04 03:19:16.734 | INFO     | app.integrations.evolution:download_media:853 | Baixando mídia de: https://mmg.whatsapp.net/v/t62.7119-24/11246508_22...
2025-08-04 03:19:16.770 | INFO     | app.integrations.evolution:download_media:873 | Mídia baixada com sucesso: 78410 bytes
2025-08-04 03:19:16.771 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 03:19:16.986 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:19:16.987 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:19:17.570 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 3 mensagens encontradas
2025-08-04 03:19:17.571 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:19:17.571 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:19:18.185 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 3 mensagens encontradas
2025-08-04 03:19:18.186 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 3 mensagens
2025-08-04 03:19:18.186 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:19:18.186 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-04 03:19:18.186 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: DOCUMENT
2025-08-04 03:19:18.186 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 104,548 caracteres
2025-08-04 03:19:18.186 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-04 03:19:18.187 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-04 03:19:18
2025-08-04 03:19:18.187 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:19:18.187 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: 4c57185dbd36f3b9ab4c2492
2025-08-04 03:19:18.188 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Formato de documento não reconhecido pelo AGNO: 4c57185dbd36f3b9ab4c2492
2025-08-04 03:19:18.188 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-04 03:19:18.188 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 3 mensagens, quality=minimal, score=0.35
2025-08-04 03:19:21.431 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
INFO:     127.0.0.1:41068 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 03:19:41.471 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Recebi o boleto aqui e agora entendi... nossa, com um valor desses eu também estaria buscando uma so...
2025-08-04 03:19:43.473 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem dividida em 3 partes | Data: {'phone': '558182986181', 'original_length': 550}
2025-08-04 03:19:50.763 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 210, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:19:50.764 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Recebi o boleto aqui e agora entendi... nossa, com', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:19:50.764 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 1/3 enviado. ID: 3EB07C99FF3BCB8EE505C22D7CDF0D4028F76D0F
2025-08-04 03:19:50.974 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 03:19:50.975 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:54218 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 03:19:55.672 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 238, 'delay_used': 1.82, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:19:55.673 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Mas a boa notícia é que pra contas como a sua, a g', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:19:55.673 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 2/3 enviado. ID: 3EB05569978B26F31E440ED21E3FD4DB9D4A919E
2025-08-04 03:19:55.675 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 03:19:55.675 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:54218 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 03:19:56.640 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:54218 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:43584 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:20:03.785 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 100, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:20:03.785 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Faz sentido pra você? Ah, e desculpa a pressa, ain', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 03:20:03.786 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 3/3 enviado. ID: 3EB09276B6D3FEA18216CD311AB1DCB88BFBA062
2025-08-04 03:20:03.791 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 03:20:03.791 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:40394 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 03:20:04.716 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:40394 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:45218 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:20:42.314 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:38110 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-04 03:20:45.952 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:38110 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-04 03:20:46.448 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 03:20:46.448 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:174 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:20:46.429Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:38110 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 03:20:46.811 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:20:46.812 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:179 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:20:46.806Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:38110 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 03:20:47.298 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:38110 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 03:20:47.298 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Nota de voz recebida]', 'sender': '558182986181', 'type': 'text'}
2025-08-04 03:20:47.637 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:38110 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:20:47.647 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:20:47.648 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:38110 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 03:20:47.659 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:38110 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:20:47.671 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:38110 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 03:20:47.672 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:20:47.672 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:38110 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 03:20:47.673 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-04 03:20:47.673 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:183 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:38126 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-04 03:20:47.689 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 03:20:47.689 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:179 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T00:20:47.684Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:38126 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INFO:     127.0.0.1:48864 - "GET /health HTTP/1.1" 200 OK
2025-08-04 03:21:17.299 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 22}
2025-08-04 03:21:20.024 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎵 ÁUDIO DETECTADO - Analisando estrutura...
2025-08-04 03:21:20.024 | INFO     | app.api.webhooks:process_message_with_agent:563 | Campos disponíveis no audioMessage: ['url', 'mimetype', 'fileSha256', 'fileLength', 'seconds', 'ptt', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'streamingSidecar', 'waveform']
2025-08-04 03:21:20.025 | INFO     | app.api.webhooks:process_message_with_agent:564 | Mimetype: audio/ogg; codecs=opus
2025-08-04 03:21:20.025 | INFO     | app.api.webhooks:process_message_with_agent:565 | Duração: 3 segundos
2025-08-04 03:21:20.025 | INFO     | app.api.webhooks:process_message_with_agent:566 | É nota de voz (ptt): True
2025-08-04 03:21:20.025 | INFO     | app.api.webhooks:process_message_with_agent:570 | mediaKey presente: mH634vNUIhWTJbKAOItL...
2025-08-04 03:21:20.025 | INFO     | app.api.webhooks:process_message_with_agent:572 | directPath presente: /v/t62.7117-24/528079263_1992285254844378_83080704...
2025-08-04 03:21:20.025 | INFO     | app.integrations.evolution:download_media:853 | Baixando mídia de: https://mmg.whatsapp.net/v/t62.7117-24/528079263_1...
2025-08-04 03:21:20.228 | INFO     | app.integrations.evolution:download_media:873 | Mídia baixada com sucesso: 7722 bytes
2025-08-04 03:21:20.228 | INFO     | app.api.webhooks:process_message_with_agent:586 | Áudio baixado, primeiros 20 bytes (hex): fd2c6d3e91422ea661e01a9cc373ea503b2208d3
2025-08-04 03:21:20.228 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Erro ao baixar áudio: 'AGNOMediaDetector' object has no attribute 'detect'
2025-08-04 03:21:20.229 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 03:21:20.809 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:21:20.809 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:21:21.382 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 5 mensagens encontradas
2025-08-04 03:21:21.383 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:21:21.383 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:21:22.354 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 5 mensagens encontradas
2025-08-04 03:21:22.355 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 5 mensagens
2025-08-04 03:21:22.355 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:21:22.355 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-04 03:21:22.355 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: AUDIO
2025-08-04 03:21:22.355 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 0 caracteres
2025-08-04 03:21:22.356 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-04 03:21:22.356 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-04 03:21:22
2025-08-04 03:21:22.356 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:21:22.356 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ❌ MULTIMODAL: Dados vazios para audio
2025-08-04 03:21:22.356 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⏱️ Tempo decorrido: 0.00s
2025-08-04 03:21:22.356 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha | Data: {'decision_score': 0.3}
2025-08-04 03:21:22.357 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 5 mensagens, quality=poor, score=0.38
2025-08-04 03:21:25.602 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}