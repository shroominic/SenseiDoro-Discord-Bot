import asyncio
import logging
from pathlib import Path

import discord
from discord.ext import commands
from watchfiles import awatch

from .db import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def reload_cog(bot: commands.Bot, cog_name: str) -> None:
    """Reload a specific cog"""
    try:
        await bot.reload_extension(f"senseidoro.cogs.{cog_name}")
        logger.info(f"🔄 Reloaded {cog_name}")
        await bot.tree.sync()
        logger.info("✅ Synced commands")
    except Exception as e:
        logger.error(f"❌ Error reloading {cog_name}: {e}")


async def watch_cogs(bot: commands.Bot):
    """Watch for changes in cog files and reload them"""
    cogs_path = Path(__file__).parent / "cogs"
    async for changes in awatch(cogs_path):
        for change in changes:
            changed_file = Path(change[1])
            if changed_file.suffix == ".py" and not changed_file.name.startswith("__"):
                cog_name = changed_file.stem
                await reload_cog(bot, cog_name)


@bot.event
async def setup_hook() -> None:
    await init_db()

    for cog in [
        "senseidoro.cogs.onboarding",
        "senseidoro.cogs.admin",
        "senseidoro.cogs.create_session",
        "senseidoro.cogs.register_old_servers",
        "senseidoro.cogs.session_listener",
    ]:
        await bot.load_extension(cog)
    await bot.tree.sync()

    # Start the file watcher
    asyncio.create_task(watch_cogs(bot))
