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

layout = Layout()
layout.split(
    Layout(header, name="header", size=1), Layout(body, name="main"),
)
