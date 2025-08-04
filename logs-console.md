INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-04 04:28:59.269 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-04 04:28:59.426 | WARNING  | app.integrations.redis_client:connect:35 | Redis não disponível: Error -2 connecting to redis:6379. -2.. Sistema funcionará sem cache.
2025-08-04 04:28:59.426 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-04 04:29:00.078 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-04 04:29:00.078 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Buffer inicializado (timeout=30.0s, max=10)
2025-08-04 04:29:00.078 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-04 04:29:00.079 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=250 chars, smart=ativada)
2025-08-04 04:29:00.079 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 250}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 04:29:00.102 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 04:29:00.103 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-04 04:29:00.103 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-04 04:29:00.104 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-04 04:29:00.104 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-04 04:29:00.104 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-04 04:29:00.105 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-04 04:29:00.105 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-04 04:29:00.105 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-04 04:29:00.105 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 04:29:00.472 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-04 04:29:00.472 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-04 04:29:00.472 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 04:29:00.472 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-04 04:29:00.473 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-04 04:29:00.473 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-04 04:29:00.473 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-04 04:29:01.270 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 04:29:01.271 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 04:29:01.271 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 6}
2025-08-04 04:29:02.235 | INFO     | app.teams.agents.crm:initialize:159 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-04 04:29:02.235 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-04 04:29:02.235 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:37806 - "GET /health HTTP/1.1" 200 OK
2025-08-04 04:29:10.517 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 04:29:10.518 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T01:29:10.293Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49230 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 04:29:10.519 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 04:29:10.519 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T01:29:10.345Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49244 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 04:29:10.730 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 04:29:10.730 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T01:29:10.723Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49244 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 04:29:11.412 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:49244 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 04:29:11.413 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Imagem recebida]', 'sender': '558182986181', 'type': 'text'}
2025-08-04 04:29:11.810 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 04:29:11.811 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T01:29:11.805Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:49244 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INFO:     127.0.0.1:33390 - "GET /health HTTP/1.1" 200 OK
2025-08-04 04:29:41.413 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 17}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 04:29:44.283 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 04:29:44.283 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: agentic_sdr_sessions
2025-08-04 04:29:44.283 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-04 04:29:44.284 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo fallback OpenAI o3-mini configurado pronto
2025-08-04 04:29:44.284 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-04 04:29:44.284 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-04 04:29:44.284 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 04:29:44.288 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base pronto | Data: {'status': 'ativo'}
2025-08-04 04:29:44.289 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-04 04:29:44.289 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-04 04:29:45.079 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-04 04:29:45.082 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-04 04:29:45.082 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-04 04:29:45.082 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-04 04:29:45.083 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-04 04:29:45.083 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-04 04:29:45.083 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-04 04:29:45.083 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-04 04:29:45.083 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-04 04:29:45.084 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-04 04:29:45.084 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 04:29:45.087 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-04 04:29:45.087 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-04 04:29:45.088 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 04:29:45.088 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-04 04:29:45.088 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-04 04:29:45.088 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-04 04:29:45.089 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-04 04:29:45.486 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 04:29:45.487 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 04:29:45.487 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-04 04:29:45.487 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-04 04:29:46.115 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📸 IMAGEM DETECTADA - Analisando estrutura...
2025-08-04 04:29:46.115 | INFO     | app.api.webhooks:process_message_with_agent:415 | Campos disponíveis na imageMessage: ['url', 'mimetype', 'fileSha256', 'fileLength', 'height', 'width', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'jpegThumbnail', 'contextInfo', 'firstScanSidecar', 'firstScanLength', 'scansSidecar', 'scanLengths', 'midQualityFileSha256', 'imageSourceType']
2025-08-04 04:29:46.115 | INFO     | app.api.webhooks:process_message_with_agent:422 | jpegThumbnail é string, tamanho: 868 chars
2025-08-04 04:29:46.115 | INFO     | app.api.webhooks:process_message_with_agent:423 | jpegThumbnail primeiros 50 chars: /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHB
2025-08-04 04:29:46.116 | INFO     | app.api.webhooks:process_message_with_agent:426 | jpegThumbnail parece ser base64 válido
2025-08-04 04:29:46.116 | INFO     | app.api.webhooks:process_message_with_agent:433 | mediaKey presente: bKAgOYLhpEHewOz/Fcfb...
2025-08-04 04:29:46.116 | INFO     | app.api.webhooks:process_message_with_agent:435 | directPath presente: /v/t62.7118-24/11281308_731162479780705_8333746825...
2025-08-04 04:29:46.116 | INFO     | app.api.webhooks:process_message_with_agent:437 | URL presente: https://mmg.whatsapp.net/v/t62.7118-24/11281308_73...
2025-08-04 04:29:46.116 | INFO     | app.api.webhooks:detect_media_format:63 | Formato detectado: Base64 válido
2025-08-04 04:29:46.116 | INFO     | app.api.webhooks:process_message_with_agent:445 | 📸 jpegThumbnail formato detectado: base64
2025-08-04 04:29:46.117 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-04 04:29:46.117 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ jpegThumbnail validado como base64: 868 chars
2025-08-04 04:29:46.117 | INFO     | app.api.webhooks:process_message_with_agent:487 | 🔍 Thumbnail muito pequena (868 chars), baixando imagem completa...
2025-08-04 04:29:46.118 | INFO     | app.api.webhooks:process_message_with_agent:505 | 🔐 Incluindo mediaKey para descriptografia
2025-08-04 04:29:46.118 | INFO     | app.integrations.evolution:download_media:955 | Baixando mídia de: https://mmg.whatsapp.net/v/t62.7118-24/11281308_73...
2025-08-04 04:29:46.118 | INFO     | app.integrations.evolution:download_media:957 | MediaKey presente - mídia será descriptografada (tipo: image)
2025-08-04 04:29:46.155 | INFO     | app.integrations.evolution:download_media:977 | Mídia baixada com sucesso: 23290 bytes
2025-08-04 04:29:46.156 | INFO     | app.integrations.evolution:download_media:981 | Iniciando descriptografia da mídia...
2025-08-04 04:29:46.156 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:856 | MediaKey decodificada: 32 bytes
2025-08-04 04:29:46.157 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:889 | IV: 16 bytes, Cipher Key: 32 bytes, MAC Key: 32 bytes
2025-08-04 04:29:46.158 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:925 | Mídia descriptografada com sucesso: 23266 bytes
2025-08-04 04:29:46.158 | INFO     | app.integrations.evolution:download_media:989 | Mídia descriptografada com sucesso: 23266 bytes
2025-08-04 04:29:46.158 | INFO     | app.api.webhooks:process_message_with_agent:511 | Imagem baixada, primeiros 20 bytes (hex): ffd8ffe000104a46494600010100000100010000
2025-08-04 04:29:46.159 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-04 04:29:46.159 | INFO     | app.api.webhooks:process_message_with_agent:534 | 🔍 AGNO validou mídia: jpeg
2025-08-04 04:29:46.159 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Imagem validada (jpeg): 31024 chars
2025-08-04 04:29:46.160 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 04:29:46.734 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 04:29:46.734 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 04:29:47.729 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 31 mensagens encontradas
2025-08-04 04:29:47.731 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 04:29:47.731 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 04:29:49.109 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 31 mensagens encontradas
2025-08-04 04:29:49.109 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 31 mensagens
2025-08-04 04:29:49.110 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 04:29:49.110 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-04 04:29:49.110 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: IMAGE
2025-08-04 04:29:49.110 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 31,024 caracteres
2025-08-04 04:29:49.110 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-04 04:29:49.110 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-04 04:29:49
2025-08-04 04:29:49.110 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 04:29:49.111 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-04 04:29:49.111 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 PROCESSAMENTO DE IMAGEM INICIADO
2025-08-04 04:29:49.111 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-04 04:29:49.111 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 IMAGEM - Formato detectado: base64
2025-08-04 04:29:49.111 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📈 IMAGEM - Métricas:
2025-08-04 04:29:49.111 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Base64: 31,024 caracteres
2025-08-04 04:29:49.111 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Estimado: 23,268 bytes (22.7 KB / 0.02 MB)
2025-08-04 04:29:49.112 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⚠️ IMAGEM: Possível thumbnail detectada (<50KB)
2025-08-04 04:29:49.506 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 1/4: Decodificando base64...
2025-08-04 04:29:49.506 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Decodificação completa em 0.00s
2025-08-04 04:29:49.507 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tamanho real: 23,266 bytes
2025-08-04 04:29:49.507 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Taxa compressão: 25.0%
2025-08-04 04:29:49.507 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 2/4: Detectando formato da imagem...
2025-08-04 04:29:49.507 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-04 04:29:49.507 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato detectado: JPEG
2025-08-04 04:29:49.507 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Confiança: high
2025-08-04 04:29:49.507 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo detecção: 0.00s
2025-08-04 04:29:49.507 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha | Data: {'decision_score': 0.3}
2025-08-04 04:29:49.508 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 31 mensagens, quality=excellent, score=0.60
2025-08-04 04:29:52.852 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
INFO:     127.0.0.1:53378 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 04:30:11.607 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Mateus, meu amigo, você é persistente, viu? hehehe Olha, vou te pedir uma coisa com todo o carinho d...
2025-08-04 04:30:13.620 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem dividida em 3 partes | Data: {'phone': '558182986181', 'original_length': 544}
2025-08-04 04:30:20.915 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 163, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 04:30:20.916 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Mateus, meu amigo, você é persistente, viu? hehehe', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 04:30:20.916 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 1/3 enviado. ID: 3EB0104CB4225BBD206D1E5FDD6111D42BA91D64
2025-08-04 04:30:21.127 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 04:30:21.128 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:44432 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 04:30:22.079 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:44432 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 04:30:29.022 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 233, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 04:30:29.023 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Eu já entendi perfeitamente, já vi que o prejuízo ', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 04:30:29.023 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 2/3 enviado. ID: 3EB0B13291E0B89E14D626669743191C75BAC3B2
2025-08-04 04:30:29.027 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 04:30:29.027 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:55552 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 04:30:29.988 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:55552 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:42882 - "GET /health HTTP/1.1" 200 OK
2025-08-04 04:30:37.210 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 04:30:37.210 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:51790 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 04:30:37.212 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 146, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 04:30:37.212 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'A gente foca 100% na solução agora. Pra começar, m', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 04:30:37.212 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 3/3 enviado. ID: 3EB06FEFBC93B2813F0DC29FB979A2B7E3AC2145
2025-08-04 04:30:38.030 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:51790 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:45586 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:53254 - "GET /health HTTP/1.1" 200 OK
2025-08-04 04:31:58.057 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:60936 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-04 04:31:58.359 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 04:31:58.359 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T01:31:58.350Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:60936 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 04:31:58.366 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 04:31:58.367 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T01:31:58.361Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:60936 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 04:31:58.386 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:60936 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 04:31:58.387 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'oi', 'sender': '558182986181', 'type': 'text'}
2025-08-04 04:31:58.744 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 04:31:58.744 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T01:31:58.738Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:60936 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 04:31:58.783 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 04:31:58.783 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T01:31:58.777Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:60936 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:37848 - "GET /health HTTP/1.1" 200 OK
2025-08-04 04:32:28.389 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 2}
2025-08-04 04:32:30.794 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 04:32:31.380 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 04:32:31.380 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 04:32:31.605 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 1 mensagens encontradas
2025-08-04 04:32:31.605 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 04:32:31.606 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 04:32:31.817 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 1 mensagens encontradas
2025-08-04 04:32:31.818 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 1 mensagens
2025-08-04 04:32:31.818 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-04 04:32:31.818 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 1 mensagens, quality=minimal, score=0.01
2025-08-04 04:32:35.062 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
INFO:     127.0.0.1:48606 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 04:32:56.220 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Oii! Seja muito bem-vindo à Solar Prime! Meu nome é Helen Vieira. Sou consultora especialista aqui d...
2025-08-04 04:33:03.521 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 167, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 04:33:03.522 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Oii! Seja muito bem-vindo à Solar Prime! Meu nome ', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 04:33:03.522 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB05A897ED7D469D0922FBF05FFC67EA17DBE92
2025-08-04 04:33:04.191 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 04:33:04.192 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:35684 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 04:33:04.650 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:35684 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-04 04:33:09.305 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:35684 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:59666 - "GET /health HTTP/1.1" 200 OK
2025-08-04 04:33:10.187 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-04 04:33:10.187 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:175 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T01:33:10.181Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:35684 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-04 04:33:10.201 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:35684 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-04 04:33:10.202 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'mateus', 'sender': '558182986181', 'type': 'text'}
2025-08-04 04:33:10.563 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 04:33:10.563 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T01:33:10.558Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:35684 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-04 04:33:10.592 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-04 04:33:10.593 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:180 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHZdoniXw0cTYWlhW79TSw52zm7Y3ahQ88MBtUMZknIiQ&oe=689D418D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-04T01:33:10.588Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:35684 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK