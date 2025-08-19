2025-08-19 23:23:21,906 - WARNING - PyNaCl is not installed, voice will NOT be supported

Starting Simple Sports Discord Bot

Discord Token: SET

2025-08-19 23:23:21,909 - INFO - logging in using static token

INFO:     Started server process [1]

INFO:     Waiting for application startup.

INFO:     Application startup complete.

INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)

INFO:     100.64.0.2:39197 - "GET /health HTTP/1.1" 200 OK

2025-08-19 23:23:22,462 - INFO - Shard ID None has connected to Gateway (Session ID: 4ba8eee7834d6ed333cd003d98208f36).

2025-08-19 23:23:24,474 - INFO - Bot ready: SportsBot#7289

2025-08-19 23:23:24,628 - INFO - Synced 2 commands

2025-08-19 23:24:14,998 - INFO - Clear channels command used by fostersfreebies for sport: soccer

2025-08-19 23:24:15,235 - INFO - 🗑️ Attempting to delete 4 channels from Soccer...

2025-08-19 23:24:15,235 - INFO - 🔄 Deleting channel 1/4: osasuna-vs-real-madri

2025-08-19 23:24:15,377 - INFO - ✅ Successfully deleted: osasuna-vs-real-madri

2025-08-19 23:24:15,878 - INFO - 🔄 Deleting channel 2/4: club-brugg-vs-rangers

2025-08-19 23:24:16,004 - INFO - ✅ Successfully deleted: club-brugg-vs-rangers

2025-08-19 23:24:16,505 - INFO - 🔄 Deleting channel 3/4: qarabag-vs-ferencvaro

2025-08-19 23:24:16,690 - INFO - ✅ Successfully deleted: qarabag-vs-ferencvaro

2025-08-19 23:24:17,191 - INFO - 🔄 Deleting channel 4/4: pafos-vs-red-star-b

2025-08-19 23:24:17,346 - INFO - ✅ Successfully deleted: pafos-vs-red-star-b

2025-08-19 23:24:17,848 - INFO - 🏁 Deletion complete: 4/4 successful

2025-08-19 23:24:18,008 - ERROR - Error in clear-channels command: 400 Bad Request (error code: 10003): Unknown Channel

2025-08-19 23:24:18,081 - ERROR - Ignoring exception in command 'clear-channels'

Traceback (most recent call last):

  File "/app/sports_discord_bot.py", line 218, in clear_channels

    await interaction.followup.send(embed=result_embed)

  File "/opt/venv/lib/python3.12/site-packages/discord/webhook/async_.py", line 1904, in send

    data = await adapter.execute_webhook(

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/opt/venv/lib/python3.12/site-packages/discord/webhook/async_.py", line 226, in request

    raise HTTPException(response, data)

discord.errors.HTTPException: 400 Bad Request (error code: 10003): Unknown Channel

 

During handling of the above exception, another exception occurred:

 

Traceback (most recent call last):

  File "/opt/venv/lib/python3.12/site-packages/discord/app_commands/commands.py", line 859, in _do_call

    return await self._callback(interaction, **params)  # type: ignore

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/app/sports_discord_bot.py", line 223, in clear_channels

    await interaction.followup.send(f"❌ Error clearing channels: {str(e)}")

  File "/opt/venv/lib/python3.12/site-packages/discord/webhook/async_.py", line 1904, in send

    data = await adapter.execute_webhook(

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/opt/venv/lib/python3.12/site-packages/discord/webhook/async_.py", line 226, in request

    raise HTTPException(response, data)

discord.errors.HTTPException: 400 Bad Request (error code: 10003): Unknown Channel

 

The above exception was the direct cause of the following exception:

 

Traceback (most recent call last):

  File "/opt/venv/lib/python3.12/site-packages/discord/app_commands/tree.py", line 1310, in _call

    await command._invoke_with_namespace(interaction, namespace)

  File "/opt/venv/lib/python3.12/site-packages/discord/app_commands/commands.py", line 884, in _invoke_with_namespace

    return await self._do_call(interaction, transformed_values)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/opt/venv/lib/python3.12/site-packages/discord/app_commands/commands.py", line 877, in _do_call

    raise CommandInvokeError(self, e) from e

discord.app_commands.errors.CommandInvokeError: Command 'clear-channels' raised an exception: HTTPException: 400 Bad Request (error code: 10003): Unknown Channel