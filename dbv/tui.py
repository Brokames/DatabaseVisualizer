import enum
import itertools
from typing import Callable

from dask import dataframe as dd
from rich.color import Color, parse_rgb_hex
from rich.console import (
    Console, ConsoleOptions, ConsoleRenderable, RenderResult
)
from rich.layout import Layout
from rich.padding import Padding
from rich.panel import Panel
from rich.pretty import Pretty
from rich.style import Style
from rich.styled import Styled
from rich.table import Table
from rich.text import Text

from dbv.df import Schema

bg_color = Color.from_triplet(parse_rgb_hex("1D1F21"))
bg_color_secondary = Color.from_triplet(parse_rgb_hex("101214"))
fg_color = Color.from_triplet(parse_rgb_hex("C5C8C6"))
yellow = Color.from_triplet(parse_rgb_hex("F0C674"))

header_style = Style(color=yellow, bgcolor=bg_color, bold=True)
header = Text("Database Viewer", justify="center", style=header_style)

body_style = Style(color=fg_color, bgcolor=bg_color)
body_style_secondary = Style(color=fg_color, bgcolor=bg_color_secondary)
body = Panel("Hello Pangolins!", style=body_style)


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


class Summary:
    """Rich-renderable summary pane for a DataFrame."""

    def __init__(self, df: dd.DataFrame):
        self.df = df

    def __rich__(self) -> ConsoleRenderable:
        return Schema.from_df(self.df)


class TableView:
    """Rich-renderable summary pane for a DataFrame."""

    def __init__(self, df: dd.DataFrame):
        self.df = df
        self.startat = 0
        self.filter = None

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Render table dynamically based on provided space and filtering."""
        # -6 for title, header, spacers
        height = options.height - 7  # could also use max_height?
        # width = options.max_width  # could also use min_width?

        filtered = self.df.pipe(lambda df: df if not self.filter else df[self.filter])
        paged = itertools.islice(
            filtered.itertuples(), self.startat, self.startat + height
        )

        table = Table(expand=True, row_styles=[body_style, body_style_secondary])
        table.add_column(" ")
        for column in filtered.columns:
            table.add_column(column)

        def format(v: any) -> ConsoleRenderable:
            return Text(v) if isinstance(v, str) else Pretty(v)

        for row in paged:
            table.add_row(*map(format, row))

        yield table
        yield f"... {len(filtered)} total rows"


class Interface:
    """Class maintaining state for the interface.

    This class coordinates the keyboard handler with anything else stateful that it
    should interact with. It has a __rich__ method which controls how the entire
    interface is rendered.

    We need Interface to know about the df so it _can_ rerender the table if it wants,
    for instance to filter to specific rows or columns; however we also don't want
    Interface to become a big blob where we throw all of the code. Ideally Interface
    should be a "controller" and should dole out responsibility of rendering to others.
    """

    def __init__(self, df: dd.DataFrame, title: str):
        self.df = df
        self.summary = Summary(self.df)
        self.table = TableView(self.df)
        self.mode = Mode.TABLE

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

    def __rich__(self) -> ConsoleRenderable:
        """Render the interface layout."""
        layout = Layout()
        layout.split(
            Layout(header, name="header", size=1),
            mode_line(self.mode),
            Layout(body, name="main"),
        )
        output = self.table if self.mode == Mode.TABLE else self.summary
        padded_output = Styled(Padding(output, (1, 2)), body_style)

        layout["main"].split_row(
            Layout(body, name="left", ratio=2),
            Layout(padded_output, name="output", ratio=3),
        )
        layout["left"].split_column(
            Layout(body, name="options", ratio=2),
            Layout(body, name="console", ratio=3),
            Layout(body, name="input"),
        )
        return layout
