
INFO:     Received SIGTERM, exiting.
INFO:     Terminated child process [8]
INFO:     Terminated child process [9]
INFO:     Waiting for child process [8]
INFO:     Shutting down
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Waiting for application shutdown.
2025-07-27 21:55:42.577 | INFO     | services.connection_monitor:stop:74 - Monitor de conexão WhatsApp parado
2025-07-27 21:55:42.577 | INFO     | services.connection_monitor:stop:74 - Monitor de conexão WhatsApp parado
INFO:     Application shutdown complete.
INFO:     Application shutdown complete.
INFO:     Finished server process [8]
INFO:     Finished server process [9]
INFO:     Waiting for child process [9]
INFO:     Stopping parent process [1]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started parent process [1]
2025-07-27 21:55:48.262 | INFO     | services.database:_initialize_client:43 - ✅ Supabase client initialized successfully
2025-07-27 21:55:48.280 | INFO     | services.database:_initialize_client:43 - ✅ Supabase client initialized successfully
2025-07-27 21:55:48.303 | INFO     | agents.sdr_agent:__init__:65 - SDR Agent 'Luna' inicializado com AGnO Framework
2025-07-27 21:55:48.303 | WARNING  | services.redis_fallback:__init__:19 - ⚠️ Usando cache em memória (Redis não disponível)
2025-07-27 21:55:48.318 | INFO     | agents.sdr_agent:__init__:65 - SDR Agent 'Luna' inicializado com AGnO Framework
2025-07-27 21:55:48.318 | WARNING  | services.redis_fallback:__init__:19 - ⚠️ Usando cache em memória (Redis não disponível)
INFO:     Started server process [8]
INFO:     Waiting for application startup.
INFO:     Started server process [9]
INFO:     Waiting for application startup.
2025-07-27 21:55:50.440 | INFO     | services.connection_monitor:start:61 - 🔍 Monitor de conexão WhatsApp iniciado
INFO:     Application startup complete.
2025-07-27 21:55:50.442 | INFO     | services.connection_monitor:start:61 - 🔍 Monitor de conexão WhatsApp iniciado
INFO:     Application startup complete.
2025-07-27 21:55:50.447 | INFO     | services.connection_monitor:_handle_state_change:167 - 📱 WhatsApp mudou de unknown para connected
2025-07-27 21:55:50.447 | INFO     | services.connection_monitor:_handle_state_change:167 - 📱 WhatsApp mudou de unknown para connected
2025-07-27 21:55:50.451 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:55:50.452 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:55:50.452 | INFO     | services.redis_fallback:_try_redis_connection:108 - ✅ Conectado ao Redis
2025-07-27 21:55:50.452 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:55:50.452 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:55:50.452 | INFO     | services.redis_fallback:_try_redis_connection:108 - ✅ Conectado ao Redis
2025-07-27 21:55:50.454 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:55:50.454 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:55:50.455 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:55:50.455 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
INFO:     127.0.0.1:49062 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.0.1.4:46794 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.0.1.4:46794 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-27 21:56:05.424 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:56:05.424 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:56:05.437 | INFO     | agents.sdr_agent:process_message:131 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-27 21:56:05.438 | INFO     | repositories.lead_repository:create_or_update:40 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-27 21:56:06.868 | INFO     | repositories.base:update:100 - Updated leads record: 4a9891f7-064b-4396-9df4-9699f5a98837
2025-07-27 21:56:07.466 | INFO     | agents.sdr_agent:_get_or_create_agent:91 - Novo agente criado para telefone: 558182986181@s.whatsapp.net
2025-07-27 21:56:08.109 | INFO     | repositories.base:create:31 - Created messages record: 3be56c81-96ce-4bb4-b96e-6e8de16654ae
2025-07-27 21:56:16.035 | INFO     | agents.sdr_agent:_analyze_context:466 - Mudança de estágio: INITIAL_CONTACT -> IDENTIFICATION
INFO:     127.0.0.1:36600 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-27 21:56:44.732 | ERROR    | agents.sdr_agent:process_message:297 - Erro ao processar mensagem: name 'UUID' is not defined
2025-07-27 21:56:45.540 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: message_processed
INFO:     10.0.1.4:59892 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-27 21:56:50.465 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:56:50.466 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:56:50.466 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:56:50.466 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
INFO:     127.0.0.1:37204 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:51624 - "GET /health HTTP/1.1" 307 Temporary Redirect
