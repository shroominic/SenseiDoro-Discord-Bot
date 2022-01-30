import asyncio

from discord.ext import commands

from src.cogs.commands import cmd_helper


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def config(self, ctx, config_command: str, arg1: bool):
        """
        Server configuration for admins.
        """
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]

        if "mute_admins" in config_command:
            if isinstance(arg1, bool):
                dojo.mute_admins = arg1
                # feedback
                title = "Config changed"
                feedback = f"[mute_admins] <- {arg1}"
                asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
            else:
                # error
                title = "Boolean required"
                asyncio.create_task(cmd_helper.feedback(ctx, title))
        else:
            # error
            title = "Wrong argument"
            feedback = "{show configurable items}"  # TODO
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
