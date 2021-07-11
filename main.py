import click
from rich.panel import Panel

from console import console


@click.command()
def main() -> None:
    """Startup ParquetVisualizer"""
    console.print(Panel("Hello, Pangolins!"))


if __name__ == "__main__":
    main()
