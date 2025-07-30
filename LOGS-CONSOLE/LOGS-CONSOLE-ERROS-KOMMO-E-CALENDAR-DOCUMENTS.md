============================================================
🚀 SDR IA SolarPrime - Configuração de Ambiente
============================================================
📍 Ambiente: PRODUCTION
🐳 Docker: Sim
🔧 Modo: Produção
------------------------------------------------------------
2025-07-30 19:17:52.778 | INFO     | core.environment:validate_services:87 - 🔍 Verificando Evolution API...
2025-07-30 19:17:52.812 | INFO     | core.environment:validate_services:111 - 🔍 Verificando Redis...

📡 Status dos Serviços:
------------------------------------------------------------
✅ Evolution Api: http://evolution-api:8080
⚠️ Redis: redis://redis:6379/0
   └─ Não foi possível conectar
------------------------------------------------------------
============================================================


============================================================
🔍 Validação de Configuração - SDR IA SolarPrime
============================================================

ℹ️  Informações:
   ✅ GEMINI_API_KEY configurada (AIza****...)
   ✅ EVOLUTION_API_KEY configurada (3ECB****...)
   ✅ EVOLUTION_INSTANCE_NAME configurada (SDR ****...)
   ✅ REDIS_URL configurada
   ✅ SUPABASE_URL configurada
   ✅ KOMMO_CLIENT_ID configurada
   ✅ KOMMO_CLIENT_SECRET configurada
   ✅ Diretório logs OK
   ✅ Diretório temp OK
   ✅ Diretório uploads OK
   ✅ Diretório data OK

⚠️  Avisos:
   ⚠️  SUPABASE_KEY não configurada - Chave do Supabase

------------------------------------------------------------
⚠️  Validação OK com avisos - Funcionalidade limitada
============================================================

2025-07-30 19:17:54.870 | INFO     | services.connection_monitor:start:61 - 🔍 Monitor de conexão WhatsApp iniciado
2025-07-30 19:17:54.871 | INFO     | workflows.follow_up_workflow:start:369 - Follow-up scheduler iniciado
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
2025-07-30 19:17:55.717 | INFO     | services.connection_monitor:_handle_state_change:167 - 📱 WhatsApp mudou de unknown para connected
2025-07-30 19:17:55.731 | ERROR    | services.redis_service:connect:79 - ❌ Erro ao conectar ao Redis: ConnectionError: Error -2 connecting to redis:6379. -2.
2025-07-30 19:17:55.731 | INFO     | services.redis_service:connect:80 - 📍 URL tentada: redis://redis:6379/0
2025-07-30 19:17:55.731 | INFO     | services.redis_fallback:_try_redis_connection:111 - ✅ Conectado ao Redis
2025-07-30 19:17:55.738 | ERROR    | services.redis_service:connect:79 - ❌ Erro ao conectar ao Redis: ConnectionError: Error -2 connecting to redis:6379. -2.
2025-07-30 19:17:55.738 | INFO     | services.redis_service:connect:80 - 📍 URL tentada: redis://redis:6379/0
INFO:     127.0.0.1:33022 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.11.0.4:43658 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.11.0.4:54302 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     127.0.0.1:53488 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.11.0.4:54088 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:18:32.460 | INFO     | services.message_buffer_service:add_message:86 - Mensagem adicionada ao buffer para 558182986181@s.whatsapp.net. Total no buffer: 1
2025-07-30 19:18:32.462 | INFO     | services.message_buffer_service:add_message:114 - Timer criado/resetado para 558182986181@s.whatsapp.net - Aguardando 8.0s para processar 1 mensagens
2025-07-30 19:18:32.463 | DEBUG    | services.message_buffer_service:_wait_and_process:124 - Timer iniciado para 558182986181@s.whatsapp.net - aguardando 8.0s
2025-07-30 19:18:40.463 | INFO     | services.message_buffer_service:_wait_and_process:138 - Timer expirado para 558182986181@s.whatsapp.net - iniciando processamento
2025-07-30 19:18:40.463 | INFO     | services.message_buffer_service:_process_buffer:180 - Iniciando processamento de 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-30 19:18:40.463 | DEBUG    | services.message_buffer_service:_process_buffer:196 -   Mensagem 1: Opa, boa tarde... (tipo: text)
2025-07-30 19:18:40.463 | INFO     | services.message_buffer_service:_process_buffer:199 - Executando callback para processar 1 mensagens de 558182986181@s.whatsapp.net
2025-07-30 19:18:40.483 | INFO     | agents.sdr_agent:process_message:159 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:18:40.484 | INFO     | repositories.lead_repository:create_or_update:41 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:18:41.758 | INFO     | repositories.base:create:31 - Created leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:18:42.954 | INFO     | repositories.base:create:31 - Created conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:18:43.397 | INFO     | agents.sdr_agent:_get_or_create_agent:118 - Novo agente criado para telefone: 558182986181@s.whatsapp.net
2025-07-30 19:18:43.617 | INFO     | repositories.base:create:31 - Created messages record: b850879e-f811-4bed-a1fa-2d4c1ae48fa0
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
2025-07-30 19:18:54.588 | INFO     | agents.sdr_agent:_analyze_context:635 - Mudança de estágio: INITIAL_CONTACT -> IDENTIFICATION
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:53882 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:39176 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:19:53.641 | INFO     | repositories.base:create:31 - Created messages record: c959ae7f-47f1-47cf-a179-f11280ad61d0
2025-07-30 19:19:54.236 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:19:55.042 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:19:55.628 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:19:56.225 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-30 19:19:56.226 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 2 chunks, tempo total: 12.9s
INFO:     127.0.0.1:34348 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.11.0.4:52008 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:20:01.950 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-30 19:20:03.863 | INFO     | services.follow_up_service:create_follow_up_after_message:91 - Follow-up criado para lead 742170c7-ae11-4c45-826e-94aea4e92cff - Tipo: first_contact - Agendado para: 16:50 (30 minutos)
2025-07-30 19:20:03.863 | INFO     | services.message_buffer_service:_process_buffer:206 - Processamento concluído para 558182986181@s.whatsapp.net - 1 mensagens processadas
2025-07-30 19:20:03.863 | DEBUG    | services.message_buffer_service:_process_buffer_with_lock:168 - Flag de processamento limpa para 558182986181@s.whatsapp.net
INFO:     10.11.0.4:52008 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.11.0.4:46052 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.11.0.4:46052 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:20:18.759 | INFO     | services.message_buffer_service:add_message:86 - Mensagem adicionada ao buffer para 558182986181@s.whatsapp.net. Total no buffer: 1
2025-07-30 19:20:18.759 | INFO     | services.message_buffer_service:add_message:114 - Timer criado/resetado para 558182986181@s.whatsapp.net - Aguardando 8.0s para processar 1 mensagens
2025-07-30 19:20:18.759 | DEBUG    | services.message_buffer_service:_wait_and_process:124 - Timer iniciado para 558182986181@s.whatsapp.net - aguardando 8.0s
2025-07-30 19:20:26.760 | INFO     | services.message_buffer_service:_wait_and_process:138 - Timer expirado para 558182986181@s.whatsapp.net - iniciando processamento
2025-07-30 19:20:26.760 | INFO     | services.message_buffer_service:_process_buffer:180 - Iniciando processamento de 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-30 19:20:26.760 | DEBUG    | services.message_buffer_service:_process_buffer:196 -   Mensagem 1: economizar na minha conta de energia mesmo... (tipo: text)
2025-07-30 19:20:26.760 | INFO     | services.message_buffer_service:_process_buffer:199 - Executando callback para processar 1 mensagens de 558182986181@s.whatsapp.net
2025-07-30 19:20:26.780 | INFO     | agents.sdr_agent:process_message:159 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:20:26.780 | INFO     | repositories.lead_repository:create_or_update:41 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:20:27.261 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:20:28.910 | INFO     | repositories.base:create:31 - Created messages record: 92bfd4a6-a26f-408e-bda0-b23fbb6a140c
INFO:     127.0.0.1:53512 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:20:42.719 | INFO     | agents.sdr_agent:_analyze_context:635 - Mudança de estágio: IDENTIFICATION -> DISCOVERY
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:45548 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:21:12.205 | INFO     | repositories.base:create:31 - Created messages record: e96534fe-4d55-4704-b0e5-4c41ba6ee4cb
2025-07-30 19:21:12.435 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:21:12.905 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:21:13.118 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:21:13.330 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-30 19:21:13.330 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 2 chunks, tempo total: 14.2s
INFO:     10.11.0.4:44436 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:21:19.037 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-30 19:21:19.865 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:119 - Cancelados 1 follow-ups pendentes para lead 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:21:20.089 | INFO     | services.follow_up_service:create_follow_up_after_message:91 - Follow-up criado para lead 742170c7-ae11-4c45-826e-94aea4e92cff - Tipo: first_contact - Agendado para: 16:51 (30 minutos)
2025-07-30 19:21:20.089 | INFO     | services.message_buffer_service:_process_buffer:206 - Processamento concluído para 558182986181@s.whatsapp.net - 1 mensagens processadas
2025-07-30 19:21:20.089 | DEBUG    | services.message_buffer_service:_process_buffer_with_lock:168 - Flag de processamento limpa para 558182986181@s.whatsapp.net
INFO:     10.11.0.4:44436 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.11.0.4:44436 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.11.0.4:44436 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:21:25.438 | INFO     | services.message_buffer_service:add_message:86 - Mensagem adicionada ao buffer para 558182986181@s.whatsapp.net. Total no buffer: 1
2025-07-30 19:21:25.438 | INFO     | services.message_buffer_service:add_message:114 - Timer criado/resetado para 558182986181@s.whatsapp.net - Aguardando 8.0s para processar 1 mensagens
2025-07-30 19:21:25.438 | DEBUG    | services.message_buffer_service:_wait_and_process:124 - Timer iniciado para 558182986181@s.whatsapp.net - aguardando 8.0s
INFO:     127.0.0.1:51712 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:21:33.437 | INFO     | services.message_buffer_service:_wait_and_process:138 - Timer expirado para 558182986181@s.whatsapp.net - iniciando processamento
2025-07-30 19:21:33.438 | INFO     | services.message_buffer_service:_process_buffer:180 - Iniciando processamento de 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-30 19:21:33.438 | DEBUG    | services.message_buffer_service:_process_buffer:196 -   Mensagem 1: nao recebo... (tipo: text)
2025-07-30 19:21:33.438 | INFO     | services.message_buffer_service:_process_buffer:199 - Executando callback para processar 1 mensagens de 558182986181@s.whatsapp.net
2025-07-30 19:21:33.456 | INFO     | agents.sdr_agent:process_message:159 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:21:33.456 | INFO     | repositories.lead_repository:create_or_update:41 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:21:33.928 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:21:34.811 | INFO     | repositories.base:create:31 - Created messages record: 51a30a2d-ec73-44c4-8ce6-b0dbf74acdcc
2025-07-30 19:21:50.761 | INFO     | agents.sdr_agent:_analyze_context:635 - Mudança de estágio: IDENTIFICATION -> QUALIFICATION
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:48968 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:50666 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:22:44.711 | INFO     | repositories.base:create:31 - Created messages record: 91267eef-bb90-43c9-89dd-61b9c785f716
2025-07-30 19:22:45.317 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:22:45.758 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:22:45.979 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:22:46.212 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-30 19:22:46.213 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 2 chunks, tempo total: 10.6s
INFO:     10.11.0.4:57408 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:22:51.943 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-30 19:22:52.405 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:119 - Cancelados 1 follow-ups pendentes para lead 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:22:52.623 | INFO     | services.follow_up_service:create_follow_up_after_message:91 - Follow-up criado para lead 742170c7-ae11-4c45-826e-94aea4e92cff - Tipo: first_contact - Agendado para: 16:52 (30 minutos)
2025-07-30 19:22:52.623 | INFO     | services.message_buffer_service:_process_buffer:206 - Processamento concluído para 558182986181@s.whatsapp.net - 1 mensagens processadas
2025-07-30 19:22:52.623 | DEBUG    | services.message_buffer_service:_process_buffer_with_lock:168 - Flag de processamento limpa para 558182986181@s.whatsapp.net
INFO:     10.11.0.4:57408 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:22:55.747 | ERROR    | services.redis_service:connect:79 - ❌ Erro ao conectar ao Redis: ConnectionError: Error -2 connecting to redis:6379. -2.
2025-07-30 19:22:55.747 | INFO     | services.redis_service:connect:80 - 📍 URL tentada: redis://redis:6379/0
INFO:     127.0.0.1:60392 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.11.0.4:47182 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.11.0.4:47182 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:23:04.568 | INFO     | services.message_buffer_service:add_message:86 - Mensagem adicionada ao buffer para 558182986181@s.whatsapp.net. Total no buffer: 1
2025-07-30 19:23:04.568 | INFO     | services.message_buffer_service:add_message:114 - Timer criado/resetado para 558182986181@s.whatsapp.net - Aguardando 8.0s para processar 1 mensagens
2025-07-30 19:23:04.568 | DEBUG    | services.message_buffer_service:_wait_and_process:124 - Timer iniciado para 558182986181@s.whatsapp.net - aguardando 8.0s
2025-07-30 19:23:12.569 | INFO     | services.message_buffer_service:_wait_and_process:138 - Timer expirado para 558182986181@s.whatsapp.net - iniciando processamento
2025-07-30 19:23:12.569 | INFO     | services.message_buffer_service:_process_buffer:180 - Iniciando processamento de 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-30 19:23:12.569 | DEBUG    | services.message_buffer_service:_process_buffer:196 -   Mensagem 1: uns 5000 mil reais... (tipo: text)
2025-07-30 19:23:12.569 | INFO     | services.message_buffer_service:_process_buffer:199 - Executando callback para processar 1 mensagens de 558182986181@s.whatsapp.net
2025-07-30 19:23:12.587 | INFO     | agents.sdr_agent:process_message:159 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:23:12.588 | INFO     | repositories.lead_repository:create_or_update:41 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:23:13.061 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:23:13.954 | INFO     | repositories.base:create:31 - Created messages record: 9c9a6890-fb9f-48c6-9427-14084fc841f0
2025-07-30 19:23:27.251 | INFO     | agents.sdr_agent:_analyze_context:635 - Mudança de estágio: IDENTIFICATION -> QUALIFICATION
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:59954 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:55618 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:24:13.010 | INFO     | repositories.base:create:31 - Created messages record: 9a96b6ad-56a8-41a0-a822-e8ae92bc9080
2025-07-30 19:24:13.228 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:24:13.674 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:24:13.891 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:24:14.126 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-30 19:24:14.126 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 2 chunks, tempo total: 26.2s
INFO:     10.11.0.4:49010 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:24:19.874 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-30 19:24:20.323 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:119 - Cancelados 1 follow-ups pendentes para lead 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:24:20.543 | INFO     | services.follow_up_service:create_follow_up_after_message:91 - Follow-up criado para lead 742170c7-ae11-4c45-826e-94aea4e92cff - Tipo: first_contact - Agendado para: 16:54 (30 minutos)
2025-07-30 19:24:20.543 | INFO     | services.message_buffer_service:_process_buffer:206 - Processamento concluído para 558182986181@s.whatsapp.net - 1 mensagens processadas
2025-07-30 19:24:20.544 | DEBUG    | services.message_buffer_service:_process_buffer_with_lock:168 - Flag de processamento limpa para 558182986181@s.whatsapp.net
INFO:     10.11.0.4:49010 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     127.0.0.1:41932 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.11.0.4:43884 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.11.0.4:43884 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:24:34.033 | INFO     | services.message_buffer_service:add_message:86 - Mensagem adicionada ao buffer para 558182986181@s.whatsapp.net. Total no buffer: 1
2025-07-30 19:24:34.033 | INFO     | services.message_buffer_service:add_message:114 - Timer criado/resetado para 558182986181@s.whatsapp.net - Aguardando 8.0s para processar 1 mensagens
2025-07-30 19:24:34.033 | DEBUG    | services.message_buffer_service:_wait_and_process:124 - Timer iniciado para 558182986181@s.whatsapp.net - aguardando 8.0s
2025-07-30 19:24:42.033 | INFO     | services.message_buffer_service:_wait_and_process:138 - Timer expirado para 558182986181@s.whatsapp.net - iniciando processamento
2025-07-30 19:24:42.033 | INFO     | services.message_buffer_service:_process_buffer:180 - Iniciando processamento de 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-30 19:24:42.033 | DEBUG    | services.message_buffer_service:_process_buffer:196 -   Mensagem 1: sim, sou eu mesmo... (tipo: text)
2025-07-30 19:24:42.033 | INFO     | services.message_buffer_service:_process_buffer:199 - Executando callback para processar 1 mensagens de 558182986181@s.whatsapp.net
2025-07-30 19:24:42.052 | INFO     | agents.sdr_agent:process_message:159 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:24:42.053 | INFO     | repositories.lead_repository:create_or_update:41 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:24:43.282 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:24:44.541 | INFO     | repositories.base:create:31 - Created messages record: 31b53b93-24a9-42b9-974b-0de43ea30ba1
2025-07-30 19:24:58.551 | INFO     | agents.sdr_agent:_analyze_context:635 - Mudança de estágio: IDENTIFICATION -> DISCOVERY
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:33736 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:25:03.698 | ERROR    | api.routes.kommo_webhooks:kommo_webhook_events:88 - Erro ao processar webhook Kommo: Expecting value: line 1 column 1 (char 0)
INFO:     10.11.0.4:51064 - "POST /webhook/kommo/events HTTP/1.1" 500 Internal Server Error
2025-07-30 19:25:04.478 | ERROR    | api.routes.kommo_webhooks:kommo_webhook_events:88 - Erro ao processar webhook Kommo: Expecting value: line 1 column 1 (char 0)
INFO:     10.11.0.4:51064 - "POST /webhook/kommo/events HTTP/1.1" 500 Internal Server Error
2025-07-30 19:25:06.669 | ERROR    | api.routes.kommo_webhooks:kommo_webhook_events:88 - Erro ao processar webhook Kommo: Expecting value: line 1 column 1 (char 0)
INFO:     10.11.0.4:51064 - "POST /webhook/kommo/events HTTP/1.1" 500 Internal Server Error
INFO:     127.0.0.1:40918 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:25:44.821 | INFO     | repositories.base:create:31 - Created messages record: d382e087-0aaf-4335-acb2-537055685170
2025-07-30 19:25:45.051 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:25:45.486 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:25:45.712 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:25:45.940 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-30 19:25:45.940 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 2 chunks, tempo total: 15.4s
INFO:     10.11.0.4:44766 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:25:52.033 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-30 19:25:52.866 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:119 - Cancelados 1 follow-ups pendentes para lead 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:25:53.461 | INFO     | services.follow_up_service:create_follow_up_after_message:91 - Follow-up criado para lead 742170c7-ae11-4c45-826e-94aea4e92cff - Tipo: first_contact - Agendado para: 16:55 (30 minutos)
2025-07-30 19:25:53.461 | INFO     | services.message_buffer_service:_process_buffer:206 - Processamento concluído para 558182986181@s.whatsapp.net - 1 mensagens processadas
2025-07-30 19:25:53.461 | DEBUG    | services.message_buffer_service:_process_buffer_with_lock:168 - Flag de processamento limpa para 558182986181@s.whatsapp.net
INFO:     10.11.0.4:44766 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     127.0.0.1:54188 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.11.0.4:38510 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.11.0.4:38510 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:26:20.484 | INFO     | services.message_buffer_service:add_message:86 - Mensagem adicionada ao buffer para 558182986181@s.whatsapp.net. Total no buffer: 1
2025-07-30 19:26:20.485 | INFO     | services.message_buffer_service:add_message:114 - Timer criado/resetado para 558182986181@s.whatsapp.net - Aguardando 8.0s para processar 1 mensagens
2025-07-30 19:26:20.486 | DEBUG    | services.message_buffer_service:_wait_and_process:124 - Timer iniciado para 558182986181@s.whatsapp.net - aguardando 8.0s
2025-07-30 19:26:28.486 | INFO     | services.message_buffer_service:_wait_and_process:138 - Timer expirado para 558182986181@s.whatsapp.net - iniciando processamento
2025-07-30 19:26:28.486 | INFO     | services.message_buffer_service:_process_buffer:180 - Iniciando processamento de 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-30 19:26:28.486 | DEBUG    | services.message_buffer_service:_process_buffer:196 -   Mensagem 1: sim sim... (tipo: text)
2025-07-30 19:26:28.486 | INFO     | services.message_buffer_service:_process_buffer:199 - Executando callback para processar 1 mensagens de 558182986181@s.whatsapp.net
2025-07-30 19:26:28.501 | INFO     | agents.sdr_agent:process_message:159 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:26:28.501 | INFO     | repositories.lead_repository:create_or_update:41 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:26:29.737 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:26:31.389 | INFO     | repositories.base:create:31 - Created messages record: 6bacea58-ba96-40dc-b5f0-265199a304b5
INFO:     127.0.0.1:39266 - "GET /health HTTP/1.1" 307 Temporary Redirect
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:55658 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:60798 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:27:37.290 | INFO     | repositories.base:create:31 - Created messages record: a5cb2b2f-9e8a-4e7a-89f6-8da114387a78
2025-07-30 19:27:37.882 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:27:38.695 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:27:38.913 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:27:39.129 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-30 19:27:39.130 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 4 chunks, tempo total: 50.5s
INFO:     10.11.0.4:38132 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.11.0.4:38132 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.11.0.4:38132 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:27:54.451 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-30 19:27:54.880 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:119 - Cancelados 1 follow-ups pendentes para lead 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:27:55.094 | INFO     | services.follow_up_service:create_follow_up_after_message:91 - Follow-up criado para lead 742170c7-ae11-4c45-826e-94aea4e92cff - Tipo: first_contact - Agendado para: 16:57 (30 minutos)
2025-07-30 19:27:55.094 | INFO     | services.message_buffer_service:_process_buffer:206 - Processamento concluído para 558182986181@s.whatsapp.net - 1 mensagens processadas
2025-07-30 19:27:55.094 | DEBUG    | services.message_buffer_service:_process_buffer_with_lock:168 - Flag de processamento limpa para 558182986181@s.whatsapp.net
INFO:     10.11.0.4:38132 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:27:55.757 | ERROR    | services.redis_service:connect:79 - ❌ Erro ao conectar ao Redis: ConnectionError: Error -2 connecting to redis:6379. -2.
2025-07-30 19:27:55.757 | INFO     | services.redis_service:connect:80 - 📍 URL tentada: redis://redis:6379/0
INFO:     127.0.0.1:38644 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:42300 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.11.0.4:52484 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:28:37.135 | INFO     | services.message_buffer_service:add_message:86 - Mensagem adicionada ao buffer para 558182986181@s.whatsapp.net. Total no buffer: 1
2025-07-30 19:28:37.135 | INFO     | services.message_buffer_service:add_message:114 - Timer criado/resetado para 558182986181@s.whatsapp.net - Aguardando 8.0s para processar 1 mensagens
2025-07-30 19:28:37.135 | DEBUG    | services.message_buffer_service:_wait_and_process:124 - Timer iniciado para 558182986181@s.whatsapp.net - aguardando 8.0s
2025-07-30 19:28:45.136 | INFO     | services.message_buffer_service:_wait_and_process:138 - Timer expirado para 558182986181@s.whatsapp.net - iniciando processamento
2025-07-30 19:28:45.137 | INFO     | services.message_buffer_service:_process_buffer:180 - Iniciando processamento de 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-30 19:28:45.137 | DEBUG    | services.message_buffer_service:_process_buffer:196 -   Mensagem 1: Sim, aqui está... (tipo: document)
2025-07-30 19:28:45.137 | INFO     | services.message_buffer_service:_process_buffer:199 - Executando callback para processar 1 mensagens de 558182986181@s.whatsapp.net
2025-07-30 19:28:45.154 | INFO     | agents.sdr_agent:process_message:159 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:28:45.155 | INFO     | repositories.lead_repository:create_or_update:41 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:28:45.646 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:28:46.575 | INFO     | repositories.base:create:31 - Created messages record: af9a64de-f983-4ac3-8024-e4e525c368a3
INFO:     127.0.0.1:50718 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:29:08.759 | INFO     | agents.sdr_agent:_analyze_context:635 - Mudança de estágio: IDENTIFICATION -> DISCOVERY
2025-07-30 19:29:08.759 | INFO     | agents.sdr_agent:_process_media:796 - 🎯 Processamento de mídia iniciado - Tipo: document
2025-07-30 19:29:08.759 | DEBUG    | agents.sdr_agent:_process_media:797 - Dados recebidos - Tipo: <class 'dict'>, É dict: True
2025-07-30 19:29:08.759 | INFO     | agents.sdr_agent:_process_media:801 - 📋 Dados disponíveis: ['filename', 'mimetype', 'url', 'directPath', 'mediaKey']
2025-07-30 19:29:08.759 | INFO     | agents.sdr_agent:_process_media:807 - 🔗 URL presente: https://mmg.whatsapp.net/v/t62.7119-24/29620685_12...
2025-07-30 19:29:08.759 | WARNING  | agents.sdr_agent:_process_media:810 - ⚠️ URL do WhatsApp detectada - usará conteúdo binário/base64 ao invés da URL
2025-07-30 19:29:08.760 | INFO     | agents.sdr_agent:_process_media:909 - 📄 Documento recebido - Tipo: application/pdf, Nome: Boleto.pdf
2025-07-30 19:29:08.760 | DEBUG    | agents.sdr_agent:_process_media:910 - Dados do documento: ['filename', 'mimetype', 'url', 'directPath', 'mediaKey']
2025-07-30 19:29:08.760 | INFO     | agents.sdr_agent:_process_media:913 - 📑 Iniciando processamento de PDF...
2025-07-30 19:29:08.760 | INFO     | agents.sdr_agent:_process_pdf_with_ocr:1547 - 📄 Processamento de PDF iniciado - usando Gemini 2.5 Pro nativo
2025-07-30 19:29:08.760 | DEBUG    | agents.sdr_agent:_process_pdf_with_ocr:1548 - 🔍 Dados recebidos para processamento: ['filename', 'mimetype', 'url', 'directPath', 'mediaKey']
2025-07-30 19:29:08.760 | INFO     | agents.sdr_agent:_process_pdf_with_ocr:1574 - 🌐 Baixando PDF da URL: https://mmg.whatsapp.net/v/t62.7119-24/29620685_1275903203971359_8552217368366932199_n.enc?ccb=11-4&oh=01_Q5Aa2AGcM_Vb-aL6jXLM_-8R1y0vZukp7q2NqICQyCacDwBaqA&oe=68B1EED4&_nc_sid=5e03e0&mms3=true
2025-07-30 19:29:08.766 | ERROR    | agents.sdr_agent:_process_pdf_with_ocr:1672 - ❌ Erro ao processar PDF: No module named 'aiohttp'
2025-07-30 19:29:08.766 | INFO     | agents.sdr_agent:_process_media:918 - ✅ PDF processado com sucesso. Status: error
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:54000 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:29:40.003 | INFO     | repositories.base:create:31 - Created messages record: f54781bb-1004-4f5c-ac33-3bdc61d5b9ce
2025-07-30 19:29:40.226 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:29:40.648 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:29:40.878 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:29:41.460 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-30 19:29:41.461 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 3 chunks, tempo total: 17.6s
INFO:     10.11.0.4:33444 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.11.0.4:33444 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:29:51.992 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-30 19:29:52.817 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:119 - Cancelados 1 follow-ups pendentes para lead 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:29:53.035 | INFO     | services.follow_up_service:create_follow_up_after_message:91 - Follow-up criado para lead 742170c7-ae11-4c45-826e-94aea4e92cff - Tipo: first_contact - Agendado para: 16:59 (30 minutos)
2025-07-30 19:29:53.035 | INFO     | services.message_buffer_service:_process_buffer:206 - Processamento concluído para 558182986181@s.whatsapp.net - 1 mensagens processadas
2025-07-30 19:29:53.035 | DEBUG    | services.message_buffer_service:_process_buffer_with_lock:168 - Flag de processamento limpa para 558182986181@s.whatsapp.net
INFO:     10.11.0.4:33444 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     127.0.0.1:41292 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.11.0.4:45280 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.11.0.4:45280 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.11.0.4:40588 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:30:22.181 | INFO     | services.message_buffer_service:add_message:86 - Mensagem adicionada ao buffer para 558182986181@s.whatsapp.net. Total no buffer: 1
2025-07-30 19:30:22.181 | INFO     | services.message_buffer_service:add_message:114 - Timer criado/resetado para 558182986181@s.whatsapp.net - Aguardando 8.0s para processar 1 mensagens
2025-07-30 19:30:22.182 | DEBUG    | services.message_buffer_service:_wait_and_process:124 - Timer iniciado para 558182986181@s.whatsapp.net - aguardando 8.0s
2025-07-30 19:30:30.183 | INFO     | services.message_buffer_service:_wait_and_process:138 - Timer expirado para 558182986181@s.whatsapp.net - iniciando processamento
2025-07-30 19:30:30.183 | INFO     | services.message_buffer_service:_process_buffer:180 - Iniciando processamento de 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-30 19:30:30.183 | DEBUG    | services.message_buffer_service:_process_buffer:196 -   Mensagem 1: ok... (tipo: text)
2025-07-30 19:30:30.183 | INFO     | services.message_buffer_service:_process_buffer:199 - Executando callback para processar 1 mensagens de 558182986181@s.whatsapp.net
2025-07-30 19:30:30.202 | INFO     | agents.sdr_agent:process_message:159 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:30:30.202 | INFO     | repositories.lead_repository:create_or_update:41 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:30:30.731 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:30:31.654 | INFO     | repositories.base:create:31 - Created messages record: 589f27a1-eba3-4e76-b299-0e749a2e9e73
INFO:     127.0.0.1:37934 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:30:47.339 | INFO     | agents.sdr_agent:_analyze_context:635 - Mudança de estágio: IDENTIFICATION -> DISCOVERY
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:55030 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:37632 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:31:36.082 | INFO     | repositories.base:create:31 - Created messages record: 1f48a1d5-15b9-487c-b395-5c3fc22526b4
2025-07-30 19:31:36.678 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:31:37.537 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:31:38.137 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:31:38.719 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-30 19:31:38.719 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 4 chunks, tempo total: 32.8s
INFO:     10.11.0.4:54910 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.11.0.4:54910 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.11.0.4:54910 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:31:54.023 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-30 19:31:54.459 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:119 - Cancelados 1 follow-ups pendentes para lead 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:31:54.677 | INFO     | services.follow_up_service:create_follow_up_after_message:91 - Follow-up criado para lead 742170c7-ae11-4c45-826e-94aea4e92cff - Tipo: first_contact - Agendado para: 17:01 (30 minutos)
2025-07-30 19:31:54.677 | INFO     | services.message_buffer_service:_process_buffer:206 - Processamento concluído para 558182986181@s.whatsapp.net - 1 mensagens processadas
2025-07-30 19:31:54.678 | DEBUG    | services.message_buffer_service:_process_buffer_with_lock:168 - Flag de processamento limpa para 558182986181@s.whatsapp.net
INFO:     10.11.0.4:54910 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     127.0.0.1:39726 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.11.0.4:55570 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.11.0.4:55572 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:32:08.775 | INFO     | services.message_buffer_service:add_message:86 - Mensagem adicionada ao buffer para 558182986181@s.whatsapp.net. Total no buffer: 1
2025-07-30 19:32:08.776 | INFO     | services.message_buffer_service:add_message:114 - Timer criado/resetado para 558182986181@s.whatsapp.net - Aguardando 8.0s para processar 1 mensagens
2025-07-30 19:32:08.776 | DEBUG    | services.message_buffer_service:_wait_and_process:124 - Timer iniciado para 558182986181@s.whatsapp.net - aguardando 8.0s
2025-07-30 19:32:16.776 | INFO     | services.message_buffer_service:_wait_and_process:138 - Timer expirado para 558182986181@s.whatsapp.net - iniciando processamento
2025-07-30 19:32:16.776 | INFO     | services.message_buffer_service:_process_buffer:180 - Iniciando processamento de 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-30 19:32:16.776 | DEBUG    | services.message_buffer_service:_process_buffer:196 -   Mensagem 1: consigo amanha as 15h... (tipo: text)
2025-07-30 19:32:16.776 | INFO     | services.message_buffer_service:_process_buffer:199 - Executando callback para processar 1 mensagens de 558182986181@s.whatsapp.net
2025-07-30 19:32:16.794 | INFO     | agents.sdr_agent:process_message:159 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:32:16.794 | INFO     | repositories.lead_repository:create_or_update:41 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:32:17.282 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:32:18.981 | INFO     | repositories.base:create:31 - Created messages record: 729696ed-806a-483b-a235-f4fa80af7858
2025-07-30 19:32:31.641 | INFO     | agents.sdr_agent:_analyze_context:635 - Mudança de estágio: IDENTIFICATION -> SCHEDULING
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:44112 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:32:55.784 | ERROR    | services.redis_service:connect:79 - ❌ Erro ao conectar ao Redis: ConnectionError: Error -2 connecting to redis:6379. -2.
2025-07-30 19:32:55.784 | INFO     | services.redis_service:connect:80 - 📍 URL tentada: redis://redis:6379/0
INFO:     127.0.0.1:34958 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:33:14.341 | INFO     | repositories.base:create:31 - Created messages record: a355b07d-e731-4d88-a791-f178af0b0ead
2025-07-30 19:33:14.577 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:33:15.786 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:33:16.395 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:33:17.036 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-30 19:33:17.036 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 3 chunks, tempo total: 20.8s
INFO:     10.11.0.4:37656 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.11.0.4:37656 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:33:25.723 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-30 19:33:26.175 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:119 - Cancelados 1 follow-ups pendentes para lead 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:33:26.410 | INFO     | services.follow_up_service:create_follow_up_after_message:91 - Follow-up criado para lead 742170c7-ae11-4c45-826e-94aea4e92cff - Tipo: first_contact - Agendado para: 17:03 (30 minutos)
2025-07-30 19:33:26.410 | INFO     | services.message_buffer_service:_process_buffer:206 - Processamento concluído para 558182986181@s.whatsapp.net - 1 mensagens processadas
2025-07-30 19:33:26.410 | DEBUG    | services.message_buffer_service:_process_buffer_with_lock:168 - Flag de processamento limpa para 558182986181@s.whatsapp.net
INFO:     10.11.0.4:37656 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     127.0.0.1:58090 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:56154 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:48638 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:54260 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:35:03.589 | ERROR    | api.routes.kommo_webhooks:kommo_webhook_events:88 - Erro ao processar webhook Kommo: Expecting value: line 1 column 1 (char 0)
INFO:     10.11.0.4:59926 - "POST /webhook/kommo/events HTTP/1.1" 500 Internal Server Error
INFO:     10.11.0.4:59932 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.11.0.4:56148 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: PRESENCE_UPDATE
INFO:     10.11.0.4:56148 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:35:18.713 | INFO     | services.message_buffer_service:add_message:86 - Mensagem adicionada ao buffer para 558182986181@s.whatsapp.net. Total no buffer: 1
2025-07-30 19:35:18.713 | INFO     | services.message_buffer_service:add_message:114 - Timer criado/resetado para 558182986181@s.whatsapp.net - Aguardando 8.0s para processar 1 mensagens
2025-07-30 19:35:18.713 | DEBUG    | services.message_buffer_service:_wait_and_process:124 - Timer iniciado para 558182986181@s.whatsapp.net - aguardando 8.0s
2025-07-30 19:35:26.714 | INFO     | services.message_buffer_service:_wait_and_process:138 - Timer expirado para 558182986181@s.whatsapp.net - iniciando processamento
2025-07-30 19:35:26.714 | INFO     | services.message_buffer_service:_process_buffer:180 - Iniciando processamento de 1 mensagens do buffer para 558182986181@s.whatsapp.net
2025-07-30 19:35:26.714 | DEBUG    | services.message_buffer_service:_process_buffer:196 -   Mensagem 1: ... (tipo: audio)
2025-07-30 19:35:26.714 | INFO     | services.message_buffer_service:_process_buffer:199 - Executando callback para processar 1 mensagens de 558182986181@s.whatsapp.net
2025-07-30 19:35:26.730 | INFO     | agents.sdr_agent:process_message:159 - Processando mensagem para telefone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:35:26.731 | INFO     | repositories.lead_repository:create_or_update:41 - create_or_update - phone: '558182986181@s.whatsapp.net' (tamanho: 27)
2025-07-30 19:35:28.117 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:35:30.559 | INFO     | repositories.base:create:31 - Created messages record: 121f130e-f44d-4b5a-90ce-f1ffe695a79e
INFO:     127.0.0.1:43048 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:35:44.733 | INFO     | agents.sdr_agent:_analyze_context:635 - Mudança de estágio: IDENTIFICATION -> SCHEDULING
2025-07-30 19:35:44.733 | INFO     | agents.sdr_agent:_process_media:796 - 🎯 Processamento de mídia iniciado - Tipo: audio
2025-07-30 19:35:44.734 | DEBUG    | agents.sdr_agent:_process_media:797 - Dados recebidos - Tipo: <class 'dict'>, É dict: True
2025-07-30 19:35:44.734 | INFO     | agents.sdr_agent:_process_media:801 - 📋 Dados disponíveis: ['duration', 'mimetype']
2025-07-30 19:35:44.734 | INFO     | agents.sdr_agent:_process_media:869 - 🎤 Iniciando processamento de áudio...
2025-07-30 19:35:44.734 | DEBUG    | agents.sdr_agent:_process_media:870 - Dados do áudio recebidos: type=<class 'dict'>, keys=dict_keys(['duration', 'mimetype'])
2025-07-30 19:35:44.734 | INFO     | agents.sdr_agent:_analyze_audio_with_gemini:1166 - 🎵 Iniciando análise de áudio com Gemini...
2025-07-30 19:35:44.734 | INFO     | agents.sdr_agent:_create_agno_audio:1374 - 🎵 Criando objeto Audio do AGnO...
2025-07-30 19:35:44.734 | INFO     | agents.sdr_agent:_create_agno_audio:1383 - 📦 Processando dict com keys: ['duration', 'mimetype']
2025-07-30 19:35:44.735 | ERROR    | agents.sdr_agent:_create_agno_audio:1423 - Formato de áudio não suportado: <class 'dict'>
2025-07-30 19:35:44.735 | ERROR    | agents.sdr_agent:_analyze_audio_with_gemini:1172 - ❌ Não foi possível criar objeto Audio AGnO
2025-07-30 19:35:44.735 | WARNING  | agents.sdr_agent:_process_media:890 - ❌ Não foi possível processar o áudio
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
INFO:     127.0.0.1:33098 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-30 19:36:33.312 | INFO     | repositories.base:create:31 - Created messages record: 190b74e0-7be6-4be8-a9c9-fde950504146
2025-07-30 19:36:33.547 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:36:33.990 | INFO     | repositories.base:update:100 - Updated conversations record: 5fe550ad-8d87-446f-863b-d62c7dfcbb28
2025-07-30 19:36:34.208 | INFO     | repositories.base:update:100 - Updated leads record: 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:36:34.431 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: buffered_messages_processed
2025-07-30 19:36:34.431 | INFO     | agents.tools.message_chunker_tool:chunk_message_standalone:91 - Mensagem dividida em 3 chunks, tempo total: 8.7s
INFO:     127.0.0.1:48058 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.11.0.4:51736 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     10.11.0.4:51736 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
2025-07-30 19:36:42.963 | DEBUG    | services.analytics_service:track_event:39 - Analytics event tracked: chunked_message_sent
2025-07-30 19:36:43.797 | INFO     | services.follow_up_service:_cancel_pending_follow_ups:119 - Cancelados 1 follow-ups pendentes para lead 742170c7-ae11-4c45-826e-94aea4e92cff
2025-07-30 19:36:44.021 | INFO     | services.follow_up_service:create_follow_up_after_message:91 - Follow-up criado para lead 742170c7-ae11-4c45-826e-94aea4e92cff - Tipo: first_contact - Agendado para: 17:06 (30 minutos)
2025-07-30 19:36:44.022 | INFO     | services.message_buffer_service:_process_buffer:206 - Processamento concluído para 558182986181@s.whatsapp.net - 1 mensagens processadas
2025-07-30 19:36:44.022 | DEBUG    | services.message_buffer_service:_process_buffer_with_lock:168 - Flag de processamento limpa para 558182986181@s.whatsapp.net
INFO:     10.11.0.4:51736 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
INFO:     127.0.0.1:57562 - "GET /health HTTP/1.1" 307 Temporary Redirect