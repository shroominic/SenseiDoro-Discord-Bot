# Application Main

from dotenv import load_dotenv
import discord
import os

from src.dbm import setup
from src.clients import SenseiClient
from src.cogs import *


def run():
    # load token from .env
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    shard_count = os.getenv('SHARD_COUNT')

    # client can see all users
    intents = discord.Intents.default()

    # init database
    setup.main()

    # init bot client
    bot = SenseiClient(shard_count=int(shard_count), command_prefix="$", intents=intents)

    # adding cogs
    bot.add_cog(OnReady(bot))
    bot.add_cog(OnVSUpdate(bot))
    bot.add_cog(OnGuildJoin(bot))
    bot.add_cog(OnGuildRemove(bot))
    bot.add_cog(CommandErrHandler(bot))
    bot.add_cog(DebugTools(bot))
    # tasks
    bot.tgg = TopGGUpdate(bot)
    bot.add_cog(bot.tgg)
    # overwrite help cmd
    bot.remove_command('help')
    bot.add_cog(Help(bot))

    # adding slash cmds
    bot.add_cog(Create(bot))
    bot.add_application_command(Data(bot))
    bot.add_application_command(Config(bot))
    bot.add_application_command(SetRole(bot))
    bot.add_application_command(SessionCmd(bot))

    bot.run(token)


if __name__ == '__main__':
    run()
