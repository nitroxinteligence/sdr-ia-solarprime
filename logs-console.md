2025-08-04 13:44:11.051 | INFO     | app.teams.agents.qualification:__init__:123 | ✅ QualificationAgent inicializado
2025-08-04 13:44:11.051 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ QualificationAgent ✅ Habilitado
2025-08-04 13:44:11.051 | INFO     | app.teams.sdr_team:_initialize_agents:151 | 📅 Verificando CalendarAgent - enable_calendar_agent: True, enable_calendar_integration: True
2025-08-04 13:44:11.051 | INFO     | app.teams.sdr_team:_initialize_agents:154 | 📅 ATIVANDO CalendarAgent...
2025-08-04 13:44:11.051 | INFO     | app.teams.agents.calendar:__init__:106 | ✅ CalendarAgent inicializado
2025-08-04 13:44:11.052 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CalendarAgent ✅ Habilitado
2025-08-04 13:44:11.052 | INFO     | app.teams.sdr_team:_initialize_agents:162 | ✅ CalendarAgent ATIVADO com sucesso!
2025-08-04 13:44:11.052 | INFO     | app.teams.agents.followup:__init__:131 | ✅ FollowUpAgent inicializado
2025-08-04 13:44:11.052 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ FollowUpAgent ✅ Habilitado
✅ PostgreSQL URL configurada: ...@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
INFO Embedder not provided, using OpenAIEmbedder as default.                    
2025-08-04 13:44:11.054 | INFO     | app.teams.agents.knowledge:__init__:134 | ✅ KnowledgeAgent inicializado
2025-08-04 13:44:11.054 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ KnowledgeAgent ✅ Habilitado
2025-08-04 13:44:11.055 | INFO     | app.teams.agents.crm:__init__:144 | ✅ CRMAgent inicializado
2025-08-04 13:44:11.055 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ CRMAgent ✅ Habilitado
2025-08-04 13:44:11.055 | INFO     | app.teams.agents.bill_analyzer:__init__:148 | ✅ BillAnalyzerAgent inicializado
2025-08-04 13:44:11.055 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ BillAnalyzerAgent ✅ Habilitado
2025-08-04 13:44:11.056 | INFO     | app.utils.logger:log_with_emoji:140 | 👥 TEAM SDR: Sistema inicializado
2025-08-04 13:44:11.830 | INFO     | app.teams.agents.knowledge:load_knowledge_base:193 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 13:44:11.831 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 13:44:11.831 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-04 13:44:11.831 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-04 13:44:15.484 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 13:44:16.093 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 13:44:16.094 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 13:44:17.252 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 17 mensagens encontradas
2025-08-04 13:44:17.254 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 13:44:17.254 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 13:44:18.026 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 17 mensagens encontradas
2025-08-04 13:44:18.026 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 17 mensagens
2025-08-04 13:44:18.027 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:771 | 📅 CALENDÁRIO DETECTADO - Score: 0.8
2025-08-04 13:44:18.027 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:772 | 📅 Mensagem: oi, eu quero agendar uma reuniao imediatamente para as 14h...
2025-08-04 13:44:18.027 | INFO     | app.agents.agentic_sdr:should_call_sdr_team:773 | 📅 Agent recomendado: CalendarAgent
2025-08-04 13:44:18.027 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: Chamar SDR Team - CalendarAgent | Data: {'recommended_agent': 'CalendarAgent', 'decision_score': 0.8}
2025-08-04 13:44:18.027 | INFO     | app.teams.sdr_team:process_message_with_context:569 | 📅 AGENT RECOMENDADO: CalendarAgent
2025-08-04 13:44:18.027 | INFO     | app.teams.sdr_team:process_message_with_context:570 | 📅 Razão: Score de complexidade: 0.80. 🗓️ Solicitação de agendamento detectada - Ativando CalendarAgent
2025-08-04 13:44:18.028 | INFO     | app.teams.sdr_team:process_message_with_context:574 | 🗓️ ATIVANDO CalendarAgent para processar solicitação de agendamento!
2025-08-04 13:44:18.028 | INFO     | app.teams.sdr_team:process_message_with_context:576 | ✅ CalendarAgent está disponível e será usado
2025-08-04 13:44:21.353 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
ERROR    Error from Gemini API: 500 INTERNAL. {'error': {'code': 500, 'message':
         'An internal error has occurred. Please retry or report in             
         https://developers.generativeai.google/guide/troubleshooting',         
         'status': 'INTERNAL'}}                                                 
WARNING  Attempt 1/4 failed:                                                    
         <ClientResponse(https://generativelanguage.googleapis.com/v1beta/models
         /gemini-2.5-pro:generateContent) [500 Internal Server Error]>          
         <CIMultiDictProxy('Vary': 'Origin', 'Vary': 'X-Origin', 'Vary':        
         'Referer', 'Content-Type': 'application/json; charset=UTF-8',          
         'Content-Encoding': 'gzip', 'Date': 'Mon, 04 Aug 2025 13:44:26 GMT',   
         'Server': 'scaffolding on HTTPServer2', 'X-XSS-Protection': '0',       
         'X-Frame-Options': 'SAMEORIGIN', 'X-Content-Type-Options': 'nosniff',  
         'Server-Timing': 'gfet4t7; dur=8225', 'Alt-Svc': 'h3=":443";           
         ma=2592000,h3-29=":443"; ma=2592000', 'Transfer-Encoding': 'chunked')> 
                                                                                
2025-08-04 13:44:32.147 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em SDR Team: Erro no processamento: 'AgentMemory' object has no attribute 'get_team_context_str' | Data: {'component': 'SDR Team'}
INFO:     127.0.0.1:39012 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-04 13:44:53.791 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Boa! Peraí, deixa eu confirmar isso aqui pra gente ter certeza absoluta...
2025-08-04 13:44:58.907 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 71, 'delay_used': 2.82, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 13:44:58.908 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Boa! Peraí, deixa eu confirmar isso aqui pra gente', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 13:44:58.908 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB05350A586D80887D9852A5CFBD6466F4F230E
2025-08-04 13:45:00.890 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 13:45:00.890 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:43328 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK
2025-08-04 13:45:00.891 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:43338 - "POST /webhook/whatsapp/messages-update HTTP/1.1" 200 OK