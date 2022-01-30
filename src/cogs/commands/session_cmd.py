import asyncio

from discord.ext import commands

from src.cogs.commands import cmd_helper
from src.session import tools


class SessionCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def session(self, ctx, arg1="", arg2="", arg3="", arg4="", arg5=""):
        """
        Get control over your session:
        :param ctx: context of command
        :param arg1: use 'delete', 'reset', 'break' or 'edit' to manage your session
        :param arg2: cmd specific
        :param arg3: cmd specific
        :param arg4: cmd specific
        :param arg5: cmd specific
        """
        # get session instance
        session = await tools.get_session(ctx.channel, self.bot)

        if "delete" in arg1:
            await session.dispose()
            # feedback
            title = "Session successfully deleted."
            asyncio.create_task(cmd_helper.feedback(ctx, title))
        elif "reset" in arg1:
            await session.reset_session()
            # feedback
            title = "Session successfully reset."
            asyncio.create_task(cmd_helper.feedback(ctx, title))
        elif "break" in arg1:
            if "" == arg2:
                await session.force_break()
                # feedback
                title = "Current work session is reset."
                feedback = f"You now have a {session.timer.break_time} minutes break"
                asyncio.create_task(cmd_helper.feedback(ctx, title, feedback, 10))
            elif arg2.isnumeric():
                await session.force_break(int(arg2))
                # feedback
                title = "Current work session is reset."
                feedback = f"You now have a {session.timer.break_time} minutes break"
                asyncio.create_task(cmd_helper.feedback(ctx, title, feedback, 10))
            else:
                # error
                title = "Integer required"
                feedback = "Please input your break time in minutes."
                asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
        elif "edit" in arg1:
            if "name" in arg2:
                if not arg3 == "":
                    session.name = arg3
                    # feedback
                    title = "Name changed"
                    asyncio.create_task(cmd_helper.feedback(ctx, title))
                else:
                    # error
                    title = "String required"
                    feedback = "Please input session name as a string."
                    asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
            # edit work_time
            elif "work_time" in arg2:
                if arg3.isnumeric():
                    work_time = int(arg3)
                    session.timer.work_time = work_time
                    # feedback
                    title = "Work time changed"
                    asyncio.create_task(cmd_helper.feedback(ctx, title))
                else:
                    # error
                    title = "Integer required"
                    feedback = "Please input your work time in minutes."
                    asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
            # edit break_time
            elif "break_time" in arg2:
                if arg3.isnumeric():
                    break_time = int(arg3)
                    session.timer.break_time = break_time
                    # feedback
                    title = "Break time changed"
                    asyncio.create_task(cmd_helper.feedback(ctx, title))
                else:
                    # error
                    title = "Integer required"
                    feedback = "Please input your break time in minutes."
                    asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
            # edit repetitions
            elif "repetitions" in arg2:
                if arg3.isnumeric():
                    repetitions = int(arg3)
                    session.timer.repetitions = repetitions
                    # feedback
                    title = "Work time changed"
                    asyncio.create_task(cmd_helper.feedback(ctx, title))
                else:
                    # error
                    title = "Integer required"
                    feedback = "Please input the number of your repetitions."
                    asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
            # edit work_time, break_time and repetitions
            elif "timer" in arg2:
                work_time, break_time, repetitions = 25, 5, 4
                if arg3.isnumeric():
                    work_time = int(arg3)
                session.timer.work_time = work_time
                if arg4.isnumeric():
                    break_time = int(arg4)
                session.timer.break_time = break_time
                if arg5.isnumeric():
                    repetitions = int(arg5)
                session.timer.repetitions = repetitions
                # feedback
                title = "Timer successfully changed"
                asyncio.create_task(cmd_helper.feedback(ctx, title))
            else:
                # error
                title = "Wrong argument"
                feedback = "Try '$session edit <name/work_time/break_time/repetitions/timer>'"
                asyncio.create_task(cmd_helper.feedback(ctx, title, feedback, 15))
            await session.update_edit()
        else:
            # error
            title = "Wrong argument"
            feedback = "Try '$session <delete/reset/edit>'"
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback, 15))

