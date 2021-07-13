import enum

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


def base_layout() -> Layout:
    """Create a terminal layout split with a few different body elements."""
    layout = Layout()
    layout.split(
        Layout(header, name="header", size=1),
        Layout(name="mode_line", size=1),
        Layout(body, name="main"),
    )
    layout["main"].split_row(
        Layout(body, name="left", ratio=2),
        Layout(body, name="output", ratio=3),
    )
    layout["left"].split_column(
        Layout(body, name="options", ratio=2),
        Layout(body, name="console", ratio=3),
        Layout(body, name="input"),
    )
    return layout


class Mode(enum.Enum):
    SUMMARY = "(s)ummary"
    TABLE = "(t)able"


def mode_line(current_mode):
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
        layout = base_layout()
        self.mode_line = layout["mode_line"]
        self.set_mode(Mode.TABLE)

    def set_mode(self, mode):
        self.mode = mode
        self.mode_line.update(mode_line(mode))

    async def keyboard_handler(self, ch: str) -> bool:
        """This function is executed serially per input typed by the keyboard.

        It does not need to be thread safe; the keyboard event generator will not
        call it in parallel. `ch` will always have length 1.
        """
        if ch == "q":
            return False
        elif ch == "s":
            self.set_mode(Mode.SUMMARY)
        elif ch == "t":
            self.set_mode(Mode.TABLE)
        return True

    def __rich__(self):
        return self.layout
