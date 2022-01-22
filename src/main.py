# Application Main

from dotenv import load_dotenv
import discord
import os

from src.clients.pomodojo_client import PomoDojoClient
from src.cogs.listeners.on_ready import OnReady
from src.cogs.listeners.on_vs_update import OnVSUpdate
from src.cogs.listeners.command_err_handler import CommandErrHandler
from src.cogs.commands.session_management import SessionManagement
from src.cogs.commands.tools import Tools


def run():
    # load token from .env
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')

    # client can see all users
    intents = discord.Intents.default()
    intents.members = True

    # init bot client
    bot = PomoDojoClient(
        intents=intents,
        command_prefix="$")

    # adding cogs
    bot.add_cog(OnReady(bot))
    bot.add_cog(OnVSUpdate(bot))
    bot.add_cog(CommandErrHandler(bot))
    bot.add_cog(SessionManagement(bot))
    bot.add_cog(Tools(bot))

    # finally run the bot
    bot.run(token)


if __name__ == '__main__':
    run()
