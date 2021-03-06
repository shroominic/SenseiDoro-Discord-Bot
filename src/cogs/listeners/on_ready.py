import sqlite3
from contextlib import closing
from discord.ext.commands import Cog

from src.dojo import Dojo


class OnReady(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        """
        Called when the client is done preparing the data received from Discord.
        Usually after login is successful and the Client.guilds and co. are filled up.
        """
        # delete all data from unused guilds
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM dojos")
            result = [id_tuple[0] for id_tuple in c.fetchall()]
            active_guild_ids = [guild.id for guild in self.bot.guilds]

            unused_guilds = list(set(result) - set(active_guild_ids))
            print(unused_guilds, "not active anymore, will get deleted")
            for guild_id in unused_guilds:
                c.execute("DELETE FROM dojos WHERE id=:id", {"id": guild_id})
            conn.commit()

        # create dojo instances for all active guilds
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            for guild in self.bot.guilds:
                # search in db for guild.id
                c.execute("SELECT * FROM dojos WHERE id=:id", {"id": guild.id})
                result = c.fetchone()
                # instantiate dojo from db entry
                if result:
                    dojo = Dojo.from_db(guild, self.bot, result[2], result[3], result[4])
                    self.bot.dojos[guild.id] = dojo
                # create new dojo (uncommon)
                else:
                    dojo = Dojo.new_db_entry(guild, self.bot, c)
                    self.bot.dojos[guild.id] = dojo
            conn.commit()

        # print all connected guilds
        all_guilds = [guild.name for guild in self.bot.guilds]
        print(f'{self.bot.user} is ready and connected to the following guilds: \n{all_guilds}')

        # update top.gg
        self.bot.tgg.update_stats.start()

