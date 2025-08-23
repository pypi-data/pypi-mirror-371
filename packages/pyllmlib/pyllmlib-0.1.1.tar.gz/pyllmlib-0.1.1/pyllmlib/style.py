from rich.console import Console
from rich.markdown import Markdown


def style(text, console=None):
    """
    Style text as markdown in the terminal and print it.

    Args:
        text (str): The text to style (markdown format)
        console (Console, optional): Rich Console instance. If None, creates a default one.
    """
    if console is None:
        console = Console()

    markdown = Markdown(text)
    console.print(markdown)