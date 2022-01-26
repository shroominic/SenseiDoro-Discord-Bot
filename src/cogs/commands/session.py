from discord.ext import commands

from src.session import Session, tools


class Session(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def session(self, ctx, session_command=""):
        """
        Get control over your session:
        :param ctx: context of command
        :param session_command: use "delete" or "reset" to manage your session
        """
        # get session instance
        session = await tools.get_session(ctx.channel, self.bot)

        if "delete" in session_command:
            await session.dispose()
        elif "reset" in session_command:
            await session.reset_session()
        else:
            await ctx.send("Type '$session delete' or '$session reset'")
