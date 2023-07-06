import asyncio
import logging


import vector_sigma.settings
import vector_sigma.signal
import vector_sigma.exchange


async def main():
    logging.info("Startup")
    await vector_sigma.settings.init()
    await vector_sigma.signal.init()

    await vector_sigma.exchange.init()


def run():
    logging.basicConfig(level=logging.DEBUG)
    logging.info("running!")

    loop = asyncio.new_event_loop()

    loop.run_until_complete(vector_sigma.settings.init())
    loop.run_until_complete(vector_sigma.signal.init())
    loop.run_until_complete(vector_sigma.exchange.init())

    try:
        loop.run_forever()
    finally:
        loop.close()
