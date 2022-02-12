from discord.ext import commands
import asyncio

from src.cogs.useful_decoration import default_feedback
from src.cogs.better_response import response
from src.session import Session


class Create(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @default_feedback(title="Session successfully created")
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
            # error feedback
            title = "Session limit reached"
            feedback = "You can currently have only {dojo.session_limit} sessions on your server."
            asyncio.create_task(response(ctx, title, feedback, 10))
            return

        # create new session
        Session(
            dojo=dojo,
            category=None,
            work_time=work_time,
            break_time=break_time,
            repetitions=repetitions,
            session_name=name,
            is_new_session=True)
