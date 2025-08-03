✅ Usando variáveis de ambiente do servidor (EasyPanel)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-03 20:30:13.039 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-03 20:30:13.043 | WARNING  | app.integrations.redis_client:connect:35 | Redis não disponível: Error -2 connecting to redis:6379. -2.. Sistema funcionará sem cache.
2025-08-03 20:30:13.044 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-03 20:30:13.876 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-03 20:30:13.877 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Buffer inicializado (timeout=30.0s, max=10)
2025-08-03 20:30:13.877 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-03 20:30:13.877 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=250 chars, smart=ativada)
2025-08-03 20:30:13.877 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 250}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-03 20:30:13.894 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-03 20:30:13.895 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-03 20:30:13.895 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-03 20:30:13.895 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-03 20:30:13.895 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-03 20:30:13.896 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-03 20:30:13.896 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-03 20:30:13.896 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-03 20:30:13.897 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-03 20:30:13.897 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-03 20:30:14.199 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-03 20:30:14.199 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-03 20:30:14.200 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-03 20:30:14.200 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-03 20:30:14.200 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-03 20:30:14.200 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-03 20:30:14.201 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-03 20:30:15.005 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-03 20:30:15.006 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-03 20:30:15.006 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'members_count': 6}
2025-08-03 20:30:15.972 | INFO     | app.teams.agents.crm:initialize:159 | ✅ Campos e stages do Kommo carregados automaticamente
2025-08-03 20:30:15.973 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Kommo CRM pronto
2025-08-03 20:30:15.973 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:57336 - "GET /health HTTP/1.1" 200 OK
2025-08-03 20:30:20.757 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:45624 - "POST /webhook/whatsapp/presence-update HTTP/1.1" 200 OK
2025-08-03 20:30:20.887 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-03 20:30:20.887 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:113 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T17:30:20.869Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:45624 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-03 20:30:20.915 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-03 20:30:20.915 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:113 | Chat update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T17:30:20.909Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:45624 - "POST /webhook/whatsapp/chats-update HTTP/1.1" 200 OK
2025-08-03 20:30:20.948 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:45624 - "POST /webhook/whatsapp/messages-upsert HTTP/1.1" 200 OK
2025-08-03 20:30:20.949 | INFO     | app.utils.logger:log_with_emoji:140 | 📥 Recebido text de 558182986181 | Data: {'preview': 'OI', 'sender': '558182986181', 'type': 'text'}
2025-08-03 20:30:21.288 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-03 20:30:21.288 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:118 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHXbqRCwsprdQRhih51sfn6gTQPEfHG-k9yyq4EtEMH8Q&oe=689CD10D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T17:30:21.282Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:45624 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-03 20:30:21.338 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-03 20:30:21.339 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:118 | Contacts update recebido: {'event': 'contacts.update', 'instance': 'SDR IA SolarPrime', 'data': {'remoteJid': '558182986181@s.whatsapp.net', 'pushName': 'Mateus M', 'profilePicUrl': 'https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2AHXbqRCwsprdQRhih51sfn6gTQPEfHG-k9yyq4EtEMH8Q&oe=689CD10D&_nc_sid=5e03e0&_nc_cat=104', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/whatsapp', 'date_time': '2025-08-03T17:30:21.334Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:45624 - "POST /webhook/whatsapp/contacts-update HTTP/1.1" 200 OK
2025-08-03 20:30:22.788 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:45624 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-03 20:30:22.797 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-03 20:30:22.797 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:122 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:45624 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
2025-08-03 20:30:22.803 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:45624 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-03 20:30:22.808 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-03 20:30:22.808 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:122 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:45624 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
INFO:     127.0.0.1:50312 - "GET /health HTTP/1.1" 200 OK
2025-08-03 20:30:50.949 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processando 1 mensagens combinadas | Data: {'phone': '558182986181', 'total_chars': 2}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-03 20:30:53.583 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-03 20:30:53.583 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: agentic_sdr_sessions
2025-08-03 20:30:53.583 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelos configurados pronto | Data: {'primary_model': 'gemini-2.5-pro', 'reasoning_enabled': True}
2025-08-03 20:30:53.584 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-03 20:30:53.586 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base pronto | Data: {'status': 'ativo'}
2025-08-03 20:30:53.587 | INFO     | app.utils.logger:log_with_emoji:140 | 🤖 AGENTIC SDR: Sistema inicializado com sucesso | Data: {'context_enabled': True, 'reasoning_enabled': True, 'multimodal_enabled': True}
2025-08-03 20:30:53.587 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Carregando knowledge base do Supabase...
2025-08-03 20:30:54.031 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Knowledge base carregada do Supabase pronto | Data: {'documents_loaded': 0, 'total_documents': 67}
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
2025-08-03 20:30:54.034 | WARNING  | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...
2025-08-03 20:30:54.034 | WARNING  | app.utils.optional_storage:__init__:48 | 📝 Sistema funcionará com storage em memória para: sdr_team_sessions
2025-08-03 20:30:54.035 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-03 20:30:54.035 | WARNING  | app.teams.sdr_team:__init__:90 | Memory sem persistência: 1 validation error for AgentMemory
db
  Input shou...
2025-08-03 20:30:54.035 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-03 20:30:54.035 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-03 20:30:54.035 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-03 20:30:54.036 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-03 20:30:54.036 | INFO     | app.teams.agents.followup:__init__:149 | ✅ FollowUpAgent inicializado
2025-08-03 20:30:54.036 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-03 20:30:54.038 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-03 20:30:54.039 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-03 20:30:54.039 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-03 20:30:54.039 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-03 20:30:54.039 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-03 20:30:54.040 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-03 20:30:54.040 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-03 20:30:54.462 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-03 20:30:54.463 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-03 20:30:54.463 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-03 20:30:54.463 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-03 20:30:56.611 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-03 20:30:59.949 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
WARNING  MemoryDb not provided.                                                 
2025-08-03 20:31:14.377 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Oii! Seja muito bem-vindo à Solar Prime!

Meu nome é Helen Vieira.

Sou consultora especialista aqui...
INFO:     127.0.0.1:57274 - "GET /health HTTP/1.1" 200 OK
2025-08-03 20:31:21.666 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 171, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-03 20:31:21.666 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Oii! Seja muito bem-vindo à Solar Prime!\n\nMeu nome', 'recipient': '558182986181', 'type': 'text'}
2025-08-03 20:31:21.666 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB05A930B3BDDECAE6BF7B4DDCD879D9855F9CA
2025-08-03 20:31:23.145 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-03 20:31:23.145 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:122 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:35908 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-03 20:31:23.146 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:47918 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK