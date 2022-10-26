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

    @tasks.loop(minutes=30)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update the server count."""
        if self.dbl_token == "DEBUG":
            pass
        else:
            with topgg.DBLClient(self.bot, self.dbl_token) as client:
                try:
                    await self.bot.topggpy.post_guild_count()
                except Exception as e:
                    self.bot.log.exception("TopGGUpdate", f"Failed to post server count\n{e.__class__.__name__}: {e}")

    def close(self):
        self.bot.topggpy.close()
        print("TopGGUpdate closed.")