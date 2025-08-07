2025-08-07 15:23:19.048 | ERROR    | app.utils.logger:log_with_emoji:140 | ❌ Erro Supabase: Erro ao buscar estado emocional: object APIResponse[~_ReturnT] can't be used in 'await' expression | Data: {'table': 'conversations'}
2025-08-07 15:23:19.052 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Novo estágio identificado: EM_QUALIFICACAO
2025-08-07 15:23:19.277 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Lead atualizado no Supabase: {'current_stage': 'EM_QUALIFICACAO', 'updated_at': '2025-08-07T15:23:19.053214'}
2025-08-07 15:23:19.278 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 15:23:19.887 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: daf3b279-53d3-4d73-b011-9c8a7c17744c
2025-08-07 15:23:19.887 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: daf3b279-53d3-4d73-b011-9c8a7c17744c
2025-08-07 15:23:20.506 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 1 mensagens encontradas (limite solicitado: 100)
2025-08-07 15:23:20.507 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 1 mensagens disponíveis (menos que o limite de 100)
2025-08-07 15:23:20.508 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: daf3b279-53d3-4d73-b011-9c8a7c17744c
2025-08-07 15:23:20.508 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: daf3b279-53d3-4d73-b011-9c8a7c17744c
2025-08-07 15:23:20.743 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 1 mensagens encontradas (limite solicitado: 100)
2025-08-07 15:23:20.743 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 1 mensagens disponíveis (menos que o limite de 100)
2025-08-07 15:23:20.744 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 1 mensagens
2025-08-07 15:23:20.744 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 15:23:26.815 | INFO     | app.services.kommo_auto_sync:sync_new_leads:187 | 📋 1 novos leads para sincronizar com Kommo
WARNING  MemoryDb not provided.                                                 
INFO:     10.11.0.4:55402 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     127.0.0.1:49452 - "GET /health HTTP/1.1" 200 OK
2025-08-07 15:23:31.664 | INFO     | app.services.kommo_auto_sync:_sync_single_lead:235 | ✅ Lead 6b53e7d5-4cbb-48c3-be1f-4e70c5b5f326 sincronizado com Kommo (ID: 3771000)
2025-08-07 15:23:33.996 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL></RESPOSTA_FINAL>...
2025-08-07 15:23:36.043 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 1.79, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
2025-08-07 15:23:37.839 | ERROR    | app.utils.logger:log_with_emoji:140 | 🚨 Erro Evolution: Evolution API retornou erro 400: {"status":400,"error":"Bad Request","response":{"message":["Text is required"]}}
2025-08-07 15:23:37.840 | ERROR    | app.utils.logger:log_with_emoji:140 | 🚨 Erro Evolution: Erro ao enviar mensagem: Erro ao enviar mensagem: Status 400 - {"status":400,"error":"Bad Request","response":{"message":["Text is required"]}}
2025-08-07 15:23:37.840 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Evolution API: Erro ao enviar mensagem: Erro ao enviar mensagem: Status 400 - {"status":400,"error":"Bad Request","response":{"message":["Text is required"]}} | Data: {'component': 'Evolution API'}
2025-08-07 15:23:37.840 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Agent Message Processing: Erro ao enviar mensagem: Status 400 - {"status":400,"error":"Bad Request","response":{"message":["Text is required"]}} | Data: {'component': 'Agent Message Processing'}
2025-08-07 15:23:37.841 | ERROR    | app.api.webhooks:process_message_with_agent:1158 | Erro detalhado no processamento com agente:
Traceback (most recent call last):

  File "/root/.local/bin/uvicorn", line 7, in <module>
    sys.exit(main())
    │   │    └ <Command main>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 1442, in __call__
    return self.main(*args, **kwargs)
           │    │     │       └ {}
           │    │     └ ()
           │    └ <function Command.main at 0x7042970d2480>
           └ <Command main>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 1363, in main
    rv = self.invoke(ctx)
         │    │      └ <click.core.Context object at 0x704297d9a290>
         │    └ <function Command.invoke at 0x7042970d2160>
         └ <Command main>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           │   │      │    │           │   └ {'host': '0.0.0.0', 'port': 8000, 'workers': 1, 'app': 'main:app', 'uds': None, 'fd': None, 'reload': False, 'reload_dirs': (...
           │   │      │    │           └ <click.core.Context object at 0x704297d9a290>
           │   │      │    └ <function main at 0x704296cde660>
           │   │      └ <Command main>
           │   └ <function Context.invoke at 0x7042970d13a0>
           └ <click.core.Context object at 0x704297d9a290>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 794, in invoke
    return callback(*args, **kwargs)
           │         │       └ {'host': '0.0.0.0', 'port': 8000, 'workers': 1, 'app': 'main:app', 'uds': None, 'fd': None, 'reload': False, 'reload_dirs': (...
           │         └ ()
           └ <function main at 0x704296cde660>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/main.py", line 410, in main
    run(
    └ <function run at 0x7042970ef880>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/main.py", line 577, in run
    server.run()
    │      └ <function Server.run at 0x704296fc0cc0>
    └ <uvicorn.server.Server object at 0x7042970fb210>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
           │       │   │    │             └ None
           │       │   │    └ <function Server.serve at 0x704296fc0d60>
           │       │   └ <uvicorn.server.Server object at 0x7042970fb210>
           │       └ <function run at 0x704297a3cea0>
           └ <module 'asyncio' from '/usr/local/lib/python3.11/asyncio/__init__.py'>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           │      │   └ <coroutine object Server.serve at 0x704296eb75b0>
           │      └ <function Runner.run at 0x704297310cc0>
           └ <asyncio.runners.Runner object at 0x704296cef690>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           │    │     │                  └ <Task pending name='Task-1' coro=<Server.serve() running at /root/.local/lib/python3.11/site-packages/uvicorn/server.py:69> w...
           │    │     └ <cyfunction Loop.run_until_complete at 0x704296d1a260>
           │    └ <uvloop.Loop running=True closed=False debug=False>
           └ <asyncio.runners.Runner object at 0x704296cef690>

  File "/app/app/services/message_buffer.py", line 107, in _process_queue
    await self._process_messages(phone, messages)
          │    │                 │      └ [{'content': 'olá, tudo bem? quero saber mais sobre os serviços de energia solar', 'data': {'key': {'remoteJid': '55818298618...
          │    │                 └ '558182986181'
          │    └ <function MessageBuffer._process_messages at 0x704290b0f2e0>
          └ <app.services.message_buffer.MessageBuffer object at 0x70429171ce50>

  File "/app/app/services/message_buffer.py", line 159, in _process_messages
    await process_message_with_agent(
          └ <function process_message_with_agent at 0x704278f2bce0>

> File "/app/app/api/webhooks.py", line 1083, in process_message_with_agent
    result = await evolution_client.send_text_message(
                   │                └ <function EvolutionAPIClient.send_text_message at 0x70429410ab60>
                   └ <app.integrations.evolution.EvolutionAPIClient object at 0x70429410f210>

  File "/app/app/integrations/evolution.py", line 327, in send_text_message
    raise Exception(f"Erro ao enviar mensagem: Status {response.status_code} - {error_text}")

Exception: Erro ao enviar mensagem: Status 400 - {"status":400,"error":"Bad Request","response":{"message":["Text is required"]}}