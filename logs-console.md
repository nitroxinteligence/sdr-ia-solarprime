✅ Usando variáveis de ambiente do servidor (EasyPanel)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-03 20:38:12.517 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-03 20:38:12.521 | WARNING  | app.integrations.redis_client:connect:35 | Redis não disponível: Error -2 connecting to redis:6379. -2.. Sistema funcionará sem cache.
2025-08-03 20:38:12.521 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-03 20:38:12.984 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-03 20:38:12.984 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Buffer inicializado (timeout=30.0s, max=10)
2025-08-03 20:38:12.984 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-03 20:38:12.984 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=250 chars, smart=ativada)
2025-08-03 20:38:12.984 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 250}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-03 20:38:13.006 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-03 20:38:13.006 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-03 20:38:13.007 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-03 20:38:13.007 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-03 20:38:13.007 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-03 20:38:13.008 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-03 20:38:13.008 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-03 20:38:13.008 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-03 20:38:13.008 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-03 20:38:13.008 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-03 20:38:13.343 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-03 20:38:13.344 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-03 20:38:13.344 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-03 20:38:13.344 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-03 20:38:13.344 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-03 20:38:13.345 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-03 20:38:13.345 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-03 20:38:13.757 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-03 20:38:13.758 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-03 20:38:13.758 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 6}
2025-08-03 20:38:14.874 | INFO     | app.teams.agents.crm:initialize:159 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-03 20:38:14.875 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
INFO:     Application startup complete.
2025-08-03 20:38:14.875 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:46406 - "GET /health HTTP/1.1" 200 OK
2025-08-03 20:38:18.339 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-03 20:38:18.339 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:113 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T17:38:18.323Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:41780 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-03 20:38:18.349 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-03 20:38:18.350 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:113 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T17:38:18.337Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:41780 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-03 20:38:18.375 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:41780 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-03 20:38:18.377 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'olá', 'sender': '558182986181', 'type': 'text'}
2025-08-03 20:38:18.714 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-03 20:38:18.715 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:118 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHXbqRCwsprdQRhih51sfn6gTQPEfHG-k9yyq4EtEMH8Q&oe=689CD10D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T17:38:18.709Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:41780 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-03 20:38:18.763 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-03 20:38:18.763 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:118 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHXbqRCwsprdQRhih51sfn6gTQPEfHG-k9yyq4EtEMH8Q&oe=689CD10D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T17:38:18.758Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:41780 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-03 20:38:18.858 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:41780 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-03 20:38:24.936 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:57914 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:50574 - "GET /health HTTP/1.1" 200 OK
2025-08-03 20:38:48.963 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 3}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-03 20:38:50.488 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-03 20:38:50.489 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: agentic_sdr_sessions
2025-08-03 20:38:50.489 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelos configurados pronto | Data: {'primary_model': 'gemini-2.5-pro', 'reasoning_enabled': True}
2025-08-03 20:38:50.489 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-03 20:38:50.492 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base pronto | Data: {'status': 'ativo'}
2025-08-03 20:38:50.492 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-03 20:38:50.492 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-03 20:38:51.288 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-03 20:38:51.290 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-03 20:38:51.291 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-03 20:38:51.291 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-03 20:38:51.291 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-03 20:38:51.292 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-03 20:38:51.292 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-03 20:38:51.292 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-03 20:38:51.292 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-03 20:38:51.293 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-03 20:38:51.293 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-03 20:38:51.295 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-03 20:38:51.295 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-03 20:38:51.296 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-03 20:38:51.296 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-03 20:38:51.296 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-03 20:38:51.296 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-03 20:38:51.296 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-03 20:38:51.701 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-03 20:38:51.701 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-03 20:38:51.702 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-03 20:38:51.702 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-03 20:38:53.820 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-03 20:38:57.162 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
WARNING  MemoryDb not provided.                                                 
2025-08-03 20:39:03.755 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Oii! Tudo bem? Seja muito bem-vindo à Solar Prime! Meu nome é Helen Vieira, sou consultora especiali...
2025-08-03 20:39:11.049 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 183, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-03 20:39:11.049 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Oii! Tudo bem? Seja muito bem-vindo à Solar Prime!', 'recipient': '558182986181', 'type': 'text'}
2025-08-03 20:39:11.049 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB0F94254A5E1D72D02D231DFFDA4D5E0AFA1D3
2025-08-03 20:39:12.478 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-03 20:39:12.478 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:122 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:46404 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-03 20:39:12.479 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:46412 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:59744 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:44052 - "GET /health HTTP/1.1" 200 OK