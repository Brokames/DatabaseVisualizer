import asyncio
import sys
import tty
from typing import Awaitable, Callable

import click
from rich.live import Live

from dbv.df import df_to_rich_table, load_df
from dbv.tui import Interface

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
    while ch := sys.stdin.read(1):
        should_continue = await keyboard_handler(ch, live.refresh)
        if not should_continue:
            break


@click.command()
@click.argument("filename")
def main(filename: str) -> None:
    """Startup Database Viewer

    TODO add more info to this help message
    """
    # Puts the terminal into cbreak mode, meaning keys aren't echoed to the screen
    # and can be read immediately without input buffering.
    tty.setcbreak(sys.stdin.fileno())

    interface = Interface()

    with Live(interface, screen=True) as live:
        df = load_df(filename)
        interface.set_table(df_to_rich_table(df, title=filename))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            consume_keyboard_events(interface.keyboard_handler, live)
        )


if __name__ == "__main__":
    main()
