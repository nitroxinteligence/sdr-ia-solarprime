INFO:     127.0.0.1:39062 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     Received SIGTERM, exiting.
INFO:     Terminated child process [8]
INFO:     Terminated child process [9]
INFO:     Waiting for child process [8]
INFO:     Shutting down
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Waiting for application shutdown.
2025-07-27 21:31:15.555 | INFO     | services.connection_monitor:stop:74 - Monitor de conexão WhatsApp parado
2025-07-27 21:31:15.556 | INFO     | services.connection_monitor:stop:74 - Monitor de conexão WhatsApp parado
INFO:     Application shutdown complete.
INFO:     Finished server process [8]
INFO:     Application shutdown complete.
INFO:     Finished server process [9]
INFO:     Waiting for child process [9]
INFO:     Stopping parent process [1]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started parent process [1]
2025-07-27 21:31:21.496 | INFO     | services.database:_initialize_client:43 - ✅ Supabase client initialized successfully
2025-07-27 21:31:21.536 | INFO     | agents.sdr_agent:__init__:65 - SDR Agent 'Luna' inicializado com AGnO Framework
2025-07-27 21:31:21.536 | WARNING  | services.redis_fallback:__init__:19 - ⚠️ Usando cache em memória (Redis não disponível)
2025-07-27 21:31:21.536 | INFO     | services.database:_initialize_client:43 - ✅ Supabase client initialized successfully
2025-07-27 21:31:21.575 | INFO     | agents.sdr_agent:__init__:65 - SDR Agent 'Luna' inicializado com AGnO Framework
2025-07-27 21:31:21.575 | WARNING  | services.redis_fallback:__init__:19 - ⚠️ Usando cache em memória (Redis não disponível)
INFO:     Started server process [9]
INFO:     Waiting for application startup.
INFO:     Started server process [8]
INFO:     Waiting for application startup.
2025-07-27 21:31:23.636 | INFO     | services.connection_monitor:start:61 - 🔍 Monitor de conexão WhatsApp iniciado
INFO:     Application startup complete.
2025-07-27 21:31:23.642 | INFO     | services.connection_monitor:_handle_state_change:167 - 📱 WhatsApp mudou de unknown para connected
2025-07-27 21:31:23.646 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:31:23.647 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:31:23.647 | INFO     | services.redis_fallback:_try_redis_connection:108 - ✅ Conectado ao Redis
2025-07-27 21:31:23.648 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:31:23.648 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:31:23.678 | INFO     | services.connection_monitor:start:61 - 🔍 Monitor de conexão WhatsApp iniciado
INFO:     Application startup complete.
2025-07-27 21:31:23.684 | INFO     | services.connection_monitor:_handle_state_change:167 - 📱 WhatsApp mudou de unknown para connected
2025-07-27 21:31:23.688 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:31:23.688 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:31:23.688 | INFO     | services.redis_fallback:_try_redis_connection:108 - ✅ Conectado ao Redis
2025-07-27 21:31:23.692 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:31:23.692 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
INFO:     127.0.0.1:54354 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.0.1.4:51546 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.0.1.4:51546 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-27 21:31:43.312 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:31:43.313 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:31:43.329 | INFO     | agents.sdr_agent:process_message:133 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-27 21:31:43.330 | INFO     | repositories.lead_repository:create_or_update:40 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-27 21:31:44.745 | INFO     | repositories.base:create:31 - Created leads record: 4a9891f7-064b-4396-9df4-9699f5a98837
2025-07-27 21:31:45.948 | INFO     | repositories.base:create:31 - Created conversations record: f31026bd-3fc9-442d-af70-58a97c229b6e
2025-07-27 21:31:45.949 | ERROR    | agents.sdr_agent:process_message:299 - Erro ao processar mensagem: Agent.__init__() got an unexpected keyword argument 'structured_output'
2025-07-27 21:31:46.166 | ERROR    | services.analytics_service:track_event:41 - Error tracking analytics event: object APIResponse[~_ReturnT] can't be used in 'await' expression
INFO:     10.0.1.4:51546 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.0.1.4:51546 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Erro ao processar webhook: 'str' object has no attribute 'get'
Traceback (most recent call last):
  File "/app/services/whatsapp_service.py", line 53, in process_webhook
    return await self._handle_message_update(payload)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/services/whatsapp_service.py", line 344, in _handle_message_update
    message_id = update.get("key", {}).get("id")
                 ^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'
Erro no processamento: 'str' object has no attribute 'get'
INFO:     127.0.0.1:37222 - "GET /health HTTP/1.1" 307 Temporary Redirect
