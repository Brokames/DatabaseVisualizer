from time import sleep

import click
from rich.live import Live

from dbv.df import df_to_rich_table, load_df
from dbv.tui import layout


@click.command()
@click.argument("filename")
def main(filename: str) -> None:
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
