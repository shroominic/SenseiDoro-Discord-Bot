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
        dojo = Dojo(guild=guild, bot=self.bot)
        self.bot.dojos[guild.id] = dojo
        # console info
        print(f"New guild: {guild.name}, {guild.id}")
