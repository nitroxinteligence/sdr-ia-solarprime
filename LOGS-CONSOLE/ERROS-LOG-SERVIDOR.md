INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started parent process [1]
Process SpawnProcess-2:
Process SpawnProcess-1:
Traceback (most recent call last):
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
    return self.real_target(sockets)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 69, in serve
    await self._serve(sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
    return self.real_target(sockets)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 76, in _serve
    config.load()
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/config.py", line 434, in load
    self.loaded_app = import_from_string(self.app)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 69, in serve
    await self._serve(sockets)
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/server.py", line 76, in _serve
    config.load()
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/config.py", line 434, in load
    self.loaded_app = import_from_string(self.app)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/api/main.py", line 16, in <module>
    from api.routes import webhooks, health, instance, webhook_admin
  File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/api/routes/webhooks.py", line 17, in <module>
    from services.whatsapp_service import whatsapp_service
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "/app/services/whatsapp_service.py", line 20, in <module>
    from agents.sdr_agent import create_sdr_agent
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "/app/agents/sdr_agent.py", line 91
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/app/api/main.py", line 16, in <module>
    from api.routes import webhooks, health, instance, webhook_admin
    markdown=True  # Usa formatação markdown
  File "/app/api/routes/webhooks.py", line 17, in <module>
    from services.whatsapp_service import whatsapp_service
  File "/app/services/whatsapp_service.py", line 20, in <module>
    from agents.sdr_agent import create_sdr_agent
    ^^^^^^^^^^^^^
SyntaxError: keyword argument repeated: markdown
  File "/app/agents/sdr_agent.py", line 91
    markdown=True  # Usa formatação markdown
    ^^^^^^^^^^^^^
SyntaxError: keyword argument repeated: markdown
INFO:     Waiting for child process [8]
INFO:     Child process [8] died
INFO:     Waiting for child process [9]
INFO:     Child process [9] died
INFO:     Waiting for child process [9]
INFO:     Child process [9] died
Process SpawnProcess-4:
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
    return self.real_target(sockets)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
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
    from api.routes import webhooks, health, instance, webhook_admin
  File "/app/api/routes/webhooks.py", line 17, in <module>
    from services.whatsapp_service import whatsapp_service
  File "/app/services/whatsapp_service.py", line 20, in <module>
    from agents.sdr_agent import create_sdr_agent
  File "/app/agents/sdr_agent.py", line 91
    markdown=True  # Usa formatação markdown
    ^^^^^^^^^^^^^
SyntaxError: keyword argument repeated: markdown
Process SpawnProcess-3:
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
    return self.real_target(sockets)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
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
    from api.routes import webhooks, health, instance, webhook_admin
  File "/app/api/routes/webhooks.py", line 17, in <module>
    from services.whatsapp_service import whatsapp_service
  File "/app/services/whatsapp_service.py", line 20, in <module>
    from agents.sdr_agent import create_sdr_agent
  File "/app/agents/sdr_agent.py", line 91
    markdown=True  # Usa formatação markdown
    ^^^^^^^^^^^^^
SyntaxError: keyword argument repeated: markdown
Process SpawnProcess-5:
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
    return self.real_target(sockets)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
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
    from api.routes import webhooks, health, instance, webhook_admin
  File "/app/api/routes/webhooks.py", line 17, in <module>
    from services.whatsapp_service import whatsapp_service
  File "/app/services/whatsapp_service.py", line 20, in <module>
    from agents.sdr_agent import create_sdr_agent
  File "/app/agents/sdr_agent.py", line 91
    markdown=True  # Usa formatação markdown
    ^^^^^^^^^^^^^
SyntaxError: keyword argument repeated: markdown
INFO:     Waiting for child process [20]
INFO:     Child process [20] died
INFO:     Waiting for child process [23]
INFO:     Child process [23] died
INFO:     Waiting for child process [23]
INFO:     Child process [23] died
Process SpawnProcess-7:
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
    return self.real_target(sockets)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
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
    from api.routes import webhooks, health, instance, webhook_admin
  File "/app/api/routes/webhooks.py", line 17, in <module>
    from services.whatsapp_service import whatsapp_service
  File "/app/services/whatsapp_service.py", line 20, in <module>
    from agents.sdr_agent import create_sdr_agent
  File "/app/agents/sdr_agent.py", line 91
    markdown=True  # Usa formatação markdown
    ^^^^^^^^^^^^^
SyntaxError: keyword argument repeated: markdown
Process SpawnProcess-6:
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
    return self.real_target(sockets)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
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
    from api.routes import webhooks, health, instance, webhook_admin
  File "/app/api/routes/webhooks.py", line 17, in <module>
    from services.whatsapp_service import whatsapp_service
  File "/app/services/whatsapp_service.py", line 20, in <module>
    from agents.sdr_agent import create_sdr_agent
  File "/app/agents/sdr_agent.py", line 91
    markdown=True  # Usa formatação markdown
    ^^^^^^^^^^^^^
SyntaxError: keyword argument repeated: markdown
Process SpawnProcess-8:
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
    return self.real_target(sockets)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
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
    from api.routes import webhooks, health, instance, webhook_admin
  File "/app/api/routes/webhooks.py", line 17, in <module>
    from services.whatsapp_service import whatsapp_service
  File "/app/services/whatsapp_service.py", line 20, in <module>
    from agents.sdr_agent import create_sdr_agent
  File "/app/agents/sdr_agent.py", line 91
    markdown=True  # Usa formatação markdown
    ^^^^^^^^^^^^^
SyntaxError: keyword argument repeated: markdown
INFO:     Waiting for child process [33]
INFO:     Child process [33] died
INFO:     Waiting for child process [36]
INFO:     Child process [36] died
INFO:     Waiting for child process [36]
INFO:     Child process [36] died
Process SpawnProcess-10:
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
    return self.real_target(sockets)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
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
    from api.routes import webhooks, health, instance, webhook_admin
  File "/app/api/routes/webhooks.py", line 17, in <module>
    from services.whatsapp_service import whatsapp_service
  File "/app/services/whatsapp_service.py", line 20, in <module>
    from agents.sdr_agent import create_sdr_agent
  File "/app/agents/sdr_agent.py", line 91
    markdown=True  # Usa formatação markdown
    ^^^^^^^^^^^^^
SyntaxError: keyword argument repeated: markdown
Process SpawnProcess-9:
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
    return self.real_target(sockets)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
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
2025-07-30 20:31:38.229 | INFO     | workflows.follow_up_workflow:_process_pending_follow_ups:399 - Processando 1 follow-ups pendentes
2025-07-30 20:31:38.231 | ERROR    | workflows.follow_up_workflow:_process_pending_follow_ups:433 - Erro ao processar follow-ups pendentes: object generator can't be used in 'await' expression
INFO:     127.0.0.1:42540 - "GET /health HTTP/1.1" 307 Temporary Redirect