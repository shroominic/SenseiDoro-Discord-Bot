import asyncio

from discord import SlashCommandGroup, slash_command
from discord.ext import commands

from src.cogs.slash_cmds import cmd_helper
from src.session import tools


class SessionCmd(SlashCommandGroup):
    def __init__(self, bot):
        super().__init__(name="session", description="session configuration")
        self.bot = bot

    @slash_command()
    async def delete(self, ctx):
        # get session instance
        session = await tools.get_session(ctx.channel, self.bot)
        await session.dispose()
        # feedback
        title = "Session successfully deleted."
        asyncio.create_task(cmd_helper.feedback(ctx, title))

    @slash_command()
    async def reset(self, ctx):
        # get session instance
        session = await tools.get_session(ctx.channel, self.bot)
        await session.reset_session()
        # feedback
        title = "Session successfully reset."
        asyncio.create_task(cmd_helper.feedback(ctx, title))

    @slash_command(name="break")
    async def _break(self, ctx, minutes=""):
        # get session instance
        session = await tools.get_session(ctx.channel, self.bot)
        # TODO : remove this weird logic
        if "" == minutes:
            await session.force_break()
            # feedback
            title = "Current work session is reset."
            feedback = f"You now have a {session.timer.break_time} minutes break"
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback, 10))
        elif minutes.isnumeric():
            await session.force_break(int(minutes))
            # feedback
            title = "Current work session is reset."
            feedback = f"You now have a {session.timer.break_time} minutes break"
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback, 10))
        else:
            # error
            title = "Integer required"
            feedback = "Please input your break time in minutes."
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))

    @slash_command()
    async def edit(self, ctx, to_edit: str, value: str):
        """ edit subcommand """

        if "name" in to_edit:
            # get session instance
            session = await tools.get_session(ctx.channel, self.bot)
            if not value == "":
                session.name = value
                # feedback
                title = "Name changed"
                asyncio.create_task(cmd_helper.feedback(ctx, title))
            else:
                # error
                title = "String required"
                feedback = "Please input session name as a string."
                asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
            await session.update_edit()

        elif "work_time" in to_edit:
            # get session instance
            session = await tools.get_session(ctx.channel, self.bot)
            if value.isnumeric():
                work_time = int(value)
                session.timer.work_time = work_time
                # feedback
                title = "Work time changed"
                asyncio.create_task(cmd_helper.feedback(ctx, title))
            else:
                # error
                title = "Integer required"
                feedback = "Please input your work time in minutes."
                asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
            await session.update_edit()

        elif "break_time" in to_edit:
            # get session instance
            session = await tools.get_session(ctx.channel, self.bot)
            if value.isnumeric():
                break_time = int(value)
                session.timer.break_time = break_time
                # feedback
                title = "Break time changed"
                asyncio.create_task(cmd_helper.feedback(ctx, title))
            else:
                # error
                title = "Integer required"
                feedback = "Please input your break time in minutes."
                asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
            await session.update_edit()

        elif "repetitions" in to_edit:
            # get session instance
            session = await tools.get_session(ctx.channel, self.bot)
            if value.isnumeric():
                repetitions = int(value)
                session.timer.repetitions = repetitions
                # feedback
                title = "Repetitions changed"
                asyncio.create_task(cmd_helper.feedback(ctx, title))
            else:
                # error
                title = "Integer required"
                feedback = "Please input the number of your repetitions."
                asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
            await session.update_edit()

        else:
            # error
            title = "Wrong argument"
            feedback = "Try /session edit <name/work_time/break_time/repetitions>"
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))

    @staticmethod
    @delete.error
    @reset.error
    @_break.error
    @edit.error
    async def session_error(ctx, error):
        if isinstance(error, AttributeError):
            title = "Wrong environment"
            feedback = "Please use this command only inside a session category."
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
