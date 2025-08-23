"""
Class definition for 'Note'.
"""

import sqlite3
import time
from sabot import tools
from sabot.items.page import Page


class Note:
    """
    A single recorded Note with multiple historical versions.
    """

    __slots__ = ("dbse", "n_id")

    def __init__(self, dbse: sqlite3.Connection, n_id: int):
        """
        Initialise the Note.
        """

        self.dbse = dbse
        self.n_id = n_id

    def __eq__(self, note: object) -> bool:
        """
        Return True if the Note is equal to another Note.
        """

        if isinstance(note, Note):
            return self.dbse == note.dbse and self.n_id == note.n_id
        else:
            return NotImplemented

    def __repr__(self) -> str:
        """
        Return the Note as a code-representative string.
        """

        return f"Note({self.dbse!r}, {self.n_id!r})"

    def __str__(self) -> str:
        """
        Return the Note as a descriptive string.
        """

        return self.name

    @property
    def init(self) -> time.struct_time:
        """
        Return the Note's creation time as a local time object.
        """

        code = "select init from Notes where n_id=?"
        drow = self.dbse.execute(code, [self.n_id]).fetchone()
        return tools.neat.time(drow["init"])

    @property
    def name(self) -> str:
        """
        Return the Note's name as a string.
        """

        code = "select name from Notes where n_id=?"
        drow = self.dbse.execute(code, [self.n_id]).fetchone()
        return tools.neat.name(drow["name"])

    def delete(self):
        """
        Delete the Note.
        """

        code = "delete from Notes where n_id=?"
        self.dbse.execute(code, [self.n_id])
        self.dbse.commit()

    def exists(self) -> bool:
        """
        Return True if the Note exists.
        """

        code = "select exists(select 1 from Notes where n_id=?) as exst"
        drow = self.dbse.execute(code, [self.n_id]).fetchone()
        return drow["exst"]

    def latest(self) -> Page:
        """
        Return the Note's latest Page.
        """

        code = "select p_id from Pages where note=? order by p_id desc"
        drow = self.dbse.execute(code, [self.n_id]).fetchone()
        return Page(self.dbse, drow["p_id"])

    def update(self, body: str) -> Page:
        """
        Create and return a new Page for the Note.
        """

        body = tools.neat.body(body)
        code = "insert into Pages (note, body) values (?, ?)"
        curs = self.dbse.execute(code, [self.n_id, body])
        self.dbse.commit()
        return Page(self.dbse, curs.lastrowid or -1)
