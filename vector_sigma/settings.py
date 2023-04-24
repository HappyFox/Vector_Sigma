import logging
import sys


import aioconsole
import aiosqlite3

from pathlib import Path


def get_db_path():
    return Path.home() / Path("vector-sigma.db")


def get_db():
    return aiosqlite3.connect(get_db_path())


async def init():
    async with get_db() as db:
        logging.info("Initial DB table creation")
        await db.execute(
            "CREATE TABLE IF NOT EXISTS registered_numbers (phone_num TEXT);"
        )

        count = None
        async with db.execute("SELECT COUNT(*) FROM registered_numbers") as cur:
            (count,) = await cur.fetchone()
        await aioconsole.aprint(count)
        if not count:
            phone_num = await aioconsole.ainput(
                "Enter the phone number you have registered with signal-cli : "
            )

            await db.execute(
                "INSERT INTO registered_numbers(phone_num) VALUES (?)", (phone_num,)
            )
            await db.commit()
