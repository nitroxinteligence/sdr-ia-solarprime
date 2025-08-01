INFO:     Started server process [7]
INFO:     Waiting for application startup.
2025-08-01 20:11:20 | INFO     | agente.main:lifespan:45 | 🚀 Starting modular SDR Agent...
2025-08-01 20:11:20 | WARNING  | agente.core.monitoring:setup_sentry:32 | Sentry DSN not configured, error tracking disabled
2025-08-01 20:11:20 | INFO     | agente.core.humanizer:__init__:82 | HelenHumanizer initialized with typing speed 50wpm and 3.0% error rate
2025-08-01 20:11:20 | INFO     | agente.services.supabase_service:__init__:143 | ✅ Supabase Service inicializado com sucesso
2025-08-01 20:11:20 | INFO     | agente.repositories.conversation_repository:__init__:41 | ConversationRepository inicializado
2025-08-01 20:11:20 | INFO     | agente.repositories.lead_repository:__init__:29 | LeadRepository inicializado
2025-08-01 20:11:20 | INFO     | agente.core.context_manager:__init__:95 | ContextManager initialized
2025-08-01 20:11:20 | INFO     | agente.repositories.lead_repository:__init__:29 | LeadRepository inicializado
2025-08-01 20:11:20 | INFO     | agente.core.qualification_flow:__init__:86 | QualificationFlow initialized
2025-08-01 20:11:20 | INFO     | agente.services.evolution_service:__init__:52 | Evolution API Service initialized
2025-08-01 20:11:20 | INFO     | agente.repositories.lead_repository:__init__:29 | LeadRepository inicializado
2025-08-01 20:11:20 | INFO     | agente.core.message_processor:__init__:137 | MessageProcessor initialized
2025-08-01 20:11:20 | INFO     | agente.repositories.conversation_repository:__init__:41 | ConversationRepository inicializado
2025-08-01 20:11:20 | INFO     | agente.repositories.lead_repository:__init__:29 | LeadRepository inicializado
2025-08-01 20:11:20 | INFO     | agente.services.evolution_service:__init__:52 | Evolution API Service initialized
2025-08-01 20:11:20 | INFO     | agente.repositories.followup_repository:__init__:39 | FollowUpRepository iniciado
2025-08-01 20:11:20 | INFO     | agente.core.session_manager:__init__:73 | SessionManager initialized
2025-08-01 20:11:20 | INFO     | agente.core.agent:_load_system_prompt:124 | 🚀 Carregando PROMPT MASTER COMPLETO - Helen Vieira Ultra-Humanizada
2025-08-01 20:11:20 | DEBUG    | agente.core.agent:_initialize_agent:225 | Initializing AGnO Agent with model: gemini-2.5-pro
2025-08-01 20:11:20 | DEBUG    | agente.core.agent:_initialize_agent:226 | Instructions length: 35028 chars
2025-08-01 20:11:20 | INFO     | agente.core.agent:_initialize_agent:302 | ✅ Agente Helen Vieira - SDR SolarPrime inicializado com sucesso
2025-08-01 20:11:20 | INFO     | agente.core.agent:_initialize_agent:303 |    - Modelo: gemini-2.5-pro (Gemini 2.5 Pro - Advanced Reasoning)
2025-08-01 20:11:20 | INFO     | agente.core.agent:_initialize_agent:304 |    - Tools: 31
2025-08-01 20:11:20 | INFO     | agente.core.agent:_initialize_agent:305 |    - Thinking Budget: 128 (reasoning avançado habilitado)
2025-08-01 20:11:20 | INFO     | agente.core.agent:_initialize_agent:306 |    - Temperature: 0.7
2025-08-01 20:11:20 | INFO     | agente.core.agent:_initialize_agent:307 |    - Max Tokens: 4096
2025-08-01 20:11:20 | INFO     | agente.core.agent:_initialize_agent:308 |    - Reasoning: False
2025-08-01 20:11:20 | INFO     | agente.core.agent:_initialize_agent:309 |    - Debug: False
2025-08-01 20:11:20 | INFO     | agente.core.agent:start:728 | 🚀 Iniciando agente Helen Vieira - SDR SolarPrime
2025-08-01 20:11:20 | INFO     | agente.core.session_manager:start:78 | SessionManager started with cleanup task
2025-08-01 20:11:20 | INFO     | agente.main:lifespan:62 | ✅ SDR Agent started successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:36678 - "GET /health HTTP/1.1" 200 OK
2025-08-01 20:11:27 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: presence.update
2025-08-01 20:11:27 | DEBUG    | agente.main:whatsapp_webhook:361 | Presence update - User: 558182986181@s.whatsapp.net, Status: composing
INFO:     10.11.0.4:58778 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-01 20:11:28 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: messages.upsert
INFO:     10.11.0.4:58778 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-01 20:11:28 | INFO     | agente.main:process_message_async:444 | Processing message from 558182986181: oi...
2025-08-01 20:11:28 | INFO     | agente.repositories.conversation_repository:__init__:41 | ConversationRepository inicializado
2025-08-01 20:11:29 | INFO     | agente.services.supabase_service:get_or_create_lead:248 | Lead existente encontrado: 558182986181
2025-08-01 20:11:29 | INFO     | agente.repositories.conversation_repository:get_or_create_conversation:118 | Lead obtido/criado para: 558182986181 (ID: d247b88d-613f-4e7c-8bc5-1795c862704f)
2025-08-01 20:11:29 | INFO     | agente.main:process_message_async:490 | ✅ Conversa existente encontrada para 558182986181: fecb7acc-5422-4d56-b204-9a029559b99f
2025-08-01 20:11:30 | DEBUG    | agente.services.supabase_service:save_message:493 | ✅ Mensagem salva: e0378273-4a04-4af5-9897-7ff0e84a2b0e
2025-08-01 20:11:31 | DEBUG    | agente.repositories.message_repository:_invalidate_cache:621 | Cache invalidado para conversa fecb7acc-5422-4d56-b204-9a029559b99f
2025-08-01 20:11:31 | INFO     | agente.repositories.message_repository:save_user_message:79 | Mensagem do usuário salva: e0378273-4a04-4af5-9897-7ff0e84a2b0e
2025-08-01 20:11:31 | INFO     | agente.main:process_message_async:508 | 💾 Mensagem do usuário salva: e0378273-4a04-4af5-9897-7ff0e84a2b0e (conversa: fecb7acc-5422-4d56-b204-9a029559b99f)
2025-08-01 20:11:31 | INFO     | agente.core.reaction_manager:__init__:64 | ReactionManager initialized
2025-08-01 20:11:31 | DEBUG    | agente.core.reaction_manager:process_spontaneous_reaction:145 | Skipping spontaneous reaction based on probability
2025-08-01 20:11:31 | INFO     | agente.core.agent:process_message:335 | 📱 Processando mensagem de 558182986181: oi...
2025-08-01 20:11:32 | INFO     | agente.services.supabase_service:get_or_create_lead:248 | Lead existente encontrado: 558182986181
2025-08-01 20:11:32 | INFO     | agente.repositories.conversation_repository:get_or_create_conversation:118 | Lead obtido/criado para: 558182986181 (ID: d247b88d-613f-4e7c-8bc5-1795c862704f)
2025-08-01 20:11:32 | INFO     | agente.repositories.conversation_repository:get_or_create_conversation:154 | Atualizando session_id da conversa fecb7acc-5422-4d56-b204-9a029559b99f
2025-08-01 20:11:33 | INFO     | agente.services.supabase_service:get_or_create_lead:248 | Lead existente encontrado: 558182986181
2025-08-01 20:11:33 | INFO     | agente.repositories.conversation_repository:get_or_create_conversation:118 | Lead obtido/criado para: 558182986181 (ID: d247b88d-613f-4e7c-8bc5-1795c862704f)
2025-08-01 20:11:33 | INFO     | agente.repositories.conversation_repository:get_or_create_conversation:154 | Atualizando session_id da conversa fecb7acc-5422-4d56-b204-9a029559b99f
2025-08-01 20:11:33 | INFO     | agente.core.session_manager:_create_new_session:371 | Created new session for 558182986181
2025-08-01 20:11:33 | INFO     | agente.core.session_manager:get_or_create_session:131 | Session for 558182986181: id=fecb7acc-5422-4d56-b204-9a029559b99f, state=active, message_count=0
2025-08-01 20:11:33 | INFO     | agente.core.context_manager:build_enhanced_context:769 | Building enhanced context for 5581****
2025-08-01 20:11:33 | INFO     | agente.services.supabase_service:get_or_create_lead:248 | Lead existente encontrado: 558182986181
2025-08-01 20:11:33 | INFO     | agente.core.context_manager:build_conversation_context:587 | Lead auto-created in context manager for 558182986181
2025-08-01 20:11:34 | DEBUG    | agente.core.context_manager:track_qualification_progress:439 | Qualification progress for None: {'completed': 0, 'is_qualified': False, 'criteria': {'conta_acima_4000': False, 'e_decisor': False, 'tem_usina_propria': False, 'tem_contrato_vigente': False, 'demonstra_interesse': False}, 'missing': ['conta_acima_4000', 'e_decisor', 'tem_usina_propria', 'tem_contrato_vigente'], 'next_question': 'Qual o valor médio da sua conta de energia?', 'total_criteria': 5, 'completed_criteria': 0}
2025-08-01 20:11:34 | DEBUG    | agente.core.context_manager:extract_key_information:551 | Extracted information: {'nome': None, 'valor_conta': None, 'tipo_imovel': None, 'objecoes': [], 'tem_interesse_real': False, 'telefones_adicionais': [], 'emails': []}
2025-08-01 20:11:34 | INFO     | agente.core.context_manager:build_conversation_context:631 | Built context for 558182986181: stage=IDENTIFICATION, interest=5, progress=0%
2025-08-01 20:11:34 | INFO     | agente.repositories.knowledge_base_repository:get_knowledge_base_repository:247 | KnowledgeBaseRepository singleton created
2025-08-01 20:11:34 | INFO     | agente.repositories.knowledge_base_repository:search_knowledge:47 | Searching knowledge base for: oi...
2025-08-01 20:11:34 | INFO     | agente.repositories.knowledge_base_repository:search_knowledge:74 | Found 3 knowledge items
2025-08-01 20:11:34 | INFO     | agente.repositories.knowledge_base_repository:get_recent_knowledge:170 | Getting recent knowledge
2025-08-01 20:11:34 | INFO     | agente.repositories.knowledge_base_repository:get_recent_knowledge:178 | Found 2 recent knowledge items
2025-08-01 20:11:34 | INFO     | agente.core.context_manager:build_enhanced_context:836 | Enhanced context built for 5581****: 0 msgs, 5 knowledge items
2025-08-01 20:11:34 | INFO     | agente.core.agent:process_message:414 | 🧠 Contexto enhanced para 5581****: 1 seções, 0 mensagens, 5 itens conhecimento
2025-08-01 20:11:34 | DEBUG    | agente.core.tool_context:set_current_context:37 | Contexto definido para tools: phone=5581****
2025-08-01 20:11:34 | DEBUG    | agente.core.agent:process_message:442 | Using AGnO agent.arun() with message: [CONTEXTO COMPLETO]
📚 Conhecimento SolarPrime:
📚 Como funciona a proteção contra as bandeiras tarifá...
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
ERROR    Function send_greetings not found                                      
2025-08-01 20:11:39 | DEBUG    | agente.tools.whatsapp.send_text_message:_send_text_message_async:62 | Phone obtido do contexto: 5581****
2025-08-01 20:11:39 | DEBUG    | agente.tools.whatsapp.send_text_message:_send_text_message_async:62 | Phone obtido do contexto: 5581****
2025-08-01 20:11:39 | INFO     | agente.tools.whatsapp.send_text_message:_send_text_message_async:65 | Enviando mensagem de texto via WhatsApp
2025-08-01 20:11:39 | DEBUG    | agente.tools.whatsapp.send_text_message:_send_text_message_async:62 | Phone obtido do contexto: 5581****
2025-08-01 20:11:39 | INFO     | agente.tools.whatsapp.send_text_message:_send_text_message_async:65 | Enviando mensagem de texto via WhatsApp
2025-08-01 20:11:39 | INFO     | agente.services.evolution_service:send_text_message:216 | Sending text message
2025-08-01 20:11:39 | INFO     | agente.tools.whatsapp.send_text_message:_send_text_message_async:65 | Enviando mensagem de texto via WhatsApp
2025-08-01 20:11:39 | INFO     | agente.services.evolution_service:send_text_message:216 | Sending text message
2025-08-01 20:11:39 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-01 20:11:39 | INFO     | agente.services.evolution_service:send_text_message:216 | Sending text message
2025-08-01 20:11:39 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-01 20:11:39 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-01 20:11:40 | INFO     | agente.core.logger:log_api_response:130 | API Response: evolution_api /message/sendText/SDR IA SolarPrime - 201 (1.70s)
2025-08-01 20:11:40 | INFO     | agente.services.evolution_service:send_text_message:238 | Text message sent successfully
2025-08-01 20:11:40 | SUCCESS  | agente.tools.whatsapp.send_text_message:_send_text_message_async:89 | Mensagem de texto enviada com sucesso
2025-08-01 20:11:41 | ERROR    | agente.services.evolution_service:_make_request:172 | Evolution API unexpected error
2025-08-01 20:11:41 | INFO     | agente.services.evolution_service:_make_request:183 | Retrying in 1.5 seconds...
2025-08-01 20:11:41 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: messages.update
INFO:     10.11.0.4:56018 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-01 20:11:42 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: messages.update
INFO:     10.11.0.4:56018 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-01 20:11:42 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-01 20:11:44 | INFO     | agente.core.logger:log_api_response:130 | API Response: evolution_api /message/sendText/SDR IA SolarPrime - 201 (5.73s)
2025-08-01 20:11:44 | INFO     | agente.services.evolution_service:send_text_message:238 | Text message sent successfully
2025-08-01 20:11:44 | SUCCESS  | agente.tools.whatsapp.send_text_message:_send_text_message_async:89 | Mensagem de texto enviada com sucesso
2025-08-01 20:11:45 | ERROR    | agente.services.evolution_service:_make_request:172 | Evolution API unexpected error
2025-08-01 20:11:45 | INFO     | agente.services.evolution_service:_make_request:183 | Retrying in 2.8 seconds...
2025-08-01 20:11:45 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: messages.update
INFO:     10.11.0.4:56018 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-01 20:11:45 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: messages.update
INFO:     10.11.0.4:56018 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-01 20:11:48 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-01 20:11:50 | INFO     | agente.core.logger:log_api_response:130 | API Response: evolution_api /message/sendText/SDR IA SolarPrime - 201 (2.42s)
2025-08-01 20:11:50 | INFO     | agente.services.evolution_service:send_text_message:238 | Text message sent successfully
2025-08-01 20:11:50 | SUCCESS  | agente.tools.whatsapp.send_text_message:_send_text_message_async:89 | Mensagem de texto enviada com sucesso
2025-08-01 20:11:51 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: messages.update
INFO:     10.11.0.4:59880 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     127.0.0.1:60804 - "GET /health HTTP/1.1" 200 OK
2025-08-01 20:11:56 | DEBUG    | agente.tools.whatsapp.send_text_message:_send_text_message_async:62 | Phone obtido do contexto: 5581****
2025-08-01 20:11:56 | INFO     | agente.tools.whatsapp.send_text_message:_send_text_message_async:65 | Enviando mensagem de texto via WhatsApp
2025-08-01 20:11:56 | INFO     | agente.services.evolution_service:send_text_message:216 | Sending text message
2025-08-01 20:11:56 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-01 20:11:56 | ERROR    | agente.services.evolution_service:_make_request:172 | Evolution API unexpected error
2025-08-01 20:11:56 | INFO     | agente.services.evolution_service:_make_request:183 | Retrying in 1.8 seconds...
2025-08-01 20:11:58 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-01 20:12:00 | INFO     | agente.core.logger:log_api_response:130 | API Response: evolution_api /message/sendText/SDR IA SolarPrime - 201 (1.71s)
2025-08-01 20:12:00 | INFO     | agente.services.evolution_service:send_text_message:238 | Text message sent successfully
2025-08-01 20:12:00 | SUCCESS  | agente.tools.whatsapp.send_text_message:_send_text_message_async:89 | Mensagem de texto enviada com sucesso
2025-08-01 20:12:01 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: messages.update
INFO:     10.11.0.4:59984 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-01 20:12:05 | DEBUG    | agente.tools.whatsapp.send_text_message:_send_text_message_async:62 | Phone obtido do contexto: 5581****
2025-08-01 20:12:05 | INFO     | agente.tools.whatsapp.send_text_message:_send_text_message_async:65 | Enviando mensagem de texto via WhatsApp
2025-08-01 20:12:05 | INFO     | agente.services.evolution_service:send_text_message:216 | Sending text message
2025-08-01 20:12:05 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-01 20:12:05 | ERROR    | agente.services.evolution_service:_make_request:172 | Evolution API unexpected error
2025-08-01 20:12:05 | INFO     | agente.services.evolution_service:_make_request:183 | Retrying in 1.1 seconds...
2025-08-01 20:12:06 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-01 20:12:08 | INFO     | agente.core.logger:log_api_response:130 | API Response: evolution_api /message/sendText/SDR IA SolarPrime - 201 (1.88s)
2025-08-01 20:12:08 | INFO     | agente.services.evolution_service:send_text_message:238 | Text message sent successfully
2025-08-01 20:12:08 | SUCCESS  | agente.tools.whatsapp.send_text_message:_send_text_message_async:89 | Mensagem de texto enviada com sucesso
2025-08-01 20:12:09 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: messages.update
INFO:     10.11.0.4:47220 - "POST /webhook/whatsapp HTTP/1.1" 200 OK