import os
import topgg

from dotenv import load_dotenv
from discord.ext import commands, tasks


class TopGGUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # load token from .env
        load_dotenv()
        self.dbl_token = os.getenv('TOP_GG_TOKEN')

        bot.topggpy = topgg.DBLClient(bot, self.dbl_token)

    @tasks.loop(minutes=30)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count."""
        if self.dbl_token == "DEBUG":
            print(f"DEBUG MODE: Posted server count ({self.bot.topggpy.guild_count})")
        else:
            try:
                await self.bot.topggpy.post_guild_count()
                print(f"Posted server count ({self.bot.topggpy.guild_count})")
            except Exception as e:
                print(f"Failed to post server count\n{e.__class__.__name__}: {e}")


# update_stats.start()
