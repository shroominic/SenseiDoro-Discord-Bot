from discord.ext import commands
import logging

logger = logging.getLogger(__name__)


class OnReady(commands.Cog):
    """Handles bot startup events"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.initialized = False  # Prevent multiple initializations

    @commands.Cog.listener()
    async def on_ready(self):
        """Initialize bot when ready"""
        if self.initialized:
            return

        register_cog = self.bot.get_cog("Register")
        if register_cog:
            await register_cog.register_all_unregistered_servers()
        else:
            logger.error("Register cog not found! Server initialization skipped.")

        self.initialized = True


async def setup(bot: commands.Bot):
    await bot.add_cog(OnReady(bot))
