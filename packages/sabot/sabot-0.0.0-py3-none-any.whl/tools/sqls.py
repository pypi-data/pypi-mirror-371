"""
SQLite pragma and schema constants.
"""

PRAGMA = """
    pragma encoding = 'utf-8';
    pragma foreign_keys = on;
"""

SCHEMA = """
    create table Notes (
        n_id integer primary key asc,
        init integer not null default (unixepoch()),
        name text    not null unique
    );

    create table Pages (
        p_id integer primary key asc,
        init integer not null default (unixepoch()),
        note integer not null,
        body text    not null,

        foreign key (note) references Notes(n_id) on delete cascade
    );
"""
