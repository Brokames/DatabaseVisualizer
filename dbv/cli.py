import asyncio
import sys
import tty
from typing import Awaitable, Callable

import click
from rich.live import Live

from dbv.df import load_df
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
    # stores terminal attributes to restore after closing the application
    stdin = sys.stdin.fileno()
    tattr = tty.tcgetattr(stdin)

    try:
        # Puts the terminal into cbreak mode, meaning keys aren't echoed to the screen
        # and can be read immediately without input buffering.
        tty.setcbreak(sys.stdin.fileno())

        df = load_df(filename)
        interface = Interface(df, filename)

        with Live(interface, screen=True) as live:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                consume_keyboard_events(interface.keyboard_handler, live)
            )

    finally:  # restores the terminal to default behavior
        tty.tcsetattr(stdin, tty.TCSANOW, tattr)


if __name__ == "__main__":
    main()
