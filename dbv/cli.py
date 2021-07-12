from time import sleep

import click
from rich.live import Live

from dbv.tui import layout
from dbv.df import load_df, df_to_rich_table


@click.command()
@click.argument("filename")
def main(filename) -> None:
    """Startup Database Viewer

    TODO add more info to this help message
    """
    with Live(layout, screen=True):
        df = load_df(filename)
        layout["main"].update(df_to_rich_table(df, title=filename))
        while True:
            sleep(1)


if __name__ == "__main__":
    main()
