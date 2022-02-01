import asyncio
import sys
import traceback

import discord
from discord import SlashCommandGroup, slash_command, ApplicationCommandInvokeError
from discord.ext.commands import has_permissions

from src.cogs.slash_cmds import cmd_helper


class SetRole(SlashCommandGroup):
    def __init__(self, bot):
        super().__init__(name="role", description="set server roles")
        self.bot = bot

    @slash_command()
    @has_permissions(administrator=True)
    async def admin(self, ctx, role: discord.Role):
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]
        # change role
        dojo.admin_role = role
        # command feedback
        title = "Role was successfully set"
        asyncio.create_task(cmd_helper.feedback(ctx, title, ""))

    @slash_command()
    @has_permissions(administrator=True)
    async def moderator(self, ctx, role: discord.Role):
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]
        # change role
        dojo.moderator_role = role
        # command feedback
        title = "Role was successfully set"
        asyncio.create_task(cmd_helper.feedback(ctx, title, ""))

    @staticmethod
    @admin.error
    @moderator.error
    async def role_error(ctx, error):
        if isinstance(error, ApplicationCommandInvokeError):
            title = "Missing Permissions"
            feedback = "You are missing Administrator permission to run this command."
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
