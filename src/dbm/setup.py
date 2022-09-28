import sqlite3
import os
from contextlib import closing


def setup_database(db_file):
    """ some description """
    with closing(sqlite3.connect(db_file)) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS dojos (
                    id integer,
                    name text,
                    role_admin text,
                    role_mod text,
                    cfg_mute_admins integer
                    )""")
        c.execute("""CREATE TABLE IF NOT EXISTS sessions (
                    id integer,
                    name text,
                    guild_id integer,
                    info_channel_id integer,
                    lobby_channel_id integer,
                    work_time integer,
                    break_time integer,
                    repetitions integer,
                    cfg_mute_admins integer
                    )""")
        conn.commit()


def main():
    setup_database("src/dbm/sensei.db")

