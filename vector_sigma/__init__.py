import asyncio
import logging


import vector_sigma.settings
import vector_sigma.front_end


async def main():
    logging.info(f"DB path : {vector_sigma.settings.get_db_path()}")
    await vector_sigma.settings.init()
    await vector_sigma.front_end.init()


def run():
    # logging.basicConfig(level=logging.INFO)
    # logging.info("running!")
    # asyncio.run(main(), debug=True)

    loop = asyncio.new_event_loop()

    loop.run_until_complete(vector_sigma.settings.init())
    loop.run_until_complete(vector_sigma.front_end.init())

    try:
        loop.run_forever()
    finally:
        loop.close()
