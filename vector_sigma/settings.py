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
    logging.debug("Starting settings")

    async with get_db() as db:
        logging.info("Initial DB table creation")
        await db.execute(
            "CREATE TABLE IF NOT EXISTS registered_lines (account_num TEXT, user_num TEXT);"
        )

        count = None
        async with db.execute("SELECT COUNT(*) FROM registered_lines") as cur:
            (count,) = await cur.fetchone()
        # await aioconsole.aprint(count)
        if not count:
            account_num = await aioconsole.ainput(
                "Enter the phone number you have registered with signal-cli : "
            )

            user_num = await aioconsole.ainput(
                "Enter the number you will message the bots from :"
            )

            await db.execute(
                "INSERT INTO registered_lines(account_num, user_num ) VALUES (?, ?)",
                (account_num, user_num),
            )

            await db.commit()


async def get_signal_lines():
    async with get_db() as db:
        async with db.execute(
            "SELECT account_num, user_num FROM registered_lines"
        ) as cur:
            numbers = await cur.fetchall()
    return numbers
