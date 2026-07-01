import asyncio
import signal
import logging

from pyrogram import Client

from config import API_ID, API_HASH, BOT_TOKEN

from core.workers.download_worker import download_worker
from core.workers.encode_worker import encode_worker
from core.workers.upload_worker import upload_worker


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


shutdown_event = asyncio.Event()


async def supervise(worker, *args):

    while not shutdown_event.is_set():

        try:

            await worker(*args)

        except Exception as e:

            logging.exception(f"Worker crashed {worker.__name__}")

            await asyncio.sleep(5)


async def startup():

    app = Client(
        "bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

    await app.start()

    logging.info("Bot started")

    tasks = [

        asyncio.create_task(
            supervise(download_worker, app)
        ),

        asyncio.create_task(
            supervise(encode_worker, app)
        ),

        asyncio.create_task(
            supervise(upload_worker, app)
        )
    ]

    await shutdown_event.wait()

    for t in tasks:
        t.cancel()

    await app.stop()


def handle_shutdown():

    logging.info("Shutdown requested")

    shutdown_event.set()


def main():

    loop = asyncio.get_event_loop()

    loop.add_signal_handler(
        signal.SIGINT,
        handle_shutdown
    )

    loop.add_signal_handler(
        signal.SIGTERM,
        handle_shutdown
    )

    loop.run_until_complete(startup())


if __name__ == "__main__":

    main()