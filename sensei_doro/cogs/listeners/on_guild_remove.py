import sqlite3
from contextlib import closing

from discord.ext.commands import Cog


class OnGuildRemove(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_remove(self, guild):
        """ Called when a Guild is removed from the Client. """
        # delete data
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            # search in db for guild.id
            c.execute(" DELETE FROM dojos WHERE id=:id", {"id": guild.id})
            conn.commit()
        # console info
        print(f"Guild leave :( {guild.name} )")
