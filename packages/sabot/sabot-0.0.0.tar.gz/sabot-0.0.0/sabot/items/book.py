"""
Class definition for 'Book'.
"""

import sqlite3
from sabot import tools
from sabot.items.note import Note
from typing_extensions import Iterator


class Book:
    """
    A single database containing Notes and Pages.
    """

    __slots__ = ("dbse", "path")

    def __init__(self, path: str):
        """
        Initialise the Book, executing default pragma on a successful connection and
        default schema if the resulting database has none defined.
        """

        self.dbse = sqlite3.connect(path)
        self.path = path
        self.dbse.row_factory = sqlite3.Row
        self.dbse.executescript(tools.sqls.PRAGMA)

        code = "select count(*) from SQLITE_SCHEMA"
        drow = self.dbse.execute(code).fetchone()
        if drow["count(*)"] == 0:
            self.dbse.executescript(tools.sqls.SCHEMA)

    def __eq__(self, book: object) -> bool:
        """
        Return True if the Book is equal to another Book.
        """

        if isinstance(book, Book):
            return self.path == book.path
        else:
            return NotImplemented

    def __repr__(self) -> str:
        """
        Return the Book as a code-representative string.
        """

        return f"Book({self.path!r})"

    def create(self, name: str) -> Note:
        """
        Create and return a new Note in the Book.
        """

        name = tools.neat.name(name)
        code = "insert into Notes (name) values (?)"
        curs = self.dbse.execute(code, [name])
        self.dbse.commit()
        return Note(self.dbse, curs.lastrowid or -1)

    def get(self, name: str) -> Note | None:
        """
        Return an existing Note from the Book by name.
        """

        name = tools.neat.name(name)
        code = "select n_id from Notes where name=?"
        if drow := self.dbse.execute(code, [name]).fetchone():
            return Note(self.dbse, drow["n_id"])
        else:
            return None

    def match(self, name: str) -> Iterator[Note]:
        """
        Yield every Note in the Book with a name containing a substring.
        """

        name = "%" + tools.neat.name(name) + "%"
        code = "select n_id from Notes where name like ? order by name asc"
        for drow in self.dbse.execute(code, [name]):
            yield Note(self.dbse, drow["n_id"])
