from asyncio import Event, sleep, create_task
import logging


async def background_sleep_and_go(duration: int, event: Event):
    create_task(sleep_and_go(duration, event))


async def sleep_and_go(duration: int, event: Event):
    """Sleep for `duration` s, then fire the `event`"""
    logging.info("Start sleep")
    await sleep(duration)
    logging.info("end sleep")
    event.set()
