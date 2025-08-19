Discord Token: SET

2025-08-19 23:31:15,172 - WARNING - PyNaCl is not installed, voice will NOT be supported

2025-08-19 23:31:15,172 - INFO - Enhanced bot initialized with configuration for: soccer, mlb

2025-08-19 23:31:15,174 - INFO - logging in using static token

2025-08-19 23:31:15,515 - INFO - Setting up enhanced bot...

2025-08-19 23:31:15,583 - INFO - Loading sport handlers...

2025-08-19 23:31:15,589 - INFO - Loaded sport handler: soccer

2025-08-19 23:31:15,593 - INFO - Loaded sport handler: mlb

2025-08-19 23:31:15,593 - INFO - Sport manager loaded with 2 sports: soccer, mlb

2025-08-19 23:31:15,593 - ERROR - Bot failed to start: property 'choices' of 'Parameter' object has no setter

Traceback (most recent call last):

  File "/app/sports_discord_bot.py", line 447, in <module>

    asyncio.run(run_bot())

  File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run

    return runner.run(main)

           ^^^^^^^^^^^^^^^^

  File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run

    return self._loop.run_until_complete(task)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

 

  File "/root/.nix-profile/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete

    return future.result()

           ^^^^^^^^^^^^^^^

  File "/app/sports_discord_bot.py", line 433, in run_bot

    await bot.start(bot.config.discord_token)

  File "/opt/venv/lib/python3.12/site-packages/discord/client.py", line 846, in start

    await self.login(token)

  File "/opt/venv/lib/python3.12/site-packages/discord/client.py", line 689, in login

    await self.setup_hook()

  File "/app/sports_discord_bot.py", line 72, in setup_hook

    self._update_command_choices()

  File "/app/sports_discord_bot.py", line 108, in _update_command_choices

    param.choices = sport_choices

    ^^^^^^^^^^^^^

AttributeError: property 'choices' of 'Parameter' object has no setter

2025-08-19 23:31:15,652 - ERROR - Unclosed connector

connections: ['deque([(<aiohttp.client_proto.ResponseHandler object at 0x7fb13e576e70>, 9192712.535307545)])']

connector: <aiohttp.connector.TCPConnector object at 0x7fb13e773ec0>

Starting Enhanced Sports Discord Bot v2.0

Discord Token: SET

2025-08-19 23:31:18,105 - WARNING - PyNaCl is not installed, voice will NOT be supported

2025-08-19 23:31:18,106 - INFO - Enhanced bot initialized with configuration for: soccer, mlb

2025-08-19 23:31:18,108 - INFO - logging in using static token

2025-08-19 23:31:18,433 - INFO - Setting up enhanced bot...

2025-08-19 23:31:18,505 - INFO - Loading sport handlers...

2025-08-19 23:31:18,513 - INFO - Loaded sport handler: soccer

2025-08-19 23:31:18,517 - INFO - Loaded sport handler: mlb

2025-08-19 23:31:18,518 - INFO - Sport manager loaded with 2 sports: soccer, mlb

2025-08-19 23:31:18,518 - ERROR - Bot failed to start: property 'choices' of 'Parameter' object has no setter

Traceback (most recent call last):

  File "/app/sports_discord_bot.py", line 447, in <module>

    asyncio.run(run_bot())

  File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run

    return runner.run(main)

           ^^^^^^^^^^^^^^^^

  File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run

    return self._loop.run_until_complete(task)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/root/.nix-profile/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete

    return future.result()

           ^^^^^^^^^^^^^^^

  File "/app/sports_discord_bot.py", line 433, in run_bot

    await bot.start(bot.config.discord_token)

  File "/opt/venv/lib/python3.12/site-packages/discord/client.py", line 846, in start[stage-0  9/10] RUN printf '\nPATH=/opt/venv/bin:$PATH' >> /root/.profile

[stage-0  9/10] RUN printf '\nPATH=/opt/venv/bin:$PATH' >> /root/.profile  ✔ 109 ms

[stage-0 10/10] COPY . /app

[stage-0 10/10] COPY . /app  ✔ 23 ms

[auth] sharing credentials for production-us-east4-eqdc4a.railway-registry.com

[auth] sharing credentials for production-us-east4-eqdc4a.railway-registry.com  ✔ 0 ms

importing to docker

importing to docker  ✔ 11 sec

=== Successfully Built! ===

Run:

docker run -it production-us-east4-eqdc4a.railway-registry.com/b85f0795-6086-4394-91bf-210a596d3426:9e5485b0-9176-472b-9dbc-baec86efe408

Build time: 24.02 seconds

====================

Starting Healthcheck

====================

Path: /health

Retry window: 5m0s

Attempt #1 failed with service unavailable. Continuing to retry for 4m58s

Attempt #2 failed with service unavailable. Continuing to retry for 4m55s

Attempt #3 failed with service unavailable. Continuing to retry for 4m43s

Attempt #4 failed with service unavailable. Continuing to retry for 4m37s

Attempt #5 failed with service unavailable. Continuing to retry for 4m28s

Attempt #6 failed with service unavailable. Continuing to retry for 4m12s