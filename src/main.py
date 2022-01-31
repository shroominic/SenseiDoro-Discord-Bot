# Application Main

from dotenv import load_dotenv
import discord
import os

from src.clients import SenseiClient
from src.cogs import *


def run():
    # load token from .env
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')

    # client can see all users
    intents = discord.Intents.default()
    intents.members = True

    # init bot client
    bot = SenseiClient(command_prefix="$", intents=intents)

    # adding cogs
    bot.add_cog(OnReady(bot))
    bot.add_cog(OnVSUpdate(bot))
    bot.add_cog(OnGuildJoin(bot))
    bot.add_cog(CommandErrHandler(bot))
    bot.add_cog(Create(bot))
    bot.add_cog(AdminTools(bot))

    # overwrite help cmd
    bot.remove_command('help')
    bot.add_cog(Help(bot))

    # adding slash cmds
    bot.add_application_command(Config(bot))
    bot.add_application_command(SetRole(bot))
    bot.add_application_command(SessionCmd(bot))

    bot.run(token)


if __name__ == '__main__':
    run()
