# Application Main

from dotenv import load_dotenv
import discord
import os

import dbm
from clients import SenseiClient
from cogs import *


def run():
    # load token from .env
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN') or "0"
    shard_count = os.getenv('SHARD_COUNT') or "1"

    # client can see all users
    intents = discord.Intents.default()

    # init database
    dbm.setup.main()

    # init bot client
    bot = SenseiClient(shard_count=int(shard_count),
                       command_prefix="$",
                       intents=intents,
                       debug_guilds=[933389956246802483])

    # adding cogs
    bot.add_cog(OnReady(bot))
    bot.add_cog(OnVSUpdate(bot))
    bot.add_cog(OnGuildJoin(bot))
    bot.add_cog(OnGuildRemove(bot))
    bot.add_cog(CommandErrHandler(bot))
    bot.add_cog(DebugTools(bot))
    # tasks
    bot.log = Logging(bot)
    bot.tgg = TopGGUpdate(bot)
    bot.add_cog(bot.log)
    bot.add_cog(bot.tgg)
    # overwrite help cmd
    bot.remove_command('help')
    bot.add_cog(Help(bot))

    # adding slash cmds
    bot.add_cog(Create(bot))
    bot.add_cog(Data(bot))
    bot.add_cog(Config(bot))
    bot.add_cog(SetRoles(bot))

    bot.run(token)


if __name__ == '__main__':
    run()
