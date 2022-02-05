import sqlite3
from contextlib import closing

from discord.ext.commands import Cog

from src.dojo import Dojo


class OnGuildJoin(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_join(self, guild):
        """
        Called when a Guild is either created by the Client
        or when the Client joins a guild.

        Creates a new dojo instance and adds it to the dojo dictionary.
        """
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            # search in db for guild.id
            c.execute(" SELECT * FROM dojos WHERE id=:id", {"id": guild.id})
            result = c.fetchone()
            # instantiate dojo from db entry (if guild already exists in db)
            if result:
                dojo = Dojo.from_db(guild, self.bot, result[2], result[3], result[4])
                self.bot.dojos[guild.id] = dojo
            # create new dojo
            else:
                dojo = Dojo.new_db_entry(guild, self.bot, c)
                conn.commit()
                self.bot.dojos[guild.id] = dojo

        # console info
        print(f"New guild: {guild.name}, {guild.id}")
