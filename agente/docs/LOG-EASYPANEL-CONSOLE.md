2025-08-01 20:03:25 | INFO     | agente.main:process_message_async:531 | ✅ Message processed successfully for 558182986181
2025-08-01 20:03:25 | DEBUG    | agente.services.supabase_service:save_message:493 | ✅ Mensagem salva: 42f1b1e7-086b-43b0-9488-424e711c8276
2025-08-01 20:03:28 | DEBUG    | agente.repositories.message_repository:_invalidate_cache:621 | Cache invalidado para conversa fecb7acc-5422-4d56-b204-9a029559b99f
2025-08-01 20:03:28 | INFO     | agente.repositories.message_repository:save_assistant_message:133 | Mensagem do assistente salva: 42f1b1e7-086b-43b0-9488-424e711c8276
2025-08-01 20:03:28 | INFO     | agente.main:process_message_async:546 | 💾 Resposta do agente salva: 42f1b1e7-086b-43b0-9488-424e711c8276 (conversa: fecb7acc-5422-4d56-b204-9a029559b99f)
2025-08-01 20:03:28 | INFO     | agente.core.auto_chunking:__init__:44 | AutoChunkingManager initialized
2025-08-01 20:03:28 | INFO     | agente.services.evolution_service:send_text_message:216 | Sending text message
2025-08-01 20:03:28 | INFO     | agente.core.logger:log_api_request:119 | API Request: POST evolution_api /message/sendText/SDR IA SolarPrime
INFO:     127.0.0.1:34784 - "GET /health HTTP/1.1" 200 OK
2025-08-01 20:03:37 | INFO     | agente.core.logger:log_api_response:130 | API Response: evolution_api /message/sendText/SDR IA SolarPrime - 201 (8.93s)
2025-08-01 20:03:37 | INFO     | agente.services.evolution_service:send_text_message:238 | Text message sent successfully
2025-08-01 20:03:37 | INFO     | agente.main:process_message_async:575 | 📤 Response sent to WhatsApp for 558182986181 (single message)
2025-08-01 20:03:38 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: messages.update
INFO:     10.11.0.4:59552 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-01 20:03:43 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: presence.update
2025-08-01 20:03:43 | DEBUG    | agente.main:whatsapp_webhook:361 | Presence update - User: 558182986181@s.whatsapp.net, Status: composing
INFO:     10.11.0.4:35742 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-01 20:03:44 | INFO     | agente.main:whatsapp_webhook:217 | Webhook received - Event: messages.upsert
INFO:     10.11.0.4:35742 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-08-01 20:03:44 | INFO     | agente.main:process_message_async:444 | Processing message from 558182986181: mateus...
2025-08-01 20:03:45 | INFO     | agente.services.supabase_service:get_or_create_lead:248 | Lead existente encontrado: 558182986181
2025-08-01 20:03:45 | INFO     | agente.repositories.conversation_repository:get_or_create_conversation:118 | Lead obtido/criado para: 558182986181 (ID: d247b88d-613f-4e7c-8bc5-1795c862704f)
2025-08-01 20:03:45 | INFO     | agente.main:process_message_async:490 | ✅ Conversa existente encontrada para 558182986181: fecb7acc-5422-4d56-b204-9a029559b99f
2025-08-01 20:03:46 | DEBUG    | agente.services.supabase_service:save_message:493 | ✅ Mensagem salva: 6a5026c9-6a20-4a32-bff7-4d015f201eb6
2025-08-01 20:03:48 | DEBUG    | agente.repositories.message_repository:_invalidate_cache:621 | Cache invalidado para conversa fecb7acc-5422-4d56-b204-9a029559b99f
2025-08-01 20:03:48 | INFO     | agente.repositories.message_repository:save_user_message:79 | Mensagem do usuário salva: 6a5026c9-6a20-4a32-bff7-4d015f201eb6
2025-08-01 20:03:48 | INFO     | agente.main:process_message_async:508 | 💾 Mensagem do usuário salva: 6a5026c9-6a20-4a32-bff7-4d015f201eb6 (conversa: fecb7acc-5422-4d56-b204-9a029559b99f)
2025-08-01 20:03:48 | DEBUG    | agente.core.reaction_manager:process_spontaneous_reaction:145 | Skipping spontaneous reaction based on probability
2025-08-01 20:03:48 | INFO     | agente.core.agent:process_message:335 | 📱 Processando mensagem de 558182986181: mateus...
2025-08-01 20:03:48 | DEBUG    | agente.core.session_manager:get_or_create_session:108 | Returning cached session for 558182986181
2025-08-01 20:03:48 | INFO     | agente.core.context_manager:build_enhanced_context:769 | Building enhanced context for 5581****
2025-08-01 20:03:49 | INFO     | agente.services.supabase_service:get_or_create_lead:248 | Lead existente encontrado: 558182986181
2025-08-01 20:03:49 | INFO     | agente.core.context_manager:build_conversation_context:587 | Lead auto-created in context manager for 558182986181
2025-08-01 20:03:50 | DEBUG    | agente.core.context_manager:track_qualification_progress:439 | Qualification progress for None: {'completed': 0, 'is_qualified': False, 'criteria': {'conta_acima_4000': False, 'e_decisor': False, 'tem_usina_propria': False, 'tem_contrato_vigente': False, 'demonstra_interesse': False}, 'missing': ['conta_acima_4000', 'e_decisor', 'tem_usina_propria', 'tem_contrato_vigente'], 'next_question': 'Qual o valor médio da sua conta de energia?', 'total_criteria': 5, 'completed_criteria': 0}
2025-08-01 20:03:50 | DEBUG    | agente.core.context_manager:extract_key_information:551 | Extracted information: {'nome': None, 'valor_conta': None, 'tipo_imovel': None, 'objecoes': [], 'tem_interesse_real': False, 'telefones_adicionais': [], 'emails': []}
2025-08-01 20:03:50 | INFO     | agente.core.context_manager:build_conversation_context:631 | Built context for 558182986181: stage=IDENTIFICATION, interest=5, progress=0%
2025-08-01 20:03:50 | INFO     | agente.repositories.knowledge_base_repository:search_knowledge:47 | Searching knowledge base for: mateus...
2025-08-01 20:03:50 | INFO     | agente.repositories.knowledge_base_repository:search_knowledge:77 | No knowledge found
2025-08-01 20:03:50 | INFO     | agente.repositories.knowledge_base_repository:get_recent_knowledge:170 | Getting recent knowledge
2025-08-01 20:03:51 | INFO     | agente.repositories.knowledge_base_repository:get_recent_knowledge:178 | Found 2 recent knowledge items
2025-08-01 20:03:51 | INFO     | agente.core.context_manager:build_enhanced_context:836 | Enhanced context built for 5581****: 0 msgs, 2 knowledge items
2025-08-01 20:03:51 | INFO     | agente.core.agent:process_message:414 | 🧠 Contexto enhanced para 5581****: 1 seções, 0 mensagens, 2 itens conhecimento
2025-08-01 20:03:51 | DEBUG    | agente.core.tool_context:set_current_context:34 | Contexto definido para tools: phone=5581****
2025-08-01 20:03:51 | DEBUG    | agente.core.agent:process_message:442 | Using AGnO agent.arun() with message: [CONTEXTO COMPLETO]
📚 Conhecimento SolarPrime:
⭐ Que vantagens a Solarprime oferece em relação aos c...
2025-08-01 20:03:54 | ERROR    | agente.tools.whatsapp.send_text_message:_send_text_message_async:54 | Phone não fornecido e não encontrado no contexto