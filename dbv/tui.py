import enum
import itertools
from dataclasses import dataclass
from typing import Any, Callable, Dict

import numpy as np
from dask import dataframe as dd
from rich.color import Color, parse_rgb_hex
from rich.console import Console, ConsoleOptions, ConsoleRenderable, RenderResult
from rich.layout import Layout
from rich.padding import Padding
from rich.panel import Panel
from rich.pretty import Pretty
from rich.style import Style
from rich.styled import Styled
from rich.table import Column, Table
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
        4. Add a row to Help.__rich__ for the help string
    """

    LOADING = "(L)oad"
    SUMMARY = "(s)ummary"
    TABLE = "(t)able"
    HELP = "(?)help"


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


class Help:
    """Rich-renderable command help page"""

    def __init__(self, command_dict: dict):
        self.tables = []
        for title, commands in command_dict.items():
            table = Table(
                title=title,
                expand=True,
                row_styles=[body_style, body_style_secondary],
            )
            table.add_column("Command")
            table.add_column("Short")
            table.add_column("Description")
            for key, command in commands.items():
                table.add_row(key, command.short_description, command.help)
            self.tables.append(table)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        for table in self.tables:
            yield table


class Summary:
    """Show a summary of the database"""

    # Rich-renderable summary pane for a DataFrame.

    def __init__(self, df: dd.DataFrame):
        self.df = df

    def __rich__(self) -> ConsoleRenderable:
        return Schema.from_df(self.df)


class TableView:
    """Show the database as a table"""

    # Rich-renderable summary pane for a DataFrame.

    def __init__(self, df: dd.DataFrame):
        self.df = df
        self._last_page_size = 0
        self._startat = 0
        self._column_startat = 0
        self.filter = None

    @property
    def startat(self) -> int:
        """Which row to start rendering at."""
        return self._startat

    @startat.setter
    def startat(self, startat: int) -> None:
        """Setter for startat."""
        self._startat = min(len(self.df) - 1, max(0, startat))

    @property
    def column_startat(self) -> int:
        """Which column to start rendering at."""
        return self._column_startat

    @column_startat.setter
    def column_startat(self, column_startat: int) -> None:
        """Setter for column_startat."""
        self._column_startat = min(len(self.df.columns) - 1, max(0, column_startat))

    def increment_page(self) -> None:
        """Increment startat by the last known page size."""
        self.startat += self._last_page_size

    def decrement_page(self) -> None:
        """Decrement startat by the last known page size."""
        self.startat -= self._last_page_size

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Render table dynamically based on provided space and filtering."""
        # -6 for title, header, spacers, -1 for footer
        height = options.height - 7  # could also use max_height?
        width = options.max_width - 2  # could also use min_width?

        # saved for page increment
        self._last_page_size = height

        filtered = (
            self.df
            # apply filter
            .pipe(lambda df: df if not self.filter else df[self.filter])
            # start at self.column_startat
            .pipe(lambda df: df.iloc[:, self.column_startat :])  # noqa: E203
        )
        paged = list(
            itertools.islice(filtered.itertuples(), self.startat, self.startat + height)
        )

        def format(v: any) -> ConsoleRenderable:
            return Text(v) if isinstance(v, str) else Pretty(v)

        table = Table(expand=True, row_styles=[body_style, body_style_secondary])

        # The following code computes the number of columns we can comfortable render
        # in the space, starting at self.column_startat, before finally trimming down
        # to just those columns and then rendering.
        column_names = [" ", *filtered.columns]
        columns = [
            Column(name, _cells=[format(v) for v in values])
            for name, values in zip(column_names, zip(*paged))
        ]

        column_widths = [
            table._measure_column(console, options, column) for column in columns
        ]
        # +1 for column separator
        max_column_widths = np.array([width.maximum for width in column_widths]) + 1
        total_width = np.add.accumulate(max_column_widths)
        # np.where returns tuple of list of elements for each dimension
        cant_render = np.where(total_width > width)[0]

        # cant_render[0], if it exists, is the first column indexd we don't have space for
        if cant_render.size:  # np.ndarray
            max_column = max(cant_render[0], self.column_startat + 1)
            column_names = column_names[:max_column]
            paged = [row[:max_column] for row in paged]

        for column_name in column_names:
            table.add_column(column_name)

        for row in paged:
            table.add_row(*map(format, row))

        yield table
        yield f"... {len(filtered)} total rows"


@dataclass
class Command:
    """Interface command dataclass"""

    key: str
    short_description: str
    fn: Callable
    help: str

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Call command"""
        return self.fn(*args, **kwds)


def add_command(command_dict: Dict, key: str, short_description: str) -> Callable:
    """Add a command to command_dict"""

    def decorator(fn: Callable) -> Callable:
        if key in command_dict:
            raise KeyError(f"Command {key} already exists")
        command_dict[key] = Command(key, short_description, fn, fn.__doc__)
        return fn

    return decorator


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

    commands = {}
    table_commands = {}

    def __init__(self, df: dd.DataFrame, title: str):
        self.df = df
        self.loading = "Loading..."
        self.summary = Summary(self.df)
        self.table = TableView(self.df)
        self.mode = Mode.TABLE
        self.help = Help(
            {
                "Mode Commands": self.commands,
                "Table Commands": self.table_commands,
            }
        )
        self.views = {
            Mode.LOADING: self.loading,
            Mode.SUMMARY: self.summary,
            Mode.TABLE: self.table,
            Mode.HELP: self.help,
        }

    async def keyboard_handler(self, ch: str, refresh: Callable[[], None]) -> bool:
        """This function is executed serially per input typed by the keyboard.

        It does not need to be thread safe; the keyboard event generator will not
        call it in parallel. `ch` will always have length 1.
        """
        # If the command is registered, call it
        if self.mode == Mode.TABLE:
            if ch in self.table_commands:
                return self.table_commands[ch].fn(self, refresh)

        if ch in self.commands:
            return self.commands[ch].fn(self, refresh)

        # If a command hasn't been found by this point it means there isn't one
        # defined.

        return True

    def __rich__(self) -> ConsoleRenderable:
        """Render the interface layout."""
        layout = Layout()
        layout.split(
            Layout(header, name="header", size=1),
            mode_line(self.mode),
            Layout(body, name="main"),
        )
        output = self.views[self.mode]
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

    # switch modes (TODO: input modes)
    @add_command(commands, "s", "(s)ummary")
    def summary_mode(self, refresh: Callable) -> bool:
        """Show a summary of the database"""
        self.mode = Mode.SUMMARY
        refresh()
        return True

    @add_command(commands, "t", "(t)able")
    def table_mode(self, refresh: Callable) -> bool:
        """Show the database as a table"""
        self.mode = Mode.TABLE
        refresh()
        return True

    @add_command(commands, "L", "(L)oad")
    def load_command(self, refresh: Callable) -> bool:
        """Load a database"""
        self.mode = Mode.LOADING
        refresh()
        return True

    # FIXME: If the mode is not TABLE the table still scrolls
    # TABLE MODE: table navigation (TODO: arrow keys)
    # need to figure out a better refresh option here; not refreshing feels weird
    # but refreshing on each j or k is slaggy
    @add_command(table_commands, "h", "scroll left")
    def scroll_left(self, refresh: Callable) -> bool:
        """Scroll left one column in the table view"""
        self.table.column_startat -= 1
        refresh()
        return True

    @add_command(table_commands, "j", "scroll down")
    def scroll_down(self, refresh: Callable) -> bool:
        """Scroll down one page in the table view"""
        self.table.increment_page()
        refresh()
        return True

    @add_command(table_commands, "k", "scroll up")
    def scroll_up(self, refresh: Callable) -> bool:
        """Scroll up one page in the table view"""
        self.table.decrement_page()
        refresh()
        return True

    @add_command(table_commands, "l", "scroll right")
    def scroll_right(self, refresh: Callable) -> bool:
        """Scroll right one column in the table view"""
        self.table.column_startat += 1
        refresh()
        return True

    @add_command(table_commands, "g", "Go to top")
    def go_to_top(self, refresh: Callable) -> bool:
        """Go to the top of the table"""
        self.table.startat = 0
        refresh()
        return True

    @add_command(table_commands, "G", "Go to bottom")
    def go_to_bottom(self, refresh: Callable) -> bool:
        """Go to the bottom of the table"""
        self.table.startat = len(self.df) - self.table._last_page_size
        refresh()
        return True

    # quit (TODO: if input is lagged, doesn't work)
    @add_command(commands, "q", "(q)uit")
    def quit(self, refresh: Callable) -> bool:
        """Quit"""
        return False

    @add_command(commands, "?", "help")
    def show_help(self, refresh: Callable) -> bool:
        """Show this help page"""
        self.mode = Mode.HELP
        refresh()
        return True
