✅ Usando variáveis de ambiente do servidor (EasyPanel)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-03 22:43:01.948 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-03 22:43:01.953 | WARNING  | app.integrations.redis_client:connect:35 | Redis não disponível: Error -2 connecting to redis:6379. -2.. Sistema funcionará sem cache.
2025-08-03 22:43:01.953 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-03 22:43:02.265 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-03 22:43:02.265 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Buffer inicializado (timeout=30.0s, max=10)
2025-08-03 22:43:02.265 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-03 22:43:02.265 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=250 chars, smart=ativada)
2025-08-03 22:43:02.266 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 250}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-03 22:43:02.287 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-03 22:43:02.288 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-03 22:43:02.288 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-03 22:43:02.288 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-03 22:43:02.289 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-03 22:43:02.289 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-03 22:43:02.289 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-03 22:43:02.289 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-03 22:43:02.290 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-03 22:43:02.290 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-03 22:43:02.638 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-03 22:43:02.639 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-03 22:43:02.639 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-03 22:43:02.639 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-03 22:43:02.639 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-03 22:43:02.639 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-03 22:43:02.640 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-03 22:43:03.059 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-03 22:43:03.060 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-03 22:43:03.060 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 6}
2025-08-03 22:43:04.395 | INFO     | app.teams.agents.crm:initialize:159 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-03 22:43:04.395 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-03 22:43:04.395 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:47100 - "GET /health HTTP/1.1" 200 OK
2025-08-03 22:43:12.860 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-03 22:43:12.861 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:113 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T19:43:12.621Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:56712 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-03 22:43:12.862 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-03 22:43:12.862 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:113 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T19:43:12.661Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:56716 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-03 22:43:13.046 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-03 22:43:13.047 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:118 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHuBTIXkXWI6KOUGaN_znEY5CYj_Zrpw-f6z5CuAL-qJw&oe=689D094D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T19:43:13.038Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:56712 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-03 22:43:14.084 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:56712 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-03 22:43:14.085 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Imagem recebida]', 'sender': '558182986181', 'type': 'text'}
2025-08-03 22:43:14.437 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:56712 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-03 22:43:14.464 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-03 22:43:14.465 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:122 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:56712 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-03 22:43:14.489 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:56712 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-03 22:43:14.492 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-03 22:43:14.492 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:118 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHuBTIXkXWI6KOUGaN_znEY5CYj_Zrpw-f6z5CuAL-qJw&oe=689D094D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T19:43:14.472Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:56716 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-03 22:43:14.493 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-03 22:43:14.494 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:122 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:56716 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
INFO:     127.0.0.1:33684 - "GET /health HTTP/1.1" 200 OK
2025-08-03 22:43:44.086 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 17}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-03 22:43:45.550 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-03 22:43:45.550 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: agentic_sdr_sessions
2025-08-03 22:43:45.551 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelos configurados pronto | Data: {'primary_model': 'gemini-2.5-pro', 'reasoning_enabled': True}
2025-08-03 22:43:45.551 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-03 22:43:45.555 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base pronto | Data: {'status': 'ativo'}
2025-08-03 22:43:45.557 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-03 22:43:45.557 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-03 22:43:45.983 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-03 22:43:45.986 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-03 22:43:45.986 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-03 22:43:45.986 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-03 22:43:45.987 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-03 22:43:45.987 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-03 22:43:45.987 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-03 22:43:45.988 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-03 22:43:45.988 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-03 22:43:45.988 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-03 22:43:45.988 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-03 22:43:45.991 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-03 22:43:45.991 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-03 22:43:45.992 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-03 22:43:45.992 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-03 22:43:45.992 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-03 22:43:45.992 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-03 22:43:45.992 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-03 22:43:46.417 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-03 22:43:46.418 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-03 22:43:46.418 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-03 22:43:46.418 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-03 22:43:47.055 | INFO     | app.integrations.evolution:download_media:853 | Baixando mídia de: https://mmg.whatsapp.net/v/t62.7118-24/11281308_73...
2025-08-03 22:43:47.988 | INFO     | app.integrations.evolution:download_media:873 | Mídia baixada com sucesso: 23290 bytes
2025-08-03 22:43:50.205 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 0 mensagens
2025-08-03 22:43:50.597 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Formato de imagem não reconhecido. Magic bytes: cfee6a4ee9379ab2dbdcd2dc
2025-08-03 22:43:50.597 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-03 22:43:53.945 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
WARNING  MemoryDb not provided.                                                 
INFO:     127.0.0.1:40228 - "GET /health HTTP/1.1" 200 OK
2025-08-03 22:44:11.904 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Poxa, por algum motivo não estou conseguindo abrir a imagem que você me enviou. Será que você poderi...
2025-08-03 22:44:13.916 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem dividida em 2 partes | Data: {'phone': '558182986181', 'original_length': 274}
2025-08-03 22:44:21.216 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 137, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-03 22:44:21.217 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Poxa, por algum motivo não estou conseguindo abrir', 'recipient': '558182986181', 'type': 'text'}
2025-08-03 22:44:21.217 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 1/2 enviado. ID: 3EB0E889456FB4C8D7B0A86D9BBF732280290DF3
2025-08-03 22:44:21.429 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-03 22:44:21.429 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:122 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:58600 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-03 22:44:22.290 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:58600 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-03 22:44:29.307 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 136, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-03 22:44:29.307 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Ah, e antes que eu me esqueça, meu nome é Helen Vi', 'recipient': '558182986181', 'type': 'text'}
2025-08-03 22:44:29.308 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chunk 2/2 enviado. ID: 3EB03116E0248D1110DF3E93D9FD4E4C168C17A8
2025-08-03 22:44:29.316 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-03 22:44:29.317 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:122 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:34028 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-03 22:44:30.208 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:34028 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-03 22:44:35.410 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-03 22:44:35.410 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:113 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T19:44:35.396Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:46954 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-03 22:44:35.416 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-03 22:44:35.416 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:113 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T19:44:35.405Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:46954 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-03 22:44:35.454 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:46954 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-03 22:44:35.455 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': '[Documento recebido: Boleto.pdf]', 'sender': '558182986181', 'type': 'text'}
2025-08-03 22:44:35.791 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-03 22:44:35.792 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:118 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHuBTIXkXWI6KOUGaN_znEY5CYj_Zrpw-f6z5CuAL-qJw&oe=689D094D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T19:44:35.782Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:46954 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-03 22:44:35.846 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-03 22:44:35.847 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:118 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHuBTIXkXWI6KOUGaN_znEY5CYj_Zrpw-f6z5CuAL-qJw&oe=689D094D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T19:44:35.840Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:46954 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-03 22:44:37.115 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:46954 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-03 22:44:37.120 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-03 22:44:37.121 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:122 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:46954 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-03 22:44:37.137 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:46954 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-03 22:44:37.142 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-03 22:44:37.143 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:122 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:46954 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
INFO:     127.0.0.1:43328 - "GET /health HTTP/1.1" 200 OK
2025-08-03 22:45:05.456 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 32}
INFO:     127.0.0.1:57686 - "GET /health HTTP/1.1" 200 OK
2025-08-03 22:45:09.180 | INFO     | app.integrations.evolution:download_media:853 | Baixando mídia de: https://mmg.whatsapp.net/v/t62.7119-24/11246508_22...
2025-08-03 22:45:10.397 | INFO     | app.integrations.evolution:download_media:873 | Mídia baixada com sucesso: 78410 bytes
2025-08-03 22:45:12.392 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 0 mensagens
/root/.local/lib/python3.11/site-packages/pypdf/_crypt_providers/_cryptography.py:32: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  from cryptography.hazmat.primitives.ciphers.algorithms import AES, ARC4
2025-08-03 22:45:12.498 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ DocumentExtractor inicializado com pypdf e pdfplumber
2025-08-03 22:45:12.499 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando documento: application/octet-stream
2025-08-03 22:45:12.499 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-03 22:45:15.757 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
INFO:     127.0.0.1:50198 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-03 22:45:43.195 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Oii! Agora sim, recebi o documento, perfeito! Só um minutinho que já estou abrindo aqui pra gente ve...
2025-08-03 22:45:52.504 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 191, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-03 22:45:52.504 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Oii! Agora sim, recebi o documento, perfeito! Só u', 'recipient': '558182986181', 'type': 'text'}
2025-08-03 22:45:52.505 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB0F35A04A3F42185617F3C2A72DB0CE9220623
2025-08-03 22:45:52.715 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-03 22:45:52.716 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:122 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:43774 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-03 22:45:53.453 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:43774 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK