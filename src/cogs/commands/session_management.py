from discord.ext import commands
import asyncio

from session import env_manager
from session import Session, tools


class SessionManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def create(self, ctx, name: str = "Pomodoro", work_time: int = 25, break_time: int = 5, repetitions: int = 4):
        """
        Creates a new session environment with a session instance.
        You can customize with these 3 parameters:
        :param ctx: context of command
        :param name: session name
        :param work_time: duration in minutes of one work session
        :param break_time: duration in minutes of one pause
        :param repetitions: how many work sessions until the timer stops
        """
        new_session = Session(
            guild=ctx.guild_pointer,
            category=None,
            work_time=work_time,
            break_time=break_time,
            repetitions=repetitions,
            session_name=name
        )
        # checks if session already exists
        for session in self.bot.sessions:
            if session == new_session:
                asyncio.create_task(ctx.send('Session already exists!'))
                del new_session
                return
        self.bot.sessions.append(new_session)
        # initializes the session category and channels
        await env_manager.create_new_environment(new_session)

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
        if "reset" in session_command:
            await session.reset_session()
        else:
            await ctx.send("Type '$session delete' or '$session reset'")
