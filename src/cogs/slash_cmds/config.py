import asyncio

from discord import SlashCommandGroup, slash_command

from src.cogs.slash_cmds import cmd_helper


class Config(SlashCommandGroup):
    def __init__(self, bot):
        super().__init__(name="config", description="bot configuration")
        self.bot = bot

    @slash_command()
    async def mute_admins(self, ctx, value: bool):
        # cmd only for admins
        role = self.bot.dojos[ctx.guild.id].admin_role
        if role in ctx.author.roles:
            # get dojo reference
            dojo = self.bot.dojos[ctx.guild.id]
            dojo.mute_admins = value
            # feedback
            title = "Config changed"
            feedback = f"[mute_admins] <- {value}"
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
        else:
            title = "Missing Role"
            feedback = "You are missing the admin role to run this command."
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
