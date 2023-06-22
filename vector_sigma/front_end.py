import asyncio
import json
import logging
import pprint

import vector_sigma.settings

pp = pprint.PrettyPrinter(indent=4)

_proc = None

_running_task = None
_listening_task = None
_registered_listeners = []

_stop_event = asyncio.Event()


async def init():
    global _proc
    global _listening_task
    global _stop_task

    lines = await vector_sigma.settings.get_signal_lines()
    for account_num, user_num in lines:
        _proc = await asyncio.create_subprocess_exec(
            "signal-cli",
            "-u",
            account_num,
            "jsonRpc",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        _listening_task = asyncio.create_task(_listening_fn(_proc.stdout, user_num))


async def _listening_fn(stdout, user_num):
    msg_bytes = await stdout.readline()
    while msg_bytes != b"":
        breakpoint()
        msg_json = json.loads(msg_bytes)
        pp.pprint(msg_json)

        if msg_json["method"] == "receive":
            from_account = msg_json["params"]["account"]
            envelope = msg_json["params"]["envelope"]
            if from_account == user_num:
                print(f"From number:{envelope['source']}")
        msg_bytes = await stdout.readline()
        breakpoint()

    print("connection lost.")
