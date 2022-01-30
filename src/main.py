# Application Main
import discord
from dotenv import load_dotenv
import os

from src.clients.sensei_client import SenseiClient
from src.cogs.commands.help import Help
from src.cogs.listeners.on_ready import OnReady
from src.cogs.listeners.on_vs_update import OnVSUpdate
from src.cogs.listeners.on_guild_join import OnGuildJoin
from src.cogs.listeners.command_err_handler import CommandErrHandler
from src.cogs.commands.session_cmd import SessionCommand
from src.cogs.commands.admin_tools import Tools
from src.cogs.commands.set_role import SetRole
from src.cogs.commands.config import Config
from src.cogs.commands.create import Create


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
    bot.add_cog(SessionCommand(bot))
    bot.add_cog(Create(bot))
    bot.add_cog(Config(bot))
    bot.add_cog(Tools(bot))
    bot.add_cog(SetRole(bot))
    bot.remove_command('help')
    bot.add_cog(Help(bot))

    bot.run(token)


if __name__ == '__main__':
    run()
