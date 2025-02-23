# Application Main
import asyncio
from dotenv import load_dotenv
import discord
import os

from . import dbm
from .clients import SenseiClient
from .cogs import (
    OnReady,
    OnVSUpdate,
    OnGuildJoin,
    OnGuildRemove,
    CommandErrHandler,
    Logging,
    TopGGUpdate,
    Create,
    Data,
    Config,
    SetRoles,
    Help,
)

load_dotenv()


async def setup_bot(bot: SenseiClient) -> None:
    # listeners
    await bot.add_cog(OnReady(bot))
    await bot.add_cog(OnVSUpdate(bot))
    await bot.add_cog(OnGuildJoin(bot))
    await bot.add_cog(OnGuildRemove(bot))
    await bot.add_cog(CommandErrHandler(bot))

    # tasks
    bot.log = Logging(bot)
    bot.topgg = TopGGUpdate(bot)
    await bot.add_cog(bot.log)
    await bot.add_cog(bot.topgg)

    # commands
    await bot.add_cog(Create(bot))
    await bot.add_cog(Data(bot))
    await bot.add_cog(Config(bot))
    await bot.add_cog(SetRoles(bot))
    bot.remove_command("help")  # overwrite
    await bot.add_cog(Help(bot))


def run() -> None:
    # database
    dbm.setup()

    # bot client
    token = os.getenv("DISCORD_TOKEN") or "0"
    shard_count = os.getenv("SHARD_COUNT") or "1"
    intents = discord.Intents.default()

    bot = SenseiClient(
        shard_count=int(shard_count), command_prefix="$", intents=intents
    )

    async def init() -> None:
        async with bot:
            await setup_bot(bot)
            await bot.start(token)

    asyncio.run(init())


if __name__ == "__main__":
    run()
