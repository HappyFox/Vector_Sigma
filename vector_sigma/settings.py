import logging
import sys


import aiosqlite3

from pathlib import Path


def get_db_path():
    return Path.home() / Path("vector-sigma.db")


def get_db():
    return aiosqlite3.connect(get_db_path())


async def init():
    async with get_db() as db:
        logging.info("Initial DB table creation")
        await db.execute("CREATE TABLE IF NOT EXISTS settings (phone_num TEXT);")

        async with db.execute("SELECT COUNT(*) FROM settings") as cur:
            (count,) = await cur.fetchone()

            if not count:
                print(
                    "No phone number associated to a character. Run vector-sigma-add to add one."
                )
                sys.exit(1)
