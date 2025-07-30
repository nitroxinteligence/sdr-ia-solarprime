NFO:     10.0.1.4:47124 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 18:18:55.217 | INFO     | services.message_buffer_service:add_message:86 - Mensagem adicionada ao buffer para 558182986181@s.whatsapp.net. Total no buffer: 1
2025-07-29 18:18:55.217 | INFO     | services.message_buffer_service:add_message:114 - Timer criado/resetado para 558182986181@s.whatsapp.net - Aguardando 8.0s para processar 1 mensagens
2025-07-29 18:18:55.217 | DEBUG    | services.message_buffer_service:_wait_and_process:124 - Timer iniciado para 558182986181@s.whatsapp.net - aguardando 8.0s
2025-07-29 18:19:03.216 | INFO     | services.message_buffer_service:_wait_and_process:138 - Timer expirado para 558182986181@s.whatsapp.net - iniciando processamento
2025-07-29 18:19:03.217 | INFO     | services.message_buffer_service:_process_buffer:180 - Iniciando processamento de 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-29 18:19:03.217 | DEBUG    | services.message_buffer_service:_process_buffer:196 -   Mensagem 1: O que tem nessa imagem?... (tipo: image)
2025-07-29 18:19:03.217 | INFO     | services.message_buffer_service:_process_buffer:199 - Executando callback para processar 1 mensagens de 558182986181@s.whatsapp.net
2025-07-29 18:19:03.233 | INFO     | agents.sdr_agent:process_message:170 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-29 18:19:03.234 | INFO     | repositories.lead_repository:create_or_update:40 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-29 18:19:04.673 | INFO     | repositories.base:update:100 - Updated leads record: 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 18:19:05.736 | INFO     | agents.sdr_agent:_get_or_create_agent:129 - Novo agente criado para telefone: 558182986181@s.whatsapp.net
2025-07-29 18:19:06.367 | INFO     | repositories.base:create:31 - Created messages record: 9ca49e97-9863-4211-bf29-8c627fdaba38
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.

------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------

INFO:     127.0.0.1:37990 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-29 18:19:22.582 | INFO     | agents.sdr_agent:_analyze_context:652 - Mudança de estágio: INITIAL_CONTACT -> QUALIFICATION
2025-07-29 18:19:22.582 | WARNING  | agents.sdr_agent:_process_media:885 - Tipo de mídia não suportado: buffered
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:53284 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-29 18:20:12.186 | INFO     | repositories.base:create:31 - Created messages record: dc64f37d-8935-4e61-b3e3-9b99f2d475f7
2025-07-29 18:20:12.810 | INFO     | repositories.base:update:100 - Updated conversations record: 6aaab738-994a-4056-9a75-aca0dae60aae
2025-07-29 18:20:14.103 | INFO     | repositories.base:update:100 - Updated conversations record: 6aaab738-994a-4056-9a75-aca0dae60aae
2025-07-29 18:20:14.724 | INFO     | repositories.base:update:100 - Updated leads record: 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 18:20:14.970 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-29 18:20:14.971 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 4 chunks, tempo total: 25.9s
INFO:     10.0.1.4:45830 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     127.0.0.1:60408 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.0.1.4:45830 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.0.1.4:45830 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 18:20:29.270 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-29 18:20:30.499 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:119 - Cancelados 1 follow-ups pendentes para lead 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 18:20:31.134 | INFO     | services.follow_up_service:create_follow_up_after_message:91 - Follow-up criado para lead 2a3976b7-e986-4546-b995-a467459efc6f - Tipo: first_contact - Agendado para: 15:50 (30 minutos)
2025-07-29 18:20:31.134 | INFO     | services.message_buffer_service:_process_buffer:206 - Processamento concluído para 558182986181@s.whatsapp.net - 1 mensagens processadas
2025-07-29 18:20:31.134 | DEBUG    | services.message_buffer_service:_process_buffer_with_lock:168 - Flag de processamento limpa para 558182986181@s.whatsapp.net
INFO:     10.0.1.4:45830 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     127.0.0.1:47850 - "GET /health HTTP/1.1" 307 Temporary Redirect