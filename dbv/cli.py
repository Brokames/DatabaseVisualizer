import asyncio
import sys
import tty
from typing import Optional

import click
from rich.live import Live

from dbv.df import df_to_rich_table, load_df
from dbv.tui import layout


async def consume_keyboard_events(keyboard_handler) -> None:
    """Read from stdin and execute the keyboard handler. The buffer is consumed
    serially with no regard to timing, so if `keyboard_handler` is slow it may delay
    the execution of events and feel unnaturaly.

    When `keyboard_handler` returns falsey, exit.
    """
    while ch := sys.stdin.read(1):
        should_continue = await keyboard_handler(ch)
        if not should_continue:
            break


class Interface:
    """Class maintaining state for the interface. This class coordinates the keyboard
    handler with anything else stateful that it should interact with. Trivially so far
    this is nothing; the next immediate step is for this class to own the layout object
    and mutate it based on user input."""

    async def keyboard_handler(self, ch: str) -> bool:
        """This function is executed serially per input typed by the keyboard.
        It does not need to be thread safe; the keyboard event generator will not
        call it in parallel. `ch` will always have length 1."""
        if ch == "q":
            return False
        return True


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

    with Live(layout, screen=True):
        df = load_df(filename)
        layout["main"].update(df_to_rich_table(df, title=filename))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(consume_keyboard_events(interface.keyboard_handler))


if __name__ == "__main__":
    main()
