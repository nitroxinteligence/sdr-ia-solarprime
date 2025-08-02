2025-08-02 17:19:27 | INFO     | agente.core.context_manager:build_enhanced_context:840 | Enhanced context built for 5581****: 0 msgs, 5 knowledge items
2025-08-02 17:19:27 | INFO     | agente.core.agent:process_message:422 | 🧠 Contexto enhanced para 5581****: 1 seções, 0 mensagens, 5 itens conhecimento
2025-08-02 17:19:27 | DEBUG    | agente.core.tool_context:set_current_context:37 | Contexto definido para tools: phone=5581****
2025-08-02 17:19:27 | DEBUG    | agente.core.agent:process_message:450 | Using AGnO agent.arun() with message: [CONTEXTO COMPLETO]
📚 Conhecimento SolarPrime:
📚 Como funciona a proteção contra as bandeiras tarifá...
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
2025-08-02 17:19:32 | INFO     | agente.tools.whatsapp.send_greetings:_send_greetings_async:75 | Enviando cumprimento personalizado
2025-08-02 17:19:32 | INFO     | agente.tools.whatsapp.type_simulation:_simulate_typing_async:77 | Iniciando simulação de digitação
2025-08-02 17:19:32 | INFO     | agente.tools.whatsapp.send_text_message:_send_text_message_async:79 | Enviando mensagem de texto via WhatsApp [SEQUENCIAL]
2025-08-02 17:19:32 | DEBUG    | agente.tools.whatsapp.type_simulation:_simulate_typing_async:96 | Tempo de digitação calculado
2025-08-02 17:19:32 | INFO     | agente.tools.whatsapp.type_simulation:_simulate_typing_async:77 | Iniciando simulação de digitação
2025-08-02 17:19:32 | INFO     | agente.services.evolution_service:send_text_message:264 | Sending text message
2025-08-02 17:19:32 | DEBUG    | agente.tools.whatsapp.type_simulation:_simulate_typing_async:96 | Tempo de digitação calculado
2025-08-02 17:19:32 | DEBUG    | agente.services.evolution_service:_ensure_client:111 | Created new HTTP client for Evolution API
2025-08-02 17:19:32 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-02 17:19:32 | INFO     | agente.core.logger:log_api_response:130 | API Response: evolution_api /message/sendText/SDR IA SolarPrime - 400 (0.42s)
2025-08-02 17:19:32 | WARNING  | agente.services.evolution_service:_make_request:179 | Evolution API returned non-2xx status
2025-08-02 17:19:32 | ERROR    | agente.services.evolution_service:send_text_message:292 | Failed to send text message
2025-08-02 17:19:32 | ERROR    | agente.tools.whatsapp.send_text_message:_send_text_message_async:117 | Falha ao enviar mensagem de texto [SEQUENCIAL]
2025-08-02 17:19:33 | DEBUG    | agente.tools.whatsapp.type_simulation:_simulate_typing_async:118 | Simulação de digitação: 25% completa
2025-08-02 17:19:33 | DEBUG    | agente.tools.whatsapp.type_simulation:_simulate_typing_async:118 | Simulação de digitação: 25% completa
2025-08-02 17:19:34 | DEBUG    | agente.tools.whatsapp.type_simulation:_simulate_typing_async:118 | Simulação de digitação: 50% completa
2025-08-02 17:19:35 | DEBUG    | agente.tools.whatsapp.type_simulation:_simulate_typing_async:118 | Simulação de digitação: 75% completa
2025-08-02 17:19:35 | DEBUG    | agente.tools.whatsapp.type_simulation:_simulate_typing_async:118 | Simulação de digitação: 50% completa
2025-08-02 17:19:36 | INFO     | agente.tools.whatsapp.type_simulation:_simulate_typing_async:123 | Simulação de digitação concluída
2025-08-02 17:19:36 | INFO     | agente.tools.whatsapp.type_simulation:_simulate_typing_async:141 | Enviando mensagem após simulação de digitação
2025-08-02 17:19:36 | INFO     | agente.services.evolution_service:send_text_message:264 | Sending text message
2025-08-02 17:19:36 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-02 17:19:36 | WARNING  | agente.services.evolution_service:_make_request:207 | TCP connection closed, will recreate client: unable to perform operation on <TCPTransport closed=True reading=False 0x74de0c1fd8c0>; the handler is closed
2025-08-02 17:19:36 | INFO     | agente.services.evolution_service:_make_request:231 | Retrying in 1.1 seconds...
2025-08-02 17:19:36 | DEBUG    | agente.tools.whatsapp.type_simulation:_simulate_typing_async:118 | Simulação de digitação: 75% completa
2025-08-02 17:19:37 | DEBUG    | agente.services.evolution_service:_ensure_client:111 | Created new HTTP client for Evolution API
2025-08-02 17:19:37 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-02 17:19:38 | INFO     | agente.core.logger:log_api_response:130 | API Response: evolution_api /message/sendText/SDR IA SolarPrime - 201 (0.69s)
2025-08-02 17:19:38 | INFO     | agente.services.evolution_service:send_text_message:286 | Text message sent successfully
2025-08-02 17:19:38 | SUCCESS  | agente.tools.whatsapp.type_simulation:_simulate_typing_async:154 | Mensagem enviada após simulação
2025-08-02 17:19:38 | INFO     | agente.main:whatsapp_webhook:260 | Webhook received - Event: send.message
2025-08-02 17:19:38 | DEBUG    | agente.main:whatsapp_webhook:440 | Unknown webhook event: send.message
INFO:     10.11.0.4:49636 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-02 17:19:38 | INFO     | agente.tools.whatsapp.type_simulation:_simulate_typing_async:123 | Simulação de digitação concluída
2025-08-02 17:19:38 | INFO     | agente.tools.whatsapp.type_simulation:_simulate_typing_async:141 | Enviando mensagem após simulação de digitação
2025-08-02 17:19:38 | INFO     | agente.services.evolution_service:send_text_message:264 | Sending text message
2025-08-02 17:19:38 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-02 17:19:38 | WARNING  | agente.services.evolution_service:_make_request:207 | TCP connection closed, will recreate client: unable to perform operation on <TCPTransport closed=True reading=False 0x74de000ccd90>; the handler is closed
2025-08-02 17:19:38 | INFO     | agente.services.evolution_service:_make_request:231 | Retrying in 1.5 seconds...
2025-08-02 17:19:39 | INFO     | agente.main:whatsapp_webhook:260 | Webhook received - Event: messages.update
INFO:     10.11.0.4:49636 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-02 17:19:39 | DEBUG    | agente.services.evolution_service:_ensure_client:111 | Created new HTTP client for Evolution API
2025-08-02 17:19:39 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-02 17:19:40 | INFO     | agente.core.logger:log_api_response:130 | API Response: evolution_api /message/sendText/SDR IA SolarPrime - 201 (0.69s)
2025-08-02 17:19:40 | INFO     | agente.services.evolution_service:send_text_message:286 | Text message sent successfully
2025-08-02 17:19:40 | SUCCESS  | agente.tools.whatsapp.type_simulation:_simulate_typing_async:154 | Mensagem enviada após simulação
2025-08-02 17:19:40 | INFO     | agente.main:whatsapp_webhook:260 | Webhook received - Event: send.message
2025-08-02 17:19:40 | DEBUG    | agente.main:whatsapp_webhook:440 | Unknown webhook event: send.message
INFO:     10.11.0.4:49636 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-02 17:19:41 | INFO     | agente.main:whatsapp_webhook:260 | Webhook received - Event: messages.update
INFO:     10.11.0.4:49636 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     127.0.0.1:33358 - "GET /health HTTP/1.1" 200 OK
/home/app/.local/lib/python3.11/site-packages/agno/agent/agent.py:1213: RuntimeWarning: coroutine 'buffer_message' was never awaited
  model_response: ModelResponse = await self.model.aresponse(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2025-08-02 17:19:47 | DEBUG    | agente.core.agent:process_message:456 | AGnO Agent response type: <class 'agno.run.response.RunResponse'>
2025-08-02 17:19:47 | DEBUG    | agente.core.agent:process_message:458 | AGnO Agent response attributes: ['content', 'content_type', 'thinking', 'reasoning_content', 'messages', 'metrics', 'model', 'model_provider', 'run_id', 'agent_id', 'agent_name', 'session_id', 'team_session_id', 'workflow_id', 'tools', 'formatted_tool_calls', 'images', 'videos', 'audio', 'response_audio', 'citations', 'extra_data', 'created_at', 'events', 'status']
2025-08-02 17:19:47 | DEBUG    | agente.core.session_manager:get_or_create_session:109 | Returning cached session for 558182986181
2025-08-02 17:19:48 | DEBUG    | agente.repositories.conversation_repository:update_last_message_at:637 | Updated conversation timestamp for fecb7acc-5422-4d56-b204-9a029559b99f
2025-08-02 17:19:48 | DEBUG    | agente.core.session_manager:update_session:185...
2025-08-02 17:19:48 | INFO     | agente.main:process_message_async:592 | ✅ Message processed successfully for 558182986181
2025-08-02 17:19:48 | DEBUG    | agente.services.supabase_service:save_message:507 | ✅ Mensagem salva: 8c14bc5c-3665-4c7c-9dee-7801342e3dfe
2025-08-02 17:19:49 | DEBUG    | agente.repositories.message_repository:_invalidate_cache:621 | Cache invalidado para conversa fecb7acc-5422-4d56-b204-9a029559b99f
2025-08-02 17:19:49 | INFO     | agente.repositories.message_repository:save_assistant_message:133 | Mensagem do assistente salva: 8c14bc5c-3665-4c7c-9dee-7801342e3dfe
2025-08-02 17:19:49 | INFO     | agente.main:process_message_async:607 | 💾 Resposta do agente salva: 8c14bc5c-3665-4c7c-9dee-7801342e3dfe (conversa: fecb7acc-5422-4d56-b204-9a029559b99f)
2025-08-02 17:19:49 | INFO     | agente.core.response_sanitizer:__init__:92 | ResponseSanitizer inicializado com 25 padrões de vazamento
2025-08-02 17:19:49 | INFO     | agente.core.response_sanitizer:sanitize_response:142 | ResponseSanitizer: Vazamentos removidos
2025-08-02 17:19:49 | INFO     | agente.main:process_message_async:624 | 🧼 ResponseSanitizer aplicado - vazamentos removidos
2025-08-02 17:19:49 | INFO     | agente.core.auto_chunking:__init__:71 | AutoChunkingManager initialized with intelligent humanization detection
2025-08-02 17:19:49 | INFO     | agente.core.auto_chunking:is_already_humanized:100 | Mensagem já humanizada detectada - BYPASS auto-chunking
2025-08-02 17:19:49 | INFO     | agente.core.auto_chunking:process_and_send_chunks:197 | 🎭 BYPASS: Mensagem já humanizada detectada - usando chunks pré-processados
2025-08-02 17:19:49 | INFO     | agente.core.auto_chunking:extract_humanized_chunks:158 | Chunks extraídos de mensagem humanizada
2025-08-02 17:19:49 | INFO     | agente.services.evolution_service:send_text_message:264 | Sending text message
2025-08-02 17:19:49 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-02 17:19:49 | WARNING  | agente.services.evolution_service:_make_request:207 | TCP connection closed, will recreate client: unable to perform operation on <TCPTransport closed=True reading=False 0x74de080ccd50>; the handler is closed
2025-08-02 17:19:49 | INFO     | agente.services.evolution_service:_make_request:231 | Retrying in 1.3 seconds...
2025-08-02 17:19:51 | DEBUG    | agente.services.evolution_service:_ensure_client:111 | Created new HTTP client for Evolution API
2025-08-02 17:19:51 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
2025-08-02 17:19:58 | INFO     | agente.core.logger:log_api_response:130 | API Response: evolution_api /message/sendText/SDR IA SolarPrime - 201 (7.70s)