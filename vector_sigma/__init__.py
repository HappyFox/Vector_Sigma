import asyncio
import logging


import vector_sigma.settings


async def main():
    logging.info(f"DB path : {vector_sigma.settings.get_db_path()}")
    await vector_sigma.settings.init()


def run():
    logging.basicConfig(level=logging.INFO)
    logging.info("running!")
    asyncio.run(main(), debug=True)
