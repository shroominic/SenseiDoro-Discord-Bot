import traceback
import asyncio
import sys

from discord.ext.commands import Cog, CommandNotFound

from src.cogs.slash_cmds import cmd_helper


class CommandErrHandler(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        The event triggered when an error
        is raised while invoking a command.
        :param ctx: context of command
        :param error: specific command error
        """
        if isinstance(error, CommandNotFound):
            # error feedback
            title = "Command not found"
            feedback = "Sorry, I do not know this command."
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback, 10))
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
