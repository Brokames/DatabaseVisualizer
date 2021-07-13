from typing import Optional

from dask import dataframe as dd
from rich.table import Table


def load_df(filename: str) -> dd.DataFrame:
    """Load a dask DataFrame from a parquet file."""
    return dd.read_parquet(filename)


def df_to_rich_table(df: dd.DataFrame, title: Optional[str] = None) -> Table:
    """Convert a dask DataFrame to a Rich table."""
    table = Table(title=title)
    table.add_column(" ")
    for column in df.columns:
        table.add_column(column)

    for i, row in df.iterrows():
        table.add_row(*map(str, [i, *row]))

    return table
