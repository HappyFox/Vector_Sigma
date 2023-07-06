"""The highest level module/object. Hooks up and exchanges messages between
lower level signal, settings and AI components.
"""

import asyncio
import logging
import pprint
import sys


import vector_sigma.signal
import vector_sigma.settings


_lines = []

STOP_MSG = "STOP_MSG"


class line:
    def __init__(self, signal_prox, phone_num):
        self.signal_prox = signal_prox
        self.phone_num = phone_num
        self.envelope_task = asyncio.create_task(self._envelope_handler())

    async def _envelope_handler(self):
        envelope_queue = self.signal_prox.register_for_msg(self.phone_num)

        envelope = await envelope_queue.get()
        while envelope is not STOP_MSG:
            logging.debug(f"Received envelope:")
            logging.debug(pprint.pformat(envelope, indent=4))

            if "dataMessage" in envelope:
                data_msg = envelope["dataMessage"]
                msg = data_msg["message"]
                msg = msg.strip()
                await self.signal_prox.send(
                    message=f"I heard you, you said '{msg}'", recipient=self.phone_num
                )

                if msg.startswith("/"):
                    await self.signal_prox.send(
                        message=f"That was a command!", recipient=self.phone_num
                    )

            envelope = await envelope_queue.get()


async def init():
    logging.debug("Starting exchange.")

    lines = await vector_sigma.settings.get_signal_lines()

    if not lines:
        print("No signal lines setup, please set them up.")
        sys.exit()

    for self_num, peer_num in lines:
        signal_prox = await vector_sigma.signal.get_num_proxy(self_num)
        _lines.append(line(signal_prox, peer_num))
