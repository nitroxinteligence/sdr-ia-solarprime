INFO:     Received SIGTERM, exiting.
INFO:     Terminated child process [8]
INFO:     Terminated child process [9]
INFO:     Waiting for child process [8]
INFO:     Shutting down
INFO:     Shutting down
INFO:     Waiting for application shutdown.
2025-07-29 16:35:53.297 | INFO     | services.connection_monitor:stop:74 - Monitor de conexão WhatsApp parado
INFO:     Application shutdown complete.
INFO:     Finished server process [8]
INFO:     Waiting for child process [9]
INFO:     Waiting for application shutdown.
2025-07-29 16:35:53.367 | INFO     | services.connection_monitor:stop:74 - Monitor de conexão WhatsApp parado
INFO:     Application shutdown complete.
INFO:     Finished server process [9]
INFO:     Stopping parent process [1]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started parent process [1]
2025-07-29 16:35:56.963 | INFO     | services.message_buffer_service:__init__:38 - MessageBufferService iniciado - Enabled: True, Timeout: 8.0s
2025-07-29 16:35:56.963 | INFO     | services.message_buffer_service:__init__:38 - MessageBufferService iniciado - Enabled: True, Timeout: 8.0s
2025-07-29 16:36:00.143 | INFO     | services.database:_initialize_client:43 - ✅ Supabase client initialized successfully
2025-07-29 16:36:00.144 | INFO     | services.database:_initialize_client:43 - ✅ Supabase client initialized successfully
2025-07-29 16:36:00.185 | INFO     | agents.sdr_agent:__init__:67 - Modelo de fallback OpenAI configurado: gpt-4.1-nano
2025-07-29 16:36:00.186 | INFO     | agents.sdr_agent:__init__:67 - Modelo de fallback OpenAI configurado: gpt-4.1-nano
2025-07-29 16:36:00.193 | INFO     | agents.sdr_agent:__init__:86 - SDR Agent 'Luna' inicializado com AGnO Framework
2025-07-29 16:36:00.193 | WARNING  | services.redis_fallback:__init__:19 - ⚠️ Usando cache em memória (Redis não disponível)
2025-07-29 16:36:00.195 | INFO     | agents.sdr_agent:__init__:86 - SDR Agent 'Luna' inicializado com AGnO Framework
2025-07-29 16:36:00.195 | WARNING  | services.redis_fallback:__init__:19 - ⚠️ Usando cache em memória (Redis não disponível)
INFO:     Started server process [9]
INFO:     Waiting for application startup.
INFO:     Started server process [8]
INFO:     Waiting for application startup.
2025-07-29 16:36:02.307 | INFO     | services.connection_monitor:start:61 - 🔍 Monitor de conexão WhatsApp iniciado
INFO:     Application startup complete.
2025-07-29 16:36:02.314 | INFO     | services.connection_monitor:_handle_state_change:167 - 📱 WhatsApp mudou de unknown para connected
2025-07-29 16:36:02.320 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-29 16:36:02.321 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-29 16:36:02.321 | INFO     | services.redis_fallback:_try_redis_connection:111 - ✅ Conectado ao Redis
2025-07-29 16:36:02.323 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-29 16:36:02.323 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-29 16:36:02.328 | INFO     | services.connection_monitor:start:61 - 🔍 Monitor de conexão WhatsApp iniciado
INFO:     Application startup complete.
2025-07-29 16:36:02.336 | INFO     | services.connection_monitor:_handle_state_change:167 - 📱 WhatsApp mudou de unknown para connected
2025-07-29 16:36:02.342 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-29 16:36:02.342 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-29 16:36:02.342 | INFO     | services.redis_fallback:_try_redis_connection:111 - ✅ Conectado ao Redis
2025-07-29 16:36:02.344 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-29 16:36:02.344 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
INFO:     127.0.0.1:46846 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.0.1.4:36938 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:36:05.768 | INFO     | services.message_buffer_service:add_message:70 - Mensagem adicionada ao buffer local para 558182986181@s.whatsapp.net. Total: 1
2025-07-29 16:36:05.769 | INFO     | services.message_buffer_service:add_message:91 - Timer criado para 558182986181@s.whatsapp.net - Aguardando 8.0s
2025-07-29 16:36:13.769 | INFO     | services.message_buffer_service:_process_buffer:137 - Processando 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-29 16:36:13.786 | INFO     | agents.sdr_agent:process_message:153 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-29 16:36:13.786 | INFO     | repositories.lead_repository:create_or_update:40 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-29 16:36:14.848 | INFO     | repositories.base:update:100 - Updated leads record: 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 16:36:16.315 | INFO     | agents.sdr_agent:_get_or_create_agent:112 - Novo agente criado para telefone: 558182986181@s.whatsapp.net
2025-07-29 16:36:16.940 | INFO     | repositories.base:create:31 - Created messages record: 9efda26c-f063-47aa-a16c-e78f857cf877
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     10.0.1.4:49240 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.0.1.4:49240 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     127.0.0.1:36392 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.0.1.4:36344 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.0.1.4:36344 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:37:01.963 | INFO     | services.message_buffer_service:add_message:70 - Mensagem adicionada ao buffer local para 558182986181@s.whatsapp.net. Total: 1
2025-07-29 16:37:01.963 | INFO     | services.message_buffer_service:add_message:91 - Timer criado para 558182986181@s.whatsapp.net - Aguardando 8.0s
INFO:     127.0.0.1:43406 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-29 16:37:09.964 | INFO     | services.message_buffer_service:_process_buffer:137 - Processando 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-29 16:37:09.983 | INFO     | agents.sdr_agent:process_message:153 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-29 16:37:09.983 | INFO     | repositories.lead_repository:create_or_update:40 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-29 16:37:11.355 | INFO     | repositories.base:update:100 - Updated leads record: 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 16:37:12.869 | INFO     | agents.sdr_agent:_get_or_create_agent:112 - Novo agente criado para telefone: 558182986181@s.whatsapp.net
2025-07-29 16:37:13.524 | INFO     | repositories.base:create:31 - Created messages record: b180e304-2ed9-4385-af5a-b30fd1b3a60b
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
2025-07-29 16:37:21.762 | INFO     | repositories.base:create:31 - Created messages record: 5104615e-f14f-44c1-ad9f-445a6ca71c92
2025-07-29 16:37:22.380 | INFO     | repositories.base:update:100 - Updated conversations record: 4866cdd9-d938-4743-9851-fa25bb5e2ecf
2025-07-29 16:37:22.942 | INFO     | agents.sdr_agent:_analyze_context:634 - Mudança de estágio: INITIAL_CONTACT -> IDENTIFICATION
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
2025-07-29 16:37:23.604 | INFO     | repositories.base:update:100 - Updated conversations record: 4866cdd9-d938-4743-9851-fa25bb5e2ecf
2025-07-29 16:37:24.203 | INFO     | repositories.base:update:100 - Updated leads record: 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 16:37:24.438 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-29 16:37:24.439 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 3 chunks, tempo total: 21.0s
INFO:     10.0.1.4:53582 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.0.1.4:53582 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:37:34.250 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
INFO:     10.0.1.4:53582 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:37:35.485 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:117 - Cancelados 1 follow-ups pendentes para lead 2a3976b7-e986-4546-b995-a467459efc6f
INFO:     127.0.0.1:39046 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-29 16:37:36.087 | INFO     | services.follow_up_service:create_follow_up_after_message:89 - Follow-up criado para lead 2a3976b7-e986-4546-b995-a467459efc6f - Tipo: first_contact - Agendado para: 17:07 (30 minutos)
INFO:     10.0.1.4:50332 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.0.1.4:50340 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
2025-07-29 16:37:52.251 | INFO     | repositories.base:create:31 - Created messages record: 1c343ea2-9336-4370-9c7a-e75309d60776
2025-07-29 16:37:52.513 | INFO     | repositories.base:update:100 - Updated conversations record: 4866cdd9-d938-4743-9851-fa25bb5e2ecf
2025-07-29 16:37:53.742 | INFO     | repositories.base:update:100 - Updated conversations record: 4866cdd9-d938-4743-9851-fa25bb5e2ecf
2025-07-29 16:37:54.376 | INFO     | repositories.base:update:100 - Updated leads record: 2a3976b7-e986-4546-b995-a467459efc6f
INFO:     10.0.1.4:50340 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:37:54.422 | INFO     | services.message_buffer_service:add_message:70 - Mensagem adicionada ao buffer local para 558182986181@s.whatsapp.net. Total: 1
2025-07-29 16:37:54.422 | INFO     | services.message_buffer_service:add_message:91 - Timer criado para 558182986181@s.whatsapp.net - Aguardando 8.0s
INFO:     10.0.1.4:50340 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
2025-07-29 16:37:55.005 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-29 16:37:55.006 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 2 chunks, tempo total: 12.6s
INFO:     10.0.1.4:50332 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:37:55.011 | INFO     | services.message_buffer_service:add_message:70 - Mensagem adicionada ao buffer local para 558182986181@s.whatsapp.net. Total: 1
2025-07-29 16:37:55.011 | DEBUG    | services.message_buffer_service:add_message:84 - Timer resetado para 558182986181@s.whatsapp.net
2025-07-29 16:37:55.011 | INFO     | services.message_buffer_service:add_message:91 - Timer criado para 558182986181@s.whatsapp.net - Aguardando 8.0s
INFO:     10.0.1.4:50332 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.0.1.4:50332 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:37:57.317 | INFO     | services.message_buffer_service:add_message:70 - Mensagem adicionada ao buffer local para 558182986181@s.whatsapp.net. Total: 2
2025-07-29 16:37:57.317 | DEBUG    | services.message_buffer_service:add_message:84 - Timer resetado para 558182986181@s.whatsapp.net
2025-07-29 16:37:57.317 | INFO     | services.message_buffer_service:add_message:91 - Timer criado para 558182986181@s.whatsapp.net - Aguardando 8.0s
2025-07-29 16:37:57.317 | DEBUG    | services.message_buffer_service:_wait_and_process:110 - Timer cancelado para 558182986181@s.whatsapp.net
2025-07-29 16:38:00.202 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
INFO:     10.0.1.4:50714 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:38:00.678 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:117 - Cancelados 1 follow-ups pendentes para lead 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 16:38:00.925 | INFO     | services.follow_up_service:create_follow_up_after_message:89 - Follow-up criado para lead 2a3976b7-e986-4546-b995-a467459efc6f - Tipo: first_contact - Agendado para: 17:08 (30 minutos)
INFO:     10.0.1.4:50332 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.0.1.4:50332 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:38:02.215 | INFO     | services.message_buffer_service:add_message:70 - Mensagem adicionada ao buffer local para 558182986181@s.whatsapp.net. Total: 3
2025-07-29 16:38:02.215 | DEBUG    | services.message_buffer_service:add_message:84 - Timer resetado para 558182986181@s.whatsapp.net
2025-07-29 16:38:02.215 | INFO     | services.message_buffer_service:add_message:91 - Timer criado para 558182986181@s.whatsapp.net - Aguardando 8.0s
2025-07-29 16:38:02.215 | DEBUG    | services.message_buffer_service:_wait_and_process:110 - Timer cancelado para 558182986181@s.whatsapp.net
2025-07-29 16:38:02.422 | INFO     | services.message_buffer_service:_process_buffer:137 - Processando 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-29 16:38:02.440 | INFO     | agents.sdr_agent:process_message:153 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-29 16:38:02.440 | INFO     | repositories.lead_repository:create_or_update:40 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-29 16:38:03.715 | INFO     | repositories.base:update:100 - Updated leads record: 2a3976b7-e986-4546-b995-a467459efc6f
INFO:     127.0.0.1:39574 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-29 16:38:05.904 | INFO     | repositories.base:create:31 - Created messages record: 9dd09590-cc8d-4020-a5e8-099b7c001972
2025-07-29 16:38:10.216 | INFO     | services.message_buffer_service:_process_buffer:137 - Processando 3 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-29 16:38:10.234 | INFO     | agents.sdr_agent:process_message:153 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-29 16:38:10.235 | INFO     | repositories.lead_repository:create_or_update:40 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-29 16:38:10.718 | INFO     | repositories.base:update:100 - Updated leads record: 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 16:38:11.647 | INFO     | repositories.base:create:31 - Created messages record: 7823e0dc-7e66-43ca-8d17-5741fb34c2f0
2025-07-29 16:38:22.769 | INFO     | agents.sdr_agent:_analyze_context:634 - Mudança de estágio: INITIAL_CONTACT -> DISCOVERY
2025-07-29 16:38:22.770 | INFO     | agents.sdr_agent:_update_lead_info:925 - Nome identificado: Mateus
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
2025-07-29 16:38:27.910 | INFO     | agents.sdr_agent:_analyze_context:634 - Mudança de estágio: INITIAL_CONTACT -> QUALIFICATION
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:41942 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-29 16:38:41.278 | INFO     | repositories.base:create:31 - Created messages record: 9b5f124b-9f6b-4170-83fa-51c1246f887f
2025-07-29 16:38:41.522 | INFO     | repositories.base:update:100 - Updated conversations record: 4866cdd9-d938-4743-9851-fa25bb5e2ecf
2025-07-29 16:38:42.372 | INFO     | repositories.base:update:100 - Updated conversations record: 4866cdd9-d938-4743-9851-fa25bb5e2ecf
2025-07-29 16:38:42.625 | INFO     | repositories.base:update:100 - Updated leads record: 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 16:38:42.853 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-29 16:38:42.854 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 2 chunks, tempo total: 13.5s
INFO:     10.0.1.4:45244 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:38:47.872 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
INFO:     10.0.1.4:45244 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:38:48.349 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:117 - Cancelados 1 follow-ups pendentes para lead 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 16:38:48.578 | INFO     | services.follow_up_service:create_follow_up_after_message:89 - Follow-up criado para lead 2a3976b7-e986-4546-b995-a467459efc6f - Tipo: first_contact - Agendado para: 17:08 (30 minutos)
INFO:     127.0.0.1:34750 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-29 16:39:06.029 | INFO     | repositories.base:create:31 - Created messages record: 999f8eed-135f-4774-8e25-e9660bcf7b88
2025-07-29 16:39:06.248 | INFO     | repositories.base:update:100 - Updated conversations record: 4866cdd9-d938-4743-9851-fa25bb5e2ecf
2025-07-29 16:39:07.073 | INFO     | repositories.base:update:100 - Updated conversations record: 4866cdd9-d938-4743-9851-fa25bb5e2ecf
2025-07-29 16:39:07.074 | WARNING  | agents.sdr_agent:process_message:299 - Erro ao converter bill_value para float: could not convert string to float: 'R$ 800'
2025-07-29 16:39:07.074 | DEBUG    | agents.sdr_agent:_calculate_qualification_score:1276 - Erro ao processar valor da conta para lead score: could not convert string to float: 'R$ 800'
2025-07-29 16:39:07.684 | INFO     | repositories.base:update:100 - Updated leads record: 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 16:39:07.911 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-29 16:39:07.912 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 4 chunks, tempo total: 33.8s
INFO:     10.0.1.4:33820 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.0.1.4:33820 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.0.1.4:33820 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-29 16:39:21.811 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-29 16:39:23.012 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:117 - Cancelados 1 follow-ups pendentes para lead 2a3976b7-e986-4546-b995-a467459efc6f
2025-07-29 16:39:23.248 | INFO     | services.follow_up_service:create_follow_up_after_message:89 - Follow-up criado para lead 2a3976b7-e986-4546-b995-a467459efc6f - Tipo: first_contact - Agendado para: 17:09 (30 minutos)
INFO:     10.0.1.4:33820 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     127.0.0.1:55994 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:49866 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:34106 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-29 16:41:02.346 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-29 16:41:02.347 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-29 16:41:02.365 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-29 16:41:02.366 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
INFO:     127.0.0.1:33666 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:54696 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:49754 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:58774 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:43198 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:45672 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:50650 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:35720 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:46606 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:47690 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-29 16:46:02.368 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-29 16:46:02.369 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-29 16:46:02.376 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-29 16:46:02.376 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
INFO:     127.0.0.1:38406 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:33730 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:49060 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:54144 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:43246 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:56992 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:47148 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:54974 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:59244 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:35218 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-29 16:51:02.395 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-29 16:51:02.395 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-29 16:51:02.398 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-29 16:51:02.398 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
INFO:     127.0.0.1:48294 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:42416 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:34836 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:35512 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:33720 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:42450 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:49658 - "GET /health HTTP/1.1" 307 Temporary Redirect