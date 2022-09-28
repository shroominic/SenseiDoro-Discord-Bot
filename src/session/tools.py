import sqlite3
from contextlib import closing

from .session import Session


async def get_session_id(some_channel, dojo):
    # get session id
    session_id = some_channel.category.id
    if session_id in dojo.active_sessions:
        return session_id
    else:
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            # check if session is in database
            c.execute("SELECT * FROM sessions WHERE id=:id", {"id": session_id})
            result = c.fetchone()
            if result:
                return session_id
    return None


async def create_session_from_db(session_id, dojo):
    session = Session.from_db(session_id, dojo.bot)
    dojo.active_sessions[session_id] = session
    return session


async def get_session(some_channel, dojo):
    # get session id
    session_id = some_channel.category.id
    # if session is active
    if session_id in dojo.active_sessions:
        return dojo.active_sessions[session_id]
    else:
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            # check if session is in database
            c.execute("SELECT * FROM sessions WHERE id=:id", {"id": session_id})
            result = c.fetchone()
            if result:
                session = Session.from_db(session_id, dojo.bot)
                dojo.active_sessions[session_id] = session
                return session


