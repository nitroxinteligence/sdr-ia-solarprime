2025-08-07 18:42:21.757 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 WEBHOOK: Usando conversation_id=09c7fc7e-a847-43c2-a06b-761a2acd493f para phone=558182986181
2025-08-07 18:42:21.758 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Chamando process_message com conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:42:21.982 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Novo estágio identificado: EM_QUALIFICACAO
2025-08-07 18:42:22.197 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Lead atualizado no Supabase: {'current_stage': 'EM_QUALIFICACAO', 'updated_at': '2025-08-07T18:42:21.982379'}
2025-08-07 18:42:22.198 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=558182986181
2025-08-07 18:42:22.198 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 18:42:22.435 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:42:22.435 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:42:22.653 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 18:42:22.653 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:42:22.654 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 5
2025-08-07 18:42:22.654 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 18:42:22.654 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T18:42:21.112049+00:00 - user
2025-08-07 18:42:22.654 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 18:42:22.654 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 5 mensagens disponíveis (menos que o limite de 100)
2025-08-07 18:42:22.655 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 HISTÓRICO: Buscando mensagens para identifier=09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:42:22.655 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:42:22.655 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:42:22.869 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 QUERY EXECUTADA:
2025-08-07 18:42:22.870 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Conversation ID: 09c7fc7e-a847-43c2-a06b-761a2acd493f
2025-08-07 18:42:22.870 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Mensagens encontradas: 5
2025-08-07 18:42:22.870 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Limite solicitado: 100
2025-08-07 18:42:22.871 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Primeira msg: 2025-08-07T18:42:21.112049+00:00 - user
2025-08-07 18:42:22.871 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Última msg: 2025-08-07T18:40:35.898117+00:00 - user
2025-08-07 18:42:22.871 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 5 mensagens disponíveis (menos que o limite de 100)
2025-08-07 18:42:22.871 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ HISTÓRICO FINAL: 5 mensagens carregadas
2025-08-07 18:42:22.871 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 18:42:22.872 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: EM_QUALIFICACAO
                    - Status: PENDING
                    
                    USER: oi
ASSISTANT: Oii! Boa tarde! Meu nome é Helen Vieira, sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?
USER: mateus
ASSISTANT: Então vamos lá, Mateus! Hoje na SolarPrime nós temos 4 soluções energét...
2025-08-07 18:42:22.872 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 1693 caracteres
2025-08-07 18:42:22.872 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ❌ Nenhum resultado multimodal incluído no prompt
2025-08-07 18:42:22.873 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Preparando para chamar agent.arun...
2025-08-07 18:42:22.873 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem instructions? True
2025-08-07 18:42:22.873 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem memory? True
2025-08-07 18:42:22.873 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem model? True
2025-08-07 18:42:22.873 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun com timeout de 30s...
2025-08-07 18:42:22.874 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:33556 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK
2025-08-07 18:42:22.958 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-07 18:42:22.959 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:33562 - "POST /webhook/whatsapp/chats-upsert HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-07 18:42:29.022 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ agent.arun completou com sucesso
2025-08-07 18:42:29.022 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Tipo do result: <class 'agno.run.response.RunResponse'>
2025-08-07 18:42:29.022 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result tem content? True
2025-08-07 18:42:29.022 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Atributos do result: ['content', 'content_type', 'thinking', 'reasoning_content', 'messages', 'metrics', 'model', 'model_provider', 'run_id', 'agent_id', 'agent_name', 'session_id', 'team_session_id', 'workflow_id', 'tools', 'formatted_tool_calls', 'images', 'videos', 'audio', 'response_audio', 'citations', 'extra_data', 'created_at', 'events', 'status']
2025-08-07 18:42:29.023 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Result não é None, tipo: RunResponse
2025-08-07 18:42:29.023 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 raw_response (primeiros 200 chars): VAZIO...
2025-08-07 18:42:29.023 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho raw_response: 0 caracteres
2025-08-07 18:42:29.024 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⚠️ raw_response está vazio ANTES da verificação!
2025-08-07 18:42:29.024 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⚠️ Agent retornou resposta vazia! Usando fallback...
2025-08-07 18:42:29.024 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Sem análise multimodal disponível
2025-08-07 18:42:29.273 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>Oi! Desculpe, tive um probleminha aqui. Pode repetir sua última mensagem?</RESPOSTA_...
2025-08-07 18:42:29.273 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=106, primeiros 200 chars: <RESPOSTA_FINAL>Oi! Desculpe, tive um probleminha aqui. Pode repetir sua última mensagem?</RESPOSTA_FINAL>
2025-08-07 18:42:29.273 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=106, primeiros 200 chars: <RESPOSTA_FINAL>Oi! Desculpe, tive um probleminha aqui. Pode repetir sua última mensagem?</RESPOSTA_FINAL>
2025-08-07 18:42:34.284 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.3, 'message_length': 73, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 18:42:39.752 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 73, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-07 18:42:39.753 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Oi! Desculpe, tive um probleminha aqui. Pode repet', 'recipient': '558182986181', 'type': 'text'}
2025-08-07 18:42:39.753 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB0EADD8C81E4C1ACF3454A18EDE891D8E75B82
2025-08-07 18:42:40.830 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-07 18:42:40.830 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:334 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:46100 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
INFO:     127.0.0.1:52726 - "GET /health HTTP/1.1" 200 OK