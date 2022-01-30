import asyncio

import discord
from discord.ext import commands

from src.cogs.commands import cmd_helper


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, help_command=""):
        """
        Helps you out of every situation :)
        """
        if "" in help_command:
            description = """
            To start a session just join the START SESSION channel.
            All your mates waiting in the Lobby will automatically follow you.
            """
            embed = discord.Embed(title="Help", description=description, color=0xff0000)

            create_command = "$create <name> <work_time> <break_time> <repetitions>"
            create_info = """
            Use this command to create a new session environment.
            Type just '$create' for the classic pomodoro experience.
            """
            embed.add_field(name=create_command, value=create_info, inline=False)

            session_command = "$session [command]"
            session_info = """
            This command only works inside a session chat!
            You can use '$session reset' or '$session delete' to delete or reset your session.
            """
            embed.add_field(name=session_command, value=session_info, inline=False)
            await ctx.send(embed=embed)

        else:
            # command error
            title = "Wrong argument"
            feedback = "Sorry, I can not help you with this."
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
