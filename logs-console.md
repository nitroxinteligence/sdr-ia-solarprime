INFO:     127.0.0.1:46442 - "GET /health HTTP/1.1" 200 OK
2025-08-03 16:44:14.636 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 4.22, 'message_length': 116, 'recipient': '558182986181', 'type': 'typing'}
2025-08-03 16:44:14.645 | ERROR    | app.utils.logger:log_with_emoji:140 | 🚨 Erro Evolution: Evolution API retornou erro 404: {"status":404,"error":"Not Found","response":{"message":["The \"sdr-ia-solarprime\" instance does not exist"]}}
2025-08-03 16:44:14.645 | ERROR    | app.utils.logger:log_with_emoji:140 | 🚨 Erro Evolution: Erro ao enviar mensagem: Erro ao enviar mensagem: Status 404 - {"status":404,"error":"Not Found","response":{"message":["The \"sdr-ia-solarprime\" instance does not exist"]}}
2025-08-03 16:44:14.646 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Evolution API: Erro ao enviar mensagem: Erro ao enviar mensagem: Status 404 - {"status":404,"error":"Not Found","response":{"message":["The \"sdr-ia-solarprime\" instance does not exist"]}} | Data: {'component': 'Evolution API'}
2025-08-03 16:44:14.646 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Webhook Message Processing: Erro ao enviar mensagem: Status 404 - {"status":404,"error":"Not Found","response":{"message":["The \"sdr-ia-solarprime\" instance does not exist"]}} | Data: {'component': 'Webhook Message Processing'}
2025-08-03 16:44:14.646 | ERROR    | app.api.webhooks:process_new_message:367 | Erro detalhado no processamento:
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
           │    └ <function Command.main at 0x7a47bd13e480>
           └ <Command main>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 1363, in main
    rv = self.invoke(ctx)
         │    │      └ <click.core.Context object at 0x7a47bde06610>
         │    └ <function Command.invoke at 0x7a47bd13e160>
         └ <Command main>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           │   │      │    │           │   └ {'host': '0.0.0.0', 'port': 8000, 'workers': 1, 'app': 'main:app', 'uds': None, 'fd': None, 'reload': False, 'reload_dirs': (...
           │   │      │    │           └ <click.core.Context object at 0x7a47bde06610>
           │   │      │    └ <function main at 0x7a47bcc38860>
           │   │      └ <Command main>
           │   └ <function Context.invoke at 0x7a47bd13d3a0>
           └ <click.core.Context object at 0x7a47bde06610>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 794, in invoke
    return callback(*args, **kwargs)
           │         │       └ {'host': '0.0.0.0', 'port': 8000, 'workers': 1, 'app': 'main:app', 'uds': None, 'fd': None, 'reload': False, 'reload_dirs': (...
           │         └ ()
           └ <function main at 0x7a47bcc38860>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/main.py", line 410, in main
    run(
    └ <function run at 0x7a47bd137880>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/main.py", line 577, in run
    server.run()
    │      └ <function Server.run at 0x7a47bd02ccc0>
    └ <uvicorn.server.Server object at 0x7a47bd2fdc90>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
           │       │   │    │             └ None
           │       │   │    └ <function Server.serve at 0x7a47bd02cd60>
           │       │   └ <uvicorn.server.Server object at 0x7a47bd2fdc90>
           │       └ <function run at 0x7a47bdaa0ea0>
           └ <module 'asyncio' from '/usr/local/lib/python3.11/asyncio/__init__.py'>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           │      │   └ <coroutine object Server.serve at 0x7a47bcf133d0>
           │      └ <function Runner.run at 0x7a47bd380cc0>
           └ <asyncio.runners.Runner object at 0x7a47bcc434d0>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           │    │     │                  └ <Task pending name='Task-1' coro=<Server.serve() running at /root/.local/lib/python3.11/site-packages/uvicorn/server.py:69> w...
           │    │     └ <cyfunction Loop.run_until_complete at 0x7a47bcc7d3c0>
           │    └ <uvloop.Loop running=True closed=False debug=False>
           └ <asyncio.runners.Runner object at 0x7a47bcc434d0>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/protocols/http/httptools_impl.py", line 399, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
                   └ <uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware object at 0x7a47b6657190>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 70, in __call__
    return await self.app(scope, receive, send)
                 │    │   │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a8194d...
                 │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
                 │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
                 │    └ <fastapi.applications.FastAPI object at 0x7a47b45e8c90>
                 └ <uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware object at 0x7a47b6657190>
  File "/root/.local/lib/python3.11/site-packages/fastapi/applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
                           │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a8194d...
                           │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
                           └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
  File "/root/.local/lib/python3.11/site-packages/starlette/applications.py", line 123, in __call__
    await self.middleware_stack(scope, receive, send)
          │    │                │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a8194d...
          │    │                │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
          │    │                └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
          │    └ <starlette.middleware.errors.ServerErrorMiddleware object at 0x7a47b45d6150>
          └ <fastapi.applications.FastAPI object at 0x7a47b45e8c90>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
          │    │   │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x7a47a816ab60>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
          │    └ <starlette.middleware.cors.CORSMiddleware object at 0x7a47abe696d0>
          └ <starlette.middleware.errors.ServerErrorMiddleware object at 0x7a47b45d6150>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
          │    │   │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x7a47a816ab60>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
          │    └ <starlette.middleware.exceptions.ExceptionMiddleware object at 0x7a47abe69490>
          └ <starlette.middleware.cors.CORSMiddleware object at 0x7a47abe696d0>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 65, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
          │                            │    │    │     │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x7a47a816ab60>
          │                            │    │    │     │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
          │                            │    │    │     └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
          │                            │    │    └ <starlette.requests.Request object at 0x7a47a8183590>
          │                            │    └ <fastapi.routing.APIRouter object at 0x7a47b4596c50>
          │                            └ <starlette.middleware.exceptions.ExceptionMiddleware object at 0x7a47abe69490>
          └ <function wrap_app_handling_exceptions at 0x7a47bbc08a40>
  File "/root/.local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
          │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x7a47a816b740>
          │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
          │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
          └ <fastapi.routing.APIRouter object at 0x7a47b4596c50>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 756, in __call__
    await self.middleware_stack(scope, receive, send)
          │    │                │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x7a47a816b740>
          │    │                │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
          │    │                └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
          │    └ <bound method Router.app of <fastapi.routing.APIRouter object at 0x7a47b4596c50>>
          └ <fastapi.routing.APIRouter object at 0x7a47b4596c50>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 776, in app
    await route.handle(scope, receive, send)
          │     │      │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x7a47a816b740>
          │     │      │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
          │     │      └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
          │     └ <function Route.handle at 0x7a47bbc0a0c0>
          └ APIRoute(path='/webhook/whatsapp/{event_type}', name='whatsapp_dynamic_webhook', methods=['POST'])
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 297, in handle
    await self.app(scope, receive, send)
          │    │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x7a47a816b740>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
          │    └ <function request_response.<locals>.app at 0x7a47abe1fe20>
          └ APIRoute(path='/webhook/whatsapp/{event_type}', name='whatsapp_dynamic_webhook', methods=['POST'])
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 77, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
          │                            │    │        │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x7a47a816b740>
          │                            │    │        │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
          │                            │    │        └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
          │                            │    └ <starlette.requests.Request object at 0x7a47abefa850>
          │                            └ <function request_response.<locals>.app.<locals>.app at 0x7a47a816b600>
          └ <function wrap_app_handling_exceptions at 0x7a47bbc08a40>
  File "/root/.local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
          │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x7a47a816b4c0>
          │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
          │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
          └ <function request_response.<locals>.app.<locals>.app at 0x7a47a816b600>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 75, in app
    await response(scope, receive, send)
          │        │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x7a47a816b4c0>
          │        │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7a47a81...
          │        └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.3.193', 8000), '...
          └ <starlette.responses.JSONResponse object at 0x7a47a8197790>
  File "/root/.local/lib/python3.11/site-packages/starlette/responses.py", line 162, in __call__
    await self.background()
          │    └ <fastapi.background.BackgroundTasks object at 0x7a47a8197090>
          └ <starlette.responses.JSONResponse object at 0x7a47a8197790>
  File "/root/.local/lib/python3.11/site-packages/starlette/background.py", line 45, in __call__
    await task()
          └ <starlette.background.BackgroundTask object at 0x7a47a8197810>
  File "/root/.local/lib/python3.11/site-packages/starlette/background.py", line 28, in __call__
    await self.func(*self.args, **self.kwargs)
          │    │     │    │       │    └ {}
          │    │     │    │       └ <starlette.background.BackgroundTask object at 0x7a47a8197810>
          │    │     │    └ ({'key': {'remoteJid': '558182986181@s.whatsapp.net', 'fromMe': False, 'id': '3A39FE9D92FD6028B404', 'senderLid': '1294720240...
          │    │     └ <starlette.background.BackgroundTask object at 0x7a47a8197810>
          │    └ <function process_new_message at 0x7a47ba600b80>
          └ <starlette.background.BackgroundTask object at 0x7a47a8197810>

> File "/app/app/api/webhooks.py", line 326, in process_new_message
    result = await evolution_client.send_text_message(
                   │                └ <function EvolutionAPIClient.send_text_message at 0x7a47ba1a6de0>
                   └ <app.integrations.evolution.EvolutionAPIClient object at 0x7a47bbd4c290>

  File "/app/app/integrations/evolution.py", line 312, in send_text_message
    raise Exception(f"Erro ao enviar mensagem: Status {response.status_code} - {error_text}")

Exception: Erro ao enviar mensagem: Status 404 - {"status":404,"error":"Not Found","response":{"message":["The \"sdr-ia-solarprime\" instance does not exist"]}}