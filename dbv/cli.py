import asyncio
from typing import Awaitable, Callable

import click
import rich.traceback
from rich.live import Live

from dbv.df import load_df
from dbv.get_char import cbreak, get_char
from dbv.tui import Interface

rich.traceback.install()

RefreshCallback = Callable[[], None]
KeyboardHandler = Callable[[str, RefreshCallback], Awaitable[bool]]


async def consume_keyboard_events(
    keyboard_handler: KeyboardHandler, live: Live
) -> None:
    """Read from stdin and execute the keyboard handler.

    The buffer is consumed serially with no regard to timing, so if `keyboard_handler`
    is slow it may delay the execution of events and feel unnaturaly.

    When `keyboard_handler` returns falsey, exit.
    """
    while ch := get_char():
        should_continue = await keyboard_handler(ch, live.refresh)
        if not should_continue:
            break


@click.command()
@click.argument("filename")
def main(filename: str) -> None:
    """Startup Database Viewer

    TODO add more info to this help message
    """
    df = load_df(filename)

    interface = Interface(df, filename)

    with cbreak():
        with Live(interface, screen=True) as live:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                consume_keyboard_events(interface.keyboard_handler, live)
            )


if __name__ == "__main__":
    main()
