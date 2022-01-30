import asyncio
import discord

from src.cogs.commands import cmd_helper
from discord.ext import commands


class SetRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def role(self, ctx, role_type: str, role: discord.Role):
        """
        Role configuration for admins.
        """
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]

        if "admin" in role_type:
            dojo.admin_role = role
            # command feedback
            title = "Role was successfully set"
            asyncio.create_task(cmd_helper.feedback(ctx, title, ""))

        elif "moderator" in role_type:
            dojo.moderator_role = role
            # command feedback
            title = "Role was successfully set"
            asyncio.create_task(cmd_helper.feedback(ctx, title, ""))

        elif "member" in role_type:
            dojo.member_role = role
            # command feedback
            title = "Role was successfully set"
            asyncio.create_task(cmd_helper.feedback(ctx, title, ""))

        else:
            # error
            title = "Role not found."
            feedback = "You can set either 'admin', 'moderator' or 'member'."
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback, 10))

