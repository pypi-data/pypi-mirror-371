"""
Command-line user interface functions.
"""

import os
from click import ClickException


def dbse_path(name: str) -> str:
    """
    Return a database path from a custom environment variable, $XDG_CONFIG_HOME or $HOME.
    """

    if path := os.environ.get(name, None):
        return os.path.normpath(path)

    elif path := os.environ.get("XDG_CONFIG_HOME", None):
        return os.path.join(path, "sabot.db")

    elif path := os.environ.get("HOME", None):
        return os.path.join(path, ".sabot")

    else:
        raise ClickException("cannot detect database path")
