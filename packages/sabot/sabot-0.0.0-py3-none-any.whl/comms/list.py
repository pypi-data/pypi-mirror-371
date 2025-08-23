"""
List Click command definition.
"""

import click
from sabot.comms.base import group
from sabot.items.book import Book


@group.command("list", add_help_option=False)
@click.argument("text", default="")
@click.help_option("-h", "--help")
@click.pass_obj
def list_(book: Book, text: str):
    """
    List all notes, or notes matching TEXT.
    """

    for note in book.match(text):
        click.echo(note.name)
