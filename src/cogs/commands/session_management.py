from discord.ext import commands
import asyncio

from src.models.session import Session


class SessionManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def create(self, ctx, work_time: int = 25, pause_time: int = 5, intervals: int = 4):
        """
        Creates a new session environment with a session instance.
        You can customize with these 3 parameters:
        :param ctx: context of command
        :param work_time: duration in minutes of one work session
        :param pause_time: duration in minutes of one pause
        :param intervals: how many work sessions until the timer stops
        """
        new_session = Session(ctx.guild, work_time=work_time, break_time=pause_time, session_repetitions=intervals)
        # checks if session already exists
        for session in self.bot.sessions:
            if session == new_session:
                asyncio.create_task(ctx.send('Session already exists!'))
                del new_session
                return
        self.bot.sessions.append(new_session)
        # initializes the session category and channels
        await new_session.create_environment()

    @commands.command()
    async def session(self, ctx, session_command=""):
        """
        Get control over your session:
        :param ctx: context of command
        :param session_command: use "delete" or "reset" to manage your session
        """
        # get session instance
        session = await Session.get_session(ctx.channel, self.bot)

        if "delete" in session_command:
            await session.dispose()
        if "reset" in session_command:
            await session.reset_session()
        else:
            await ctx.send("Type '$session delete' or '$session reset'")
