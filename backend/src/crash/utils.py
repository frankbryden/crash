from asyncio import Event, sleep
import logging


async def sleep_and_go(duration: int, event: Event):
    """Sleep for `duration` s, then fire the `event`"""
    logging.info("Start sleep")
    await sleep(duration)
    logging.info("end sleep")
    event.set()
