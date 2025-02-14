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
        # create topggpy instance
        self.topggpy = topgg.DBLClient(bot, self.dbl_token)

    @tasks.loop(minutes=30)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update the server count."""
        if self.dbl_token == "DEBUG":
            pass
        else:
            try:
                await self.topggpy.post_guild_count()
            except Exception as e:
                self.bot.log.exception("TopGGUpdate", f"Failed to post server count\n{e.__class__.__name__}: {e}")

    async def close(self) -> None:
        self.update_stats.stop()
        await self.topggpy.close()
        print("TopGGUpdate closed.")
