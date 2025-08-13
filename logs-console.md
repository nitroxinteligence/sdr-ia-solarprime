✅ Usando variáveis de ambiente do servidor (EasyPanel)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-13 15:14:52.322 | INFO     | app.utils.logger:log_with_emoji:140 | 🚀 Iniciando SDR IA Solar Prime v0.2
2025-08-13 15:14:52.326 | INFO     | app.integrations.redis_client:connect:39 | ✅ Conectado ao Redis com sucesso! URL: redis_redis:6379
2025-08-13 15:14:52.326 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Redis pronto
2025-08-13 15:14:52.963 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Supabase pronto
2025-08-13 15:14:52.963 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buffer Inteligente inicializado (timeout=30.0s, max=10)
2025-08-13 15:14:52.963 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Buffer pronto | Data: {'timeout': '30.0s'}
2025-08-13 15:14:52.964 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Message Splitter inicializado (max=200 chars, smart=ativada)
2025-08-13 15:14:52.964 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Message Splitter pronto | Data: {'max_length': 200}
2025-08-13 15:14:52.964 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema Refatorado pronto | Data: {'modules': 'Core + Services'}
2025-08-13 15:14:52.964 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⚠️ FollowUp Executor não iniciado: cannot import name 'get_supabase_client' from 'app.database.supabase_client' (/app/app/database/supabase_client.py)
2025-08-13 15:14:52.965 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔥 Pré-aquecendo AgenticSDR (tentativa 1/3)...
2025-08-13 15:14:52.965 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Sistema: 🏗️ Criando instância singleton do AgenticSDR...
2025-08-13 15:14:52.971 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Sistema: 🚀 Inicializando AgenticSDR Modular...
2025-08-13 15:14:52.972 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-13 15:14:52.972 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-13 15:14:52.972 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': False, 'reasoning_enabled': True}
2025-08-13 15:14:52.972 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ 🎨 MultimodalProcessor habilitado pronto
2025-08-13 15:14:52.973 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ 📊 LeadManager inicializado pronto
2025-08-13 15:14:52.973 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ 🧠 ContextAnalyzer inicializado pronto
2025-08-13 15:14:52.974 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Service: 📅 Calendar Service pronto
2025-08-13 15:14:52.974 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Service: 📊 CRM Service pronto
2025-08-13 15:14:52.982 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ Service: 🔄 FollowUp Service pronto
2025-08-13 15:14:52.983 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ 🎯 TeamCoordinator inicializado pronto | Data: {'services': ['calendar', 'crm', 'followup']}
2025-08-13 15:14:52.983 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ 📊 ConversationMonitor inicializado pronto
2025-08-13 15:14:52.983 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ ConversationMonitor: Loop de monitoramento iniciado
2025-08-13 15:14:52.983 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ AgenticSDR Modular inicializado com sucesso! pronto | Data: {'modules': ['ModelManager', 'MultimodalProcessor', 'LeadManager', 'ContextAnalyzer', 'TeamCoordinator']}
2025-08-13 15:14:52.984 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Singleton AgenticSDR criado e inicializado pronto
2025-08-13 15:14:52.984 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ ✅ Nova instância do AgenticSDR criada! pronto
2025-08-13 15:14:52.984 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AgenticSDR pronto | Data: {'status': 'pré-aquecido com sucesso'}
2025-08-13 15:14:52.984 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 3000.0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:53452 - "GET /health HTTP/1.1" 200 OK
2025-08-13 15:15:02.449 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Kommo Webhook: Expecting value: line 1 column 1 (char 0) | Data: {'component': 'Kommo Webhook'}
2025-08-13 15:15:02.450 | ERROR    | app.api.webhooks:kommo_webhook:1716 | Erro detalhado no webhook Kommo:
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
           │    └ <function Command.main at 0x7348236c6480>
           └ <Command main>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 1363, in main
    rv = self.invoke(ctx)
         │    │      └ <click.core.Context object at 0x7348246c9f90>
         │    └ <function Command.invoke at 0x7348236c6160>
         └ <Command main>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           │   │      │    │           │   └ {'host': '0.0.0.0', 'port': 8000, 'workers': 1, 'app': 'main:app', 'uds': None, 'fd': None, 'reload': False, 'reload_dirs': (...
           │   │      │    │           └ <click.core.Context object at 0x7348246c9f90>
           │   │      │    └ <function main at 0x7348232c6660>
           │   │      └ <Command main>
           │   └ <function Context.invoke at 0x7348236c53a0>
           └ <click.core.Context object at 0x7348246c9f90>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 794, in invoke
    return callback(*args, **kwargs)
           │         │       └ {'host': '0.0.0.0', 'port': 8000, 'workers': 1, 'app': 'main:app', 'uds': None, 'fd': None, 'reload': False, 'reload_dirs': (...
           │         └ ()
           └ <function main at 0x7348232c6660>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/main.py", line 410, in main
    run(
    └ <function run at 0x7348236ab880>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/main.py", line 577, in run
    server.run()
    │      └ <function Server.run at 0x734823580cc0>
    └ <uvicorn.server.Server object at 0x7348236eb290>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
           │       │   │    │             └ None
           │       │   │    └ <function Server.serve at 0x734823580d60>
           │       │   └ <uvicorn.server.Server object at 0x7348236eb290>
           │       └ <function run at 0x73482435cea0>
           └ <module 'asyncio' from '/usr/local/lib/python3.11/asyncio/__init__.py'>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           │      │   └ <coroutine object Server.serve at 0x73482349f5b0>
           │      └ <function Runner.run at 0x7348238b0cc0>
           └ <asyncio.runners.Runner object at 0x7348232d37d0>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           │    │     │                  └ <Task pending name='Task-1' coro=<Server.serve() running at /root/.local/lib/python3.11/site-packages/uvicorn/server.py:69> w...
           │    │     └ <cyfunction Loop.run_until_complete at 0x7348232fe260>
           │    └ <uvloop.Loop running=True closed=False debug=False>
           └ <asyncio.runners.Runner object at 0x7348232d37d0>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/protocols/http/httptools_impl.py", line 399, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
                   └ <uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware object at 0x734802862a10>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 70, in __call__
    return await self.app(scope, receive, send)
                 │    │   │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028eb4...
                 │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
                 │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
                 │    └ <fastapi.applications.FastAPI object at 0x7348035a7550>
                 └ <uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware object at 0x734802862a10>
  File "/root/.local/lib/python3.11/site-packages/fastapi/applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
                           │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028eb4...
                           │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
                           └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
  File "/root/.local/lib/python3.11/site-packages/starlette/applications.py", line 123, in __call__
    await self.middleware_stack(scope, receive, send)
          │    │                │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028eb4...
          │    │                │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
          │    │                └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <starlette.middleware.errors.ServerErrorMiddleware object at 0x7348035a7a50>
          └ <fastapi.applications.FastAPI object at 0x7348035a7550>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
          │    │   │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x73480278a5c0>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <starlette.middleware.cors.CORSMiddleware object at 0x73481048bcd0>
          └ <starlette.middleware.errors.ServerErrorMiddleware object at 0x7348035a7a50>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
          │    │   │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x73480278a5c0>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <starlette.middleware.exceptions.ExceptionMiddleware object at 0x734805601010>
          └ <starlette.middleware.cors.CORSMiddleware object at 0x73481048bcd0>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 65, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
          │                            │    │    │     │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x73480278a5c0>
          │                            │    │    │     │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
          │                            │    │    │     └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │                            │    │    └ <starlette.requests.Request object at 0x7348029ec350>
          │                            │    └ <fastapi.routing.APIRouter object at 0x7348028f0c10>
          │                            └ <starlette.middleware.exceptions.ExceptionMiddleware object at 0x734805601010>
          └ <function wrap_app_handling_exceptions at 0x73482215a7a0>
  File "/root/.local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
          │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a0c0>
          │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
          │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          └ <fastapi.routing.APIRouter object at 0x7348028f0c10>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 756, in __call__
    await self.middleware_stack(scope, receive, send)
          │    │                │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a0c0>
          │    │                │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
          │    │                └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <bound method Router.app of <fastapi.routing.APIRouter object at 0x7348028f0c10>>
          └ <fastapi.routing.APIRouter object at 0x7348028f0c10>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 776, in app
    await route.handle(scope, receive, send)
          │     │      │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a0c0>
          │     │      │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
          │     │      └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │     └ <function Route.handle at 0x73482215be20>
          └ APIRoute(path='/webhook/kommo/events', name='kommo_webhook', methods=['POST'])
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 297, in handle
    await self.app(scope, receive, send)
          │    │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a0c0>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <function request_response.<locals>.app at 0x73480299c9a0>
          └ APIRoute(path='/webhook/kommo/events', name='kommo_webhook', methods=['POST'])
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 77, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
          │                            │    │        │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a0c0>
          │                            │    │        │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
          │                            │    │        └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │                            │    └ <starlette.requests.Request object at 0x7348029eda90>
          │                            └ <function request_response.<locals>.app.<locals>.app at 0x73480278a160>
          └ <function wrap_app_handling_exceptions at 0x73482215a7a0>
  File "/root/.local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
          │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a2a0>
          │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348028...
          │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          └ <function request_response.<locals>.app.<locals>.app at 0x73480278a160>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 72, in app
    response = await func(request)
                     │    └ <starlette.requests.Request object at 0x7348029eda90>
                     └ <function get_request_handler.<locals>.app at 0x73480299c860>
  File "/root/.local/lib/python3.11/site-packages/fastapi/routing.py", line 278, in app
    raw_response = await run_endpoint_function(
                         └ <function run_endpoint_function at 0x7348246be7a0>
  File "/root/.local/lib/python3.11/site-packages/fastapi/routing.py", line 191, in run_endpoint_function
    return await dependant.call(**values)
                 │         │      └ {'request': <starlette.requests.Request object at 0x7348029eda90>}
                 │         └ <function kommo_webhook at 0x734802976840>
                 └ <fastapi.dependencies.models.Dependant object at 0x734802a2cf50>

> File "/app/app/api/webhooks.py", line 1696, in kommo_webhook
    data = await request.json()
                 │       └ <function Request.json at 0x734822315c60>
                 └ <starlette.requests.Request object at 0x7348029eda90>

  File "/root/.local/lib/python3.11/site-packages/starlette/requests.py", line 252, in json
    self._json = json.loads(body)
    │            │    │     └ b'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofviei...
    │            │    └ <function loads at 0x7348238f5580>
    │            └ <module 'json' from '/usr/local/lib/python3.11/json/__init__.py'>
    └ <starlette.requests.Request object at 0x7348029eda90>
  File "/usr/local/lib/python3.11/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           │                │      └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
           │                └ <function JSONDecoder.decode at 0x7348238f4ea0>
           └ <json.decoder.JSONDecoder object at 0x7348238e4950>
  File "/usr/local/lib/python3.11/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               │    │          │      │  └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
               │    │          │      └ <built-in method match of re.Pattern object at 0x7348238fc450>
               │    │          └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
               │    └ <function JSONDecoder.raw_decode at 0x7348238f4f40>
               └ <json.decoder.JSONDecoder object at 0x7348238e4950>
  File "/usr/local/lib/python3.11/json/decoder.py", line 355, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
          │                                  └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
          └ <class 'json.decoder.JSONDecodeError'>

json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
INFO:     10.11.0.4:38736 - "POST /webhook/kommo/events HTTP/1.1" 500 Internal Server Error
2025-08-13 15:15:03.925 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Kommo Webhook: Expecting value: line 1 column 1 (char 0) | Data: {'component': 'Kommo Webhook'}
2025-08-13 15:15:03.925 | ERROR    | app.api.webhooks:kommo_webhook:1716 | Erro detalhado no webhook Kommo:
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
           │    └ <function Command.main at 0x7348236c6480>
           └ <Command main>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 1363, in main
    rv = self.invoke(ctx)
         │    │      └ <click.core.Context object at 0x7348246c9f90>
         │    └ <function Command.invoke at 0x7348236c6160>
         └ <Command main>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           │   │      │    │           │   └ {'host': '0.0.0.0', 'port': 8000, 'workers': 1, 'app': 'main:app', 'uds': None, 'fd': None, 'reload': False, 'reload_dirs': (...
           │   │      │    │           └ <click.core.Context object at 0x7348246c9f90>
           │   │      │    └ <function main at 0x7348232c6660>
           │   │      └ <Command main>
           │   └ <function Context.invoke at 0x7348236c53a0>
           └ <click.core.Context object at 0x7348246c9f90>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 794, in invoke
    return callback(*args, **kwargs)
           │         │       └ {'host': '0.0.0.0', 'port': 8000, 'workers': 1, 'app': 'main:app', 'uds': None, 'fd': None, 'reload': False, 'reload_dirs': (...
           │         └ ()
           └ <function main at 0x7348232c6660>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/main.py", line 410, in main
    run(
    └ <function run at 0x7348236ab880>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/main.py", line 577, in run
    server.run()
    │      └ <function Server.run at 0x734823580cc0>
    └ <uvicorn.server.Server object at 0x7348236eb290>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
           │       │   │    │             └ None
           │       │   │    └ <function Server.serve at 0x734823580d60>
           │       │   └ <uvicorn.server.Server object at 0x7348236eb290>
           │       └ <function run at 0x73482435cea0>
           └ <module 'asyncio' from '/usr/local/lib/python3.11/asyncio/__init__.py'>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           │      │   └ <coroutine object Server.serve at 0x73482349f5b0>
           │      └ <function Runner.run at 0x7348238b0cc0>
           └ <asyncio.runners.Runner object at 0x7348232d37d0>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           │    │     │                  └ <Task pending name='Task-1' coro=<Server.serve() running at /root/.local/lib/python3.11/site-packages/uvicorn/server.py:69> w...
           │    │     └ <cyfunction Loop.run_until_complete at 0x7348232fe260>
           │    └ <uvloop.Loop running=True closed=False debug=False>
           └ <asyncio.runners.Runner object at 0x7348232d37d0>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/protocols/http/httptools_impl.py", line 399, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
                   └ <uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware object at 0x734802862a10>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 70, in __call__
    return await self.app(scope, receive, send)
                 │    │   │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x734802799d...
                 │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
                 │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
                 │    └ <fastapi.applications.FastAPI object at 0x7348035a7550>
                 └ <uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware object at 0x734802862a10>
  File "/root/.local/lib/python3.11/site-packages/fastapi/applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
                           │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x734802799d...
                           │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
                           └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
  File "/root/.local/lib/python3.11/site-packages/starlette/applications.py", line 123, in __call__
    await self.middleware_stack(scope, receive, send)
          │    │                │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x734802799d...
          │    │                │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │    │                └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <starlette.middleware.errors.ServerErrorMiddleware object at 0x7348035a7a50>
          └ <fastapi.applications.FastAPI object at 0x7348035a7550>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
          │    │   │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x7348027893a0>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <starlette.middleware.cors.CORSMiddleware object at 0x73481048bcd0>
          └ <starlette.middleware.errors.ServerErrorMiddleware object at 0x7348035a7a50>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
          │    │   │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x7348027893a0>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <starlette.middleware.exceptions.ExceptionMiddleware object at 0x734805601010>
          └ <starlette.middleware.cors.CORSMiddleware object at 0x73481048bcd0>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 65, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
          │                            │    │    │     │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x7348027893a0>
          │                            │    │    │     │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │                            │    │    │     └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │                            │    │    └ <starlette.requests.Request object at 0x734802798e10>
          │                            │    └ <fastapi.routing.APIRouter object at 0x7348028f0c10>
          │                            └ <starlette.middleware.exceptions.ExceptionMiddleware object at 0x734805601010>
          └ <function wrap_app_handling_exceptions at 0x73482215a7a0>
  File "/root/.local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
          │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a2a0>
          │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          └ <fastapi.routing.APIRouter object at 0x7348028f0c10>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 756, in __call__
    await self.middleware_stack(scope, receive, send)
          │    │                │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a2a0>
          │    │                │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │    │                └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <bound method Router.app of <fastapi.routing.APIRouter object at 0x7348028f0c10>>
          └ <fastapi.routing.APIRouter object at 0x7348028f0c10>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 776, in app
    await route.handle(scope, receive, send)
          │     │      │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a2a0>
          │     │      │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │     │      └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │     └ <function Route.handle at 0x73482215be20>
          └ APIRoute(path='/webhook/kommo/events', name='kommo_webhook', methods=['POST'])
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 297, in handle
    await self.app(scope, receive, send)
          │    │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a2a0>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <function request_response.<locals>.app at 0x73480299c9a0>
          └ APIRoute(path='/webhook/kommo/events', name='kommo_webhook', methods=['POST'])
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 77, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
          │                            │    │        │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a2a0>
          │                            │    │        │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │                            │    │        └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │                            │    └ <starlette.requests.Request object at 0x73480279bf10>
          │                            └ <function request_response.<locals>.app.<locals>.app at 0x73480278a3e0>
          └ <function wrap_app_handling_exceptions at 0x73482215a7a0>
  File "/root/.local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
          │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a340>
          │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          └ <function request_response.<locals>.app.<locals>.app at 0x73480278a3e0>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 72, in app
    response = await func(request)
                     │    └ <starlette.requests.Request object at 0x73480279bf10>
                     └ <function get_request_handler.<locals>.app at 0x73480299c860>
  File "/root/.local/lib/python3.11/site-packages/fastapi/routing.py", line 278, in app
    raw_response = await run_endpoint_function(
                         └ <function run_endpoint_function at 0x7348246be7a0>
  File "/root/.local/lib/python3.11/site-packages/fastapi/routing.py", line 191, in run_endpoint_function
    return await dependant.call(**values)
                 │         │      └ {'request': <starlette.requests.Request object at 0x73480279bf10>}
                 │         └ <function kommo_webhook at 0x734802976840>
                 └ <fastapi.dependencies.models.Dependant object at 0x734802a2cf50>

> File "/app/app/api/webhooks.py", line 1696, in kommo_webhook
    data = await request.json()
                 │       └ <function Request.json at 0x734822315c60>
                 └ <starlette.requests.Request object at 0x73480279bf10>

  File "/root/.local/lib/python3.11/site-packages/starlette/requests.py", line 252, in json
    self._json = json.loads(body)
    │            │    │     └ b'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofviei...
    │            │    └ <function loads at 0x7348238f5580>
    │            └ <module 'json' from '/usr/local/lib/python3.11/json/__init__.py'>
    └ <starlette.requests.Request object at 0x73480279bf10>
  File "/usr/local/lib/python3.11/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           │                │      └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
           │                └ <function JSONDecoder.decode at 0x7348238f4ea0>
           └ <json.decoder.JSONDecoder object at 0x7348238e4950>
  File "/usr/local/lib/python3.11/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               │    │          │      │  └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
               │    │          │      └ <built-in method match of re.Pattern object at 0x7348238fc450>
               │    │          └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
               │    └ <function JSONDecoder.raw_decode at 0x7348238f4f40>
               └ <json.decoder.JSONDecoder object at 0x7348238e4950>
  File "/usr/local/lib/python3.11/json/decoder.py", line 355, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
          │                                  └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
          └ <class 'json.decoder.JSONDecodeError'>

json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
INFO:     10.11.0.4:38736 - "POST /webhook/kommo/events HTTP/1.1" 500 Internal Server Error
2025-08-13 15:15:05.943 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Kommo Webhook: Expecting value: line 1 column 1 (char 0) | Data: {'component': 'Kommo Webhook'}
2025-08-13 15:15:05.943 | ERROR    | app.api.webhooks:kommo_webhook:1716 | Erro detalhado no webhook Kommo:
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
           │    └ <function Command.main at 0x7348236c6480>
           └ <Command main>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 1363, in main
    rv = self.invoke(ctx)
         │    │      └ <click.core.Context object at 0x7348246c9f90>
         │    └ <function Command.invoke at 0x7348236c6160>
         └ <Command main>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           │   │      │    │           │   └ {'host': '0.0.0.0', 'port': 8000, 'workers': 1, 'app': 'main:app', 'uds': None, 'fd': None, 'reload': False, 'reload_dirs': (...
           │   │      │    │           └ <click.core.Context object at 0x7348246c9f90>
           │   │      │    └ <function main at 0x7348232c6660>
           │   │      └ <Command main>
           │   └ <function Context.invoke at 0x7348236c53a0>
           └ <click.core.Context object at 0x7348246c9f90>
  File "/root/.local/lib/python3.11/site-packages/click/core.py", line 794, in invoke
    return callback(*args, **kwargs)
           │         │       └ {'host': '0.0.0.0', 'port': 8000, 'workers': 1, 'app': 'main:app', 'uds': None, 'fd': None, 'reload': False, 'reload_dirs': (...
           │         └ ()
           └ <function main at 0x7348232c6660>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/main.py", line 410, in main
    run(
    └ <function run at 0x7348236ab880>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/main.py", line 577, in run
    server.run()
    │      └ <function Server.run at 0x734823580cc0>
    └ <uvicorn.server.Server object at 0x7348236eb290>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
           │       │   │    │             └ None
           │       │   │    └ <function Server.serve at 0x734823580d60>
           │       │   └ <uvicorn.server.Server object at 0x7348236eb290>
           │       └ <function run at 0x73482435cea0>
           └ <module 'asyncio' from '/usr/local/lib/python3.11/asyncio/__init__.py'>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           │      │   └ <coroutine object Server.serve at 0x73482349f5b0>
           │      └ <function Runner.run at 0x7348238b0cc0>
           └ <asyncio.runners.Runner object at 0x7348232d37d0>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           │    │     │                  └ <Task pending name='Task-1' coro=<Server.serve() running at /root/.local/lib/python3.11/site-packages/uvicorn/server.py:69> w...
           │    │     └ <cyfunction Loop.run_until_complete at 0x7348232fe260>
           │    └ <uvloop.Loop running=True closed=False debug=False>
           └ <asyncio.runners.Runner object at 0x7348232d37d0>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/protocols/http/httptools_impl.py", line 399, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
                   └ <uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware object at 0x734802862a10>
  File "/root/.local/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 70, in __call__
    return await self.app(scope, receive, send)
                 │    │   │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027b47...
                 │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
                 │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
                 │    └ <fastapi.applications.FastAPI object at 0x7348035a7550>
                 └ <uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware object at 0x734802862a10>
  File "/root/.local/lib/python3.11/site-packages/fastapi/applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
                           │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027b47...
                           │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
                           └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
  File "/root/.local/lib/python3.11/site-packages/starlette/applications.py", line 123, in __call__
    await self.middleware_stack(scope, receive, send)
          │    │                │      │        └ <bound method RequestResponseCycle.send of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027b47...
          │    │                │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │    │                └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <starlette.middleware.errors.ServerErrorMiddleware object at 0x7348035a7a50>
          └ <fastapi.applications.FastAPI object at 0x7348035a7550>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
          │    │   │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x73480278a3e0>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <starlette.middleware.cors.CORSMiddleware object at 0x73481048bcd0>
          └ <starlette.middleware.errors.ServerErrorMiddleware object at 0x7348035a7a50>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
          │    │   │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x73480278a3e0>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <starlette.middleware.exceptions.ExceptionMiddleware object at 0x734805601010>
          └ <starlette.middleware.cors.CORSMiddleware object at 0x73481048bcd0>
  File "/root/.local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 65, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
          │                            │    │    │     │      │        └ <function ServerErrorMiddleware.__call__.<locals>._send at 0x73480278a3e0>
          │                            │    │    │     │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │                            │    │    │     └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │                            │    │    └ <starlette.requests.Request object at 0x734802798fd0>
          │                            │    └ <fastapi.routing.APIRouter object at 0x7348028f0c10>
          │                            └ <starlette.middleware.exceptions.ExceptionMiddleware object at 0x734805601010>
          └ <function wrap_app_handling_exceptions at 0x73482215a7a0>
  File "/root/.local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
          │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a340>
          │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          └ <fastapi.routing.APIRouter object at 0x7348028f0c10>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 756, in __call__
    await self.middleware_stack(scope, receive, send)
          │    │                │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a340>
          │    │                │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │    │                └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <bound method Router.app of <fastapi.routing.APIRouter object at 0x7348028f0c10>>
          └ <fastapi.routing.APIRouter object at 0x7348028f0c10>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 776, in app
    await route.handle(scope, receive, send)
          │     │      │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a340>
          │     │      │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │     │      └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │     └ <function Route.handle at 0x73482215be20>
          └ APIRoute(path='/webhook/kommo/events', name='kommo_webhook', methods=['POST'])
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 297, in handle
    await self.app(scope, receive, send)
          │    │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a340>
          │    │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │    │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │    └ <function request_response.<locals>.app at 0x73480299c9a0>
          └ APIRoute(path='/webhook/kommo/events', name='kommo_webhook', methods=['POST'])
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 77, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
          │                            │    │        │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278a340>
          │                            │    │        │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │                            │    │        └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          │                            │    └ <starlette.requests.Request object at 0x73480279a310>
          │                            └ <function request_response.<locals>.app.<locals>.app at 0x73480278aa20>
          └ <function wrap_app_handling_exceptions at 0x73482215a7a0>
  File "/root/.local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
          │   │      │        └ <function wrap_app_handling_exceptions.<locals>.wrapped_app.<locals>.sender at 0x73480278ac00>
          │   │      └ <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.httptools_impl.RequestResponseCycle object at 0x7348027...
          │   └ {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.4'}, 'http_version': '1.1', 'server': ('10.11.5.55', 8000), 'c...
          └ <function request_response.<locals>.app.<locals>.app at 0x73480278aa20>
  File "/root/.local/lib/python3.11/site-packages/starlette/routing.py", line 72, in app
    response = await func(request)
                     │    └ <starlette.requests.Request object at 0x73480279a310>
                     └ <function get_request_handler.<locals>.app at 0x73480299c860>
  File "/root/.local/lib/python3.11/site-packages/fastapi/routing.py", line 278, in app
    raw_response = await run_endpoint_function(
                         └ <function run_endpoint_function at 0x7348246be7a0>
  File "/root/.local/lib/python3.11/site-packages/fastapi/routing.py", line 191, in run_endpoint_function
    return await dependant.call(**values)
                 │         │      └ {'request': <starlette.requests.Request object at 0x73480279a310>}
                 │         └ <function kommo_webhook at 0x734802976840>
                 └ <fastapi.dependencies.models.Dependant object at 0x734802a2cf50>

> File "/app/app/api/webhooks.py", line 1696, in kommo_webhook
    data = await request.json()
                 │       └ <function Request.json at 0x734822315c60>
                 └ <starlette.requests.Request object at 0x73480279a310>

  File "/root/.local/lib/python3.11/site-packages/starlette/requests.py", line 252, in json
    self._json = json.loads(body)
    │            │    │     └ b'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofviei...
    │            │    └ <function loads at 0x7348238f5580>
    │            └ <module 'json' from '/usr/local/lib/python3.11/json/__init__.py'>
    └ <starlette.requests.Request object at 0x73480279a310>
  File "/usr/local/lib/python3.11/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           │                │      └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
           │                └ <function JSONDecoder.decode at 0x7348238f4ea0>
           └ <json.decoder.JSONDecoder object at 0x7348238e4950>
  File "/usr/local/lib/python3.11/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               │    │          │      │  └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
               │    │          │      └ <built-in method match of re.Pattern object at 0x7348238fc450>
               │    │          └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
               │    └ <function JSONDecoder.raw_decode at 0x7348238f4f40>
               └ <json.decoder.JSONDecoder object at 0x7348238e4950>
  File "/usr/local/lib/python3.11/json/decoder.py", line 355, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
          │                                  └ 'account%5Bsubdomain%5D=leonardofvieira00&account%5Bid%5D=34932776&account%5B_links%5D%5Bself%5D=https%3A%2F%2Fleonardofvieir...
          └ <class 'json.decoder.JSONDecodeError'>

json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
INFO:     10.11.0.4:38736 - "POST /webhook/kommo/events HTTP/1.1" 500 Internal Server Error