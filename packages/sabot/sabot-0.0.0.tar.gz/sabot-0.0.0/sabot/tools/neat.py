"""
Value sanitisation and conversion functions.
"""

import time as time_
from string import ascii_lowercase, digits

NAME_CHARS = ascii_lowercase + digits + "-"


def body(body: str) -> str:
    """
    Return a whitespace-trimmed body string with a trailing newline.
    """

    return body.strip() + "\n"


def name(name: str) -> str:
    """
    Return a lowercase alphanumeric-with-dashes name string.
    """

    name = name.strip().lower().replace("_", "-")
    return "".join(char for char in name if char in NAME_CHARS)


def time(unix: int) -> time_.struct_time:
    """
    Return a local time object from a Unix UTC integer.
    """

    return time_.localtime(unix)
