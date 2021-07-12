from time import sleep

import click
from rich.live import Live

from dbv.tui import layout


@click.command()
def main() -> None:
    """Startup Database Viewer

    TODO add more info to this help message
    """
    with Live(layout, screen=True):
        while True:
            sleep(1)


if __name__ == "__main__":
    main()
