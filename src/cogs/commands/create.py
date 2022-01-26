from discord.ext import commands
import asyncio

from src.session import env_manager
from src.session import Session


class Create(commands.Cog):
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

        # checks for session limit
        if len(dojo.sessions) >= dojo.session_limit:
            asyncio.create_task(ctx.send(
                f'Session limit reached. You can only have {dojo.session_limit} sessions on your server.'))
            return

        # create new session
        new_session = Session(
            dojo=dojo,
            category=None,
            work_time=work_time,
            break_time=break_time,
            repetitions=repetitions,
            session_name=name,
            is_new_session=True)

        dojo.sessions[new_session.category_pointer.id] = new_session
