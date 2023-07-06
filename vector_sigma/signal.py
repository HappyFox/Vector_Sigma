import asyncio
import functools
import json
import logging
import pprint
import dataclasses

_running_proxies = {}


async def init():
    logging.debug("Starting signal")


class BadJsonCall(Exception):
    pass


async def get_num_proxy(account_num):
    if account_num in _running_proxies:
        return _running_proxies[account_num]

    proxy = SignalProxy(account_num)
    await proxy.start()

    _running_proxies[account_num] = proxy

    return proxy


class SignalProxy:
    @dataclasses.dataclass
    class FnCallRecord:
        completed: asyncio.Event = dataclasses.field(default_factory=asyncio.Event)
        result: dict = None
        error: dict = None

    def __init__(self, account_num):
        self._account_num = account_num
        self._proc = None
        self._listening_task = None

        self._registered_receivers = {}
        self._in_progress_calls = {}

        self._current_id = 0

    async def start(self):
        self._proc = await asyncio.create_subprocess_exec(
            "signal-cli",
            "-u",
            self._account_num,
            "jsonRpc",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        self._listening_task = asyncio.create_task(self._listen_fn())

    async def stop(self):
        self._proc.terminate()
        await self._listening_task

    async def _listen_fn(self):
        msg_bytes = await self._proc.stdout.readline()
        while msg_bytes != b"":
            msg_json = json.loads(msg_bytes)
            logging.debug(pprint.pformat(msg_json, indent=4))

            if "id" in msg_json:
                call_record = self._in_progress_calls[msg_json["id"]]

                if "result" in msg_json:
                    call_record.result = msg_json["result"]
                elif "error" in msg_json:
                    call_record.error = msg_json["error"]

                call_record.completed.set()

                del self._in_progress_calls[msg_json["id"]]

            elif msg_json["method"] == "receive":
                params = msg_json["params"]
                envelope = params["envelope"]
                logging.info(f"From number:{envelope['source']}")
                source_num = envelope["sourceNumber"]
                if source_num in self._registered_receivers:
                    try:
                        self._registered_receivers[source_num].put_nowait(envelope)
                    except asyncio.QueueFull:
                        pass  # add logging.

            msg_bytes = await self._proc.stdout.readline()

    def register_for_msg(self, number, queue=None):
        if not queue:
            queue = asyncio.Queue()
        self._registered_receivers[number] = queue
        return queue

    def __getattr__(self, name):
        return functools.partial(self._delegate_coroutine, name)

    def _get_id(self):
        self._current_id = (self._current_id + 1) % 2**32
        return str(self._current_id)

    async def _delegate_coroutine(self, method, **kwargs):
        id_ = self._get_id()
        call_record = SignalProxy.FnCallRecord()
        logging.debug(f"addig {call_record} to in progress calls.")
        self._in_progress_calls[id_] = call_record

        request = {"jsonrpc": "2.0", "method": method, "id": str(id_)}

        if kwargs:
            request["params"] = kwargs

        json_str = json.dumps(request) + "\n"
        json_bytes = json_str.encode("UTF-8")

        self._proc.stdin.write(json_bytes)
        await self._proc.stdin.drain()

        await call_record.completed.wait()

        # This can be improved.
        if call_record.error:
            raise BadJsonCall(call_record.error["message"])

        return call_record.result["results"]
