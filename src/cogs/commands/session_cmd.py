from discord.ext import commands

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
        elif "reset" in arg1:
            await session.reset_session()
        elif "break" in arg1:
            if "" == arg2:
                await session.force_break()
            elif arg2.isnumeric():
                await session.force_break(int(arg2))
            else:
                await ctx.send("Please input your break time in minutes (integer).")
        elif "edit" in arg1:
            if "name" in arg2:
                if not arg3 == "":
                    session.name = arg3
                else:
                    await ctx.send("Please input a string.")
            # edit work_time
            elif "work_time" in arg2:
                if arg3.isnumeric():
                    work_time = int(arg3)
                    session.timer.work_time = work_time
                else:
                    await ctx.send("Please input your work_time in minutes (integer).")
            # edit break_time
            elif "break_time" in arg2:
                if arg3.isnumeric():
                    break_time = int(arg3)
                    session.timer.break_time = break_time
                else:
                    await ctx.send("Please input your break_time in minutes (integer).")
            # edit repetitions
            elif "repetitions" in arg2:
                if arg3.isnumeric():
                    repetitions = int(arg3)
                    session.timer.repetitions = repetitions
                else:
                    await ctx.send("Please input your repetitions as an integer.")
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
            else:
                error = "You can use '$session edit <name/work_time/break_time/repetitions/timer>'"
                await ctx.send(error)
            await session.update_edit()
        else:
            await ctx.send("You can use '$session <delete/reset/edit>'")
