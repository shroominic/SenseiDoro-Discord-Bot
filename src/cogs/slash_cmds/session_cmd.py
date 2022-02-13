import asyncio

from discord import SlashCommandGroup, slash_command, Option

from src.cogs.useful_decoration import default_feedback
from src.cogs.better_response import response
from src.session import tools


class SessionCmd(SlashCommandGroup):
    def __init__(self, bot):
        super().__init__(name="session", description="Session configuration")
        self.bot = bot

    @slash_command()
    @default_feedback(title="Session successfully deleted.")
    async def delete(self, ctx):
        """ Use this command to delete your 🍅 session."""
        # get session instance
        session = await tools.get_session(ctx.channel, self.bot)
        await session.dispose()

    @slash_command()
    @default_feedback(title="Session successfully reset.")
    async def reset(self, ctx):
        """ Use this command to reset your 🍅 session. """
        # get session instance
        session = await tools.get_session(ctx.channel, self.bot)
        await session.reset_session()

    @slash_command(name="break")
    async def _break(self, ctx, minutes: int = 420):
        """ Use this command force a break and quit your current work session.
            :param minutes: break duration
        """
        # get session instance
        session = await tools.get_session(ctx.channel, self.bot)

        if session.timer.is_active:
            await session.force_break(minutes)
            # feedback
            title = "Current work session is reset."
            feedback = f"You now have a {session.timer.break_time} minutes break"
            asyncio.create_task(response(ctx, title, feedback, 10))
        else:
            # feedback
            title = "No active session."
            feedback = f"Dude, you can't have a break if you're not working!"
            asyncio.create_task(response(ctx, title, feedback, 10))

    @slash_command()
    async def edit(self, ctx, to_edit: Option(str,
                                              "What you want to edit.",
                                              choices=['name', 'work_time', 'break_time', 'repetitions']),
                   value: str):
        """ Use this command to edit your 🍅 session.
            :param to_edit: you can edit: 'name', 'work_time', 'break_time' or 'repetitions'
            :param value: new value of to_edit
        """
        # get session reference
        session = await tools.get_session(ctx.channel, self.bot)
        if "name" in to_edit:
            # get session instance
            if not value == "":
                session.name = value
                # feedback
                title = "Name changed"
                asyncio.create_task(response(ctx, title))
            else:
                # error
                title = "String required"
                feedback = "Please input session name as a string."
                asyncio.create_task(response(ctx, title, feedback))
        elif "work_time" in to_edit:
            if value.isnumeric():
                work_time = int(value)
                session.timer.work_time = work_time
                # feedback
                title = "Work time changed"
                asyncio.create_task(response(ctx, title))
            else:
                # error
                title = "Integer required"
                feedback = "Please input your work time in minutes."
                asyncio.create_task(response(ctx, title, feedback))
        elif "break_time" in to_edit:
            if value.isnumeric():
                break_time = int(value)
                session.timer.break_time = break_time
                # feedback
                title = "Break time changed"
                asyncio.create_task(response(ctx, title))
            else:
                # error
                title = "Integer required"
                feedback = "Please input your break time in minutes."
                asyncio.create_task(response(ctx, title, feedback))
        elif "repetitions" in to_edit:
            # get session instance
            session = await tools.get_session(ctx.channel, self.bot)
            if value.isnumeric():
                repetitions = int(value)
                session.timer.repetitions = repetitions
                # feedback
                title = "Repetitions changed"
                asyncio.create_task(response(ctx, title))
            else:
                # error
                title = "Integer required"
                feedback = "Please input the number of your repetitions."
                asyncio.create_task(response(ctx, title, feedback))
            await session.update_edit()
        else:
            # error
            title = "Wrong argument"
            feedback = "Try /session edit <name/work_time/break_time/repetitions>"
            asyncio.create_task(response(ctx, title, feedback))
        await session.update_edit()

    @staticmethod
    @delete.error
    @reset.error
    @_break.error
    @edit.error
    async def session_error(ctx, error):
        title = "Wrong environment"
        feedback = "Please use this command only inside a session category."
        asyncio.create_task(response(ctx, title, feedback))
