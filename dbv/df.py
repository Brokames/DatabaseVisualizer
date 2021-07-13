from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
from dask import dataframe as dd
from rich.console import Console, ConsoleOptions, RenderResult
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


@dataclass
class Schema:
    """Class for storing and rendering a table schema.

    For now column type is simply a dtype. Since parquet supports nested schemas with
    thrift types, this could be expanded to instead render with rich.tree.Tree and
    to be thrift-type aware.
    """

    columns: Dict[str, np.dtype]

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Control Rich rendering of the schema."""
        table = Table(title="schema")
        table.add_column("column")
        table.add_column("dtype")
        for column, dtype in self.columns.items():
            table.add_row(column, str(dtype))
        yield table


def df_schema(df: dd.DataFrame) -> Schema:
    """Construct a table schema from a dataframe."""
    return Schema({col: getattr(df, col).dtype for col in df.columns})
