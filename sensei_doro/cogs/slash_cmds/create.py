from discord.ext import commands

from ..useful_decoration import default_feedback, mod_required
from ..better_response import slash_response
from ...session import Session


class Create(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="create",
        description="Creates a new session in your server.",
        cooldown=commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.user))
    @mod_required
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
        if len(dojo.lobby_ids) >= dojo.session_limit:
            # error feedback
            title = "Session limit reached"
            feedback = f"You can currently have only {dojo.session_limit} sessions on your server."
            slash_response(ctx, title, feedback, 10)
            return
        # create new session
        Session.new_session(self.bot, ctx.guild.id, name, work_time, break_time, repetitions)
        # success feedback
        title = "Session successfully created"
        slash_response(ctx, title, "", 10)
