import sqlite3
import os
from contextlib import closing


def setup_database(db_file):
    """ some description """
    with closing(sqlite3.connect(db_file)) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE dojos (
                    id integer,
                    name text,
                    role_admin text,
                    role_mod text,
                    cfg_mute_admins integer
                    )""")
        conn.commit()


def main():
    if "sensei.db" not in os.listdir("src/dbm"):
        print("Create new database: sensei.db")
        setup_database("src/dbm/sensei.db")
    else:
        print("Found database: sensei.db")


if __name__ == '__main__':
    main()
