import enum
from typing import Callable

import rich
from rich.color import Color, parse_rgb_hex
from rich.layout import Layout
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

bg_color = Color.from_triplet(parse_rgb_hex("1D1F21"))
fg_color = Color.from_triplet(parse_rgb_hex("C5C8C6"))
yellow = Color.from_triplet(parse_rgb_hex("F0C674"))

header_style = Style(color=yellow, bgcolor=bg_color, bold=True,)
header = Text("Database Viewer", justify="center", style=header_style,)

body_style = Style(color=fg_color, bgcolor=bg_color,)
body = Panel("Hello Pangolins!", style=body_style,)


class Mode(enum.Enum):
    """Mode enum for the interface.

    Modes specified here are shown as options in the modeline; add more modes by
        1. add an element here
        2. add a keyboard shortcut to switch to the mode in keyboard_handler
        3. update __rich__ to change rendering based on the mode.
    """
    SUMMARY = "(s)ummary"
    TABLE = "(t)able"


def mode_line(current_mode: Mode) -> Layout:
    """Render the UI mode line."""
    line = Layout(name="mode_line", size=1)

    inactive_style = "green on blue"
    active_style = "bold blue on white"

    line.split_row(
        *(
            Text(
                mode.value,
                justify="center",
                style=active_style if mode == current_mode else inactive_style,
            )
            for mode in Mode
        )
    )

    return line


class Interface:
    """Class maintaining state for the interface.

    This class coordinates the keyboard handler with anything else stateful that it
    should interact with. Trivially so far this is nothing; the next immediate step
    is for this class to own the layout object and mutate it based on user input.
    """

    def __init__(self):
        self.table = None
        self.mode = Mode.TABLE

    def set_table(self, table: rich.table.Table) -> None:
        """Record the rendered table for the interface.

        For now setting as a table directly because we don't want to recompute
        the rich.table.Table on each refresh. However, we need a better separation
        of concerns here. We want Interface to know about the df so it _can_
        rerender the table if it wants, for instance to filter to specific rows
        or columns; however we also don't want Interface to become a big blob
        where we throw all of the code. Ideally Interface should be a "controller"
        and should dole out responsibility of rendering to others.
        """
        self.table = table
        self.table.style = body_style

    async def keyboard_handler(self, ch: str, refresh: Callable[[], None]) -> bool:
        """This function is executed serially per input typed by the keyboard.

        It does not need to be thread safe; the keyboard event generator will not
        call it in parallel. `ch` will always have length 1.
        """
        if ch == "q":
            return False
        elif ch == "s":
            self.mode = Mode.SUMMARY
            refresh()
        elif ch == "t":
            self.mode = Mode.TABLE
            refresh()
        return True

    def __rich__(self) -> Layout:
        """Render the interface layout."""
        layout = Layout()
        layout.split(
            Layout(header, name="header", size=1),
            mode_line(self.mode),
            Layout(body, name="main"),
        )
        output = self.table if self.mode == Mode.TABLE else Text("SUMMARY HOORAY")

        layout["main"].split_row(
            Layout(body, name="left", ratio=2), Layout(output, name="output", ratio=3),
        )
        layout["left"].split_column(
            Layout(body, name="options", ratio=2),
            Layout(body, name="console", ratio=3),
            Layout(body, name="input"),
        )
        return layout
