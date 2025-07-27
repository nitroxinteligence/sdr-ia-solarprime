INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started parent process [1]
Process SpawnProcess-2:
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
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
    raise exc from None
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
  File "/app/agents/sdr_agent.py", line 29, in <module>
    from utils.helpers import calculate_typing_delay, format_phone_number
  File "/app/utils/helpers.py", line 11, in <module>
    import pytz
ModuleNotFoundError: No module named 'pytz'
Process SpawnProcess-1:
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
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
    raise exc from None
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
  File "/app/agents/sdr_agent.py", line 29, in <module>
    from utils.helpers import calculate_typing_delay, format_phone_number
  File "/app/utils/helpers.py", line 11, in <module>
    import pytz
ModuleNotFoundError: No module named 'pytz'
INFO:     Waiting for child process [9]
INFO:     Child process [9] died
INFO:     Waiting for child process [8]
INFO:     Child process [8] died
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
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
    raise exc from None
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
  File "/app/agents/sdr_agent.py", line 29, in <module>
    from utils.helpers import calculate_typing_delay, format_phone_number
  File "/app/utils/helpers.py", line 11, in <module>
    import pytz
ModuleNotFoundError: No module named 'pytz'
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
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
    raise exc from None
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
  File "/app/agents/sdr_agent.py", line 29, in <module>
    from utils.helpers import calculate_typing_delay, format_phone_number
  File "/app/utils/helpers.py", line 11, in <module>
    import pytz
ModuleNotFoundError: No module named 'pytz'
INFO:     Waiting for child process [19]
INFO:     Child process [19] died
INFO:     Waiting for child process [21]
INFO:     Child process [21] died
INFO:     Waiting for child process [21]
INFO:     Child process [21] died
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
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
    raise exc from None
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
  File "/app/agents/sdr_agent.py", line 29, in <module>
    from utils.helpers import calculate_typing_delay, format_phone_number
  File "/app/utils/helpers.py", line 11, in <module>
    import pytz
ModuleNotFoundError: No module named 'pytz'
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
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
    raise exc from None
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
  File "/app/agents/sdr_agent.py", line 29, in <module>
    from utils.helpers import calculate_typing_delay, format_phone_number
  File "/app/utils/helpers.py", line 11, in <module>
    import pytz
ModuleNotFoundError: No module named 'pytz'
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
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
    raise exc from None
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
  File "/app/agents/sdr_agent.py", line 29, in <module>
    from utils.helpers import calculate_typing_delay, format_phone_number
  File "/app/utils/helpers.py", line 11, in <module>
    import pytz
ModuleNotFoundError: No module named 'pytz'
INFO:     Waiting for child process [38]
INFO:     Child process [38] died
INFO:     Waiting for child process [41]
INFO:     Child process [41] died
INFO:     Waiting for child process [41]
INFO:     Child process [41] died
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
  File "/home/app/.local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
    raise exc from None
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
  File "/app/agents/sdr_agent.py", line 29, in <module>
    from utils.helpers import calculate_typing_delay, format_phone_number
  File "/app/utils/helpers.py", line 11, in <module>
    import pytz
ModuleNotFoundError: No module named 'pytz'
Process SpawnProcess-9:
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started parent process [1]
2025-07-27 21:11:01.300 | INFO     | services.database:_initialize_client:43 - ✅ Supabase client initialized successfully
2025-07-27 21:11:01.347 | INFO     | agents.sdr_agent:__init__:65 - SDR Agent 'Luna' inicializado com AGnO Framework
2025-07-27 21:11:01.348 | WARNING  | services.redis_fallback:__init__:19 - ⚠️ Usando cache em memória (Redis não disponível)
INFO:     Started server process [9]
INFO:     Waiting for application startup.
2025-07-27 21:11:01.484 | INFO     | services.database:_initialize_client:43 - ✅ Supabase client initialized successfully
2025-07-27 21:11:01.532 | INFO     | agents.sdr_agent:__init__:65 - SDR Agent 'Luna' inicializado com AGnO Framework
2025-07-27 21:11:01.532 | WARNING  | services.redis_fallback:__init__:19 - ⚠️ Usando cache em memória (Redis não disponível)
INFO:     Started server process [8]
INFO:     Waiting for application startup.
2025-07-27 21:11:03.479 | INFO     | services.connection_monitor:start:61 - 🔍 Monitor de conexão WhatsApp iniciado
INFO:     Application startup complete.
2025-07-27 21:11:03.486 | INFO     | services.connection_monitor:_handle_state_change:167 - 📱 WhatsApp mudou de unknown para connected
2025-07-27 21:11:03.598 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:11:03.598 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:11:03.598 | INFO     | services.redis_fallback:_try_redis_connection:108 - ✅ Conectado ao Redis
2025-07-27 21:11:03.600 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:11:03.600 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:11:03.600 | ERROR    | services.redis_service:set:125 - Erro ao salvar no cache: 'NoneType' object has no attribute 'setex'
2025-07-27 21:11:03.644 | INFO     | services.connection_monitor:start:61 - 🔍 Monitor de conexão WhatsApp iniciado
INFO:     Application startup complete.
2025-07-27 21:11:03.650 | INFO     | services.connection_monitor:_handle_state_change:167 - 📱 WhatsApp mudou de unknown para connected
2025-07-27 21:11:03.656 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:11:03.656 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:11:03.656 | INFO     | services.redis_fallback:_try_redis_connection:108 - ✅ Conectado ao Redis
2025-07-27 21:11:03.657 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:11:03.658 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:11:03.658 | ERROR    | services.redis_service:set:125 - Erro ao salvar no cache: 'NoneType' object has no attribute 'setex'
INFO:     127.0.0.1:47206 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.0.1.4:53780 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: presence.update
INFO:     10.0.1.4:53780 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: messages.upsert
INFO:     127.0.0.1:43628 - "GET /health HTTP/1.1" 307 Temporary Redirect
2025-07-27 21:12:03.611 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:12:03.611 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:12:03.611 | ERROR    | services.redis_service:set:125 - Erro ao salvar no cache: 'NoneType' object has no attribute 'setex'
2025-07-27 21:12:03.667 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:12:03.667 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:12:03.667 | ERROR    | services.redis_service:set:125 - Erro ao salvar no cache: 'NoneType' object has no attribute 'setex'
INFO:     127.0.0.1:39780 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:51508 - "GET /health HTTP/1.1" 307 Temporary Redirect
INFO:     10.0.1.4:52842 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: presence.update
INFO:     10.0.1.4:52842 - "POST /webhook/whatsapp HTTP/1.1" 200 OK
Evento não tratado: messages.upsert
2025-07-27 21:13:03.622 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:13:03.622 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:13:03.622 | ERROR    | services.redis_service:set:125 - Erro ao salvar no cache: 'NoneType' object has no attribute 'setex'
2025-07-27 21:13:03.679 | ERROR    | services.redis_service:connect:57 - ❌ Erro ao conectar ao Redis: Error -2 connecting to redis:6379. -2.
2025-07-27 21:13:03.679 | INFO     | services.redis_service:connect:58 - 🔄 Usando fallback em memória para cache
2025-07-27 21:13:03.679 | ERROR    | services.redis_service:set:125 - Erro ao salvar no cache: 'NoneType' object has no attribute 'setex'
INFO:     127.0.0.1:36100 - "GET /health HTTP/1.1" 307 Temporary Redirect