from time import sleep

import click
from rich.live import Live

from tui import layout


@click.command()
def main() -> None:
    """Startup ParquetVisualizer"""
    with Live(layout, screen=True):
        while True:
            sleep(1)


if __name__ == "__main__":
    main()
