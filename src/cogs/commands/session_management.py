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
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]
        # create new session
        new_session = Session(
            dojo=dojo,
            category=None,
            work_time=work_time,
            break_time=break_time,
            repetitions=repetitions,
            session_name=name
        )
        # checks if session already exists
        if len(dojo.sessions) >= dojo.session_limit:
            asyncio.create_task(ctx.send(
                f'Session limit reached. You can only have {dojo.session_limit} 🍅 sessions on your server.'))
            del new_session
            return
        # initializes the session category and channels
        await env_manager.create_new_environment(new_session)
        dojo.sessions[new_session.category_pointer.id] = new_session

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
