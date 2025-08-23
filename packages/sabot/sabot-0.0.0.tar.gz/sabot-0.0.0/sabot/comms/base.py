"""
Base Click group definition.
"""

import click
from sabot import VERSION_TEXT, tools
from sabot.items.book import Book


@click.group("sabot", add_help_option=False)
@click.pass_context
@click.help_option("-h", "--help")
@click.version_option("", "-v", "--version", message=VERSION_TEXT)
def group(ctxt: click.Context):
    """
    Sabot: a sharp note-taking database in Python.
    """

    if not ctxt.obj:
        path = tools.clui.dbse_path("SABOT_DB")
        ctxt.obj = Book(path)
