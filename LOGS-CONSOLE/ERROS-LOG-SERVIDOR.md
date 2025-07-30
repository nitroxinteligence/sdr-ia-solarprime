2025-07-30 21:02:51.579 | INFO     | core.environment:_configure_urls:50 - 📡 Evolution API URL: http://evolution-api:8080
2025-07-30 21:02:51.580 | INFO     | core.environment:_configure_urls:51 - 💾 Redis URL: redis://redis:6379/0
2025-07-30 21:02:51.580 | INFO     | core.environment:__init__:26 - 🔧 Ambiente detectado: production
2025-07-30 21:02:51.580 | INFO     | core.environment:__init__:27 - 🐳 Docker: Sim
2025-07-30 21:02:51.583 | INFO     | services.message_buffer_service:__init__:44 - MessageBufferService iniciado - Enabled: True, Timeout: 8.0s
2025-07-30 21:02:54.640 | INFO     | agents.sdr_agent:<module>:28 - ✅ Processamento de PDFs será feito nativamente pelo Gemini 2.5 Pro
2025-07-30 21:02:54.869 | INFO     | services.database:_initialize_client:43 - ✅ Supabase client initialized successfully
2025-07-30 21:02:54.942 | INFO     | services.kommo_service:__init__:41 - ✅ KommoService inicializado com Long-Lived Token para: leonardofvieira00
Traceback (most recent call last):
  File "/home/app/.local/bin/uvicorn", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/click/core.py", line 1442, in __call__
    return self.main(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/click/core.py", line 1363, in main
    rv = self.invoke(ctx)
         ^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/click/core.py", line 794, in invoke
    return callback(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/main.py", line 410, in main
    run(
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/main.py", line 577, in run
    server.run()
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 69, in serve
    await self._serve(sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 76, in _serve
    config.load()
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/config.py", line 434, in load
    self.loaded_app = import_from_string(self.app)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/app/api/main.py", line 16, in <module>
    from api.routes import webhooks, health, instance, webhook_admin, auth, kommo_webhooks, diagnostics
  File "/app/api/routes/webhooks.py", line 17, in <module>
    from services.whatsapp_service import whatsapp_service
  File "/app/services/whatsapp_service.py", line 21, in <module>
    from agents.sdr_agent import create_sdr_agent
  File "/app/agents/sdr_agent.py", line 55, in <module>
    from services.evolution_api import evolution_api
ImportError: cannot import name 'evolution_api' from 'services.evolution_api' (/app/services/evolution_api.py)
2025-07-30 21:03:02.721 | INFO     | core.environment:_configure_urls:50 - 📡 Evolution API URL: http://evolution-api:8080
2025-07-30 21:03:02.721 | INFO     | core.environment:_configure_urls:51 - 💾 Redis URL: redis://redis:6379/0
2025-07-30 21:03:02.721 | INFO     | core.environment:__init__:26 - 🔧 Ambiente detectado: production
2025-07-30 21:03:02.721 | INFO     | core.environment:__init__:27 - 🐳 Docker: Sim
2025-07-30 21:03:02.725 | INFO     | services.message_buffer_service:__init__:44 - MessageBufferService iniciado - Enabled: True, Timeout: 8.0s
2025-07-30 21:03:05.843 | INFO     | agents.sdr_agent:<module>:28 - ✅ Processamento de PDFs será feito nativamente pelo Gemini 2.5 Pro
2025-07-30 21:03:06.076 | INFO     | services.database:_initialize_client:43 - ✅ Supabase client initialized successfully
2025-07-30 21:03:06.157 | INFO     | services.kommo_service:__init__:41 - ✅ KommoService inicializado com Long-Lived Token para: leonardofvieira00
Traceback (most recent call last):
  File "/home/app/.local/bin/uvicorn", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/click/core.py", line 1442, in __call__
    return self.main(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/click/core.py", line 1363, in main
    rv = self.invoke(ctx)
         ^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/click/core.py", line 794, in invoke
    return callback(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/main.py", line 410, in main
    run(
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/main.py", line 577, in run
    server.run()
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 69, in serve
    await self._serve(sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 76, in _serve
    config.load()
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/config.py", line 434, in load
    self.loaded_app = import_from_string(self.app)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/app/api/main.py", line 16, in <module>
    from api.routes import webhooks, health, instance, webhook_admin, auth, kommo_webhooks, diagnostics
  File "/app/api/routes/webhooks.py", line 17, in <module>
    from services.whatsapp_service import whatsapp_service
  File "/app/services/whatsapp_service.py", line 21, in <module>
    from agents.sdr_agent import create_sdr_agent
  File "/app/agents/sdr_agent.py", line 55, in <module>
    from services.evolution_api import evolution_api
ImportError: cannot import name 'evolution_api' from 'services.evolution_api' (/app/services/evolution_api.py)
