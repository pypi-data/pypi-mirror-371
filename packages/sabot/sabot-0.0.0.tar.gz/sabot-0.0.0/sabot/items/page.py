"""
Class definition for 'Page'.
"""

import sqlite3
import time
from sabot import tools


class Page:
    """
    A single historical version of a recorded Note.
    """

    __slots__ = ("dbse", "p_id")

    def __init__(self, dbse: sqlite3.Connection, p_id: int):
        """
        Initialise the Page.
        """

        self.dbse = dbse
        self.p_id = p_id

    def __eq__(self, page: object) -> bool:
        """
        Return True if the Page is equal to another Page.
        """

        if isinstance(page, Page):
            return self.dbse == page.dbse and self.p_id == page.p_id
        else:
            return NotImplemented

    def __repr__(self) -> str:
        """
        Return the Page as a code-representative string.
        """

        return f"Page({self.dbse!r}, {self.p_id!r})"

    def __str__(self) -> str:
        """
        Return the Page as a descriptive string.
        """

        return self.body

    @property
    def body(self) -> str:
        """
        Return the Page's body as a string.
        """

        code = "select body from Pages where p_id=?"
        drow = self.dbse.execute(code, [self.p_id]).fetchone()
        return tools.neat.body(drow["body"])

    @property
    def init(self) -> time.struct_time:
        """
        Return the Page's creation time as a local time object.
        """

        code = "select init from Pages where p_id=?"
        drow = self.dbse.execute(code, [self.p_id]).fetchone()
        return tools.neat.time(drow["init"])

    @property
    def note(self) -> int:
        """
        Return the Page's parent Note ID as an integer.
        """

        code = "select note from Pages where p_id=?"
        drow = self.dbse.execute(code, [self.p_id]).fetchone()
        return drow["note"]

    def delete(self):
        """
        Delete the Page.
        """

        code = "delete from Pages where p_id=?"
        self.dbse.execute(code, [self.p_id])
        self.dbse.commit()

    def exists(self) -> bool:
        """
        Return True if the Page exists.
        """

        code = "select exists(select 1 from Pages where p_id=?) as exst"
        drow = self.dbse.execute(code, [self.p_id]).fetchone()
        return drow["exst"]
