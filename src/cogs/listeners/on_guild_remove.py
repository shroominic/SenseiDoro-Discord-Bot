import sqlite3
from contextlib import closing

from discord.ext.commands import Cog

from src.dojo import Dojo


class OnGuildRemove(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_remove(self, guild):
        """ Called when a Guild is removed from the Client. """

        # console info
        print(f"{guild.name} no longer wants me :(")
