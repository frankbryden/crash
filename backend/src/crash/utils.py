import time
import asyncio
from threading import Event, Thread


def sleep_and_go(duration: int, event: Event):
    """Sleep for `duration` s, then fire the `event`"""

    def _thread_func():
        time.sleep(duration)
        event.set()

    Thread(target=_thread_func).start()


def run_async_in_thread(async_func):
    # Create a new event loop in the thread and run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_func())
