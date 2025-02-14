# Application Main
from discord.ext.commands import AutoShardedBot
from dotenv import load_dotenv
import discord
import os

from . import dbm
from .clients import SenseiClient
from .cogs import *

load_dotenv()


def run():
    # database
    dbm.setup()

    # bot client
    token = os.getenv('DISCORD_TOKEN') or "0"
    shard_count = os.getenv('SHARD_COUNT') or "1"
    intents = discord.Intents.default()

    bot: AutoShardedBot = SenseiClient(shard_count=int(shard_count),
                                       command_prefix="$",
                                       intents=intents)

    # listeners
    bot.add_cog(OnReady(bot))
    bot.add_cog(OnVSUpdate(bot))
    bot.add_cog(OnGuildJoin(bot))
    bot.add_cog(OnGuildRemove(bot))
    bot.add_cog(CommandErrHandler(bot))

    # tasks
    bot.log = Logging(bot)
    bot.tgg = TopGGUpdate(bot)
    bot.add_cog(bot.log)
    bot.add_cog(bot.tgg)

    # commands
    bot.add_cog(Create(bot))
    bot.add_cog(Data(bot))
    bot.add_cog(Config(bot))
    bot.add_cog(SetRoles(bot))
    bot.remove_command('help')  # overwrite
    bot.add_cog(Help(bot))

    bot.run(token)


if __name__ == '__main__':
    run()
