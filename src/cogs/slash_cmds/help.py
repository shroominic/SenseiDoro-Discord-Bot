
import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def help(self, ctx):
        """
        Helps you out of every situation :)a
        """

        description = """
        To start a session just join the START SESSION channel.
        All your mates waiting in the Lobby will automatically follow you.
        
        Notation: <required argument> , [optional arg]{default value} , <'subcommands'|'to'|'choose'|'from'>
        """
        embed = discord.Embed(title="Help", description=description, color=0x00ff00)

        create_command = "Setup commands"
        create_info = """
        - Show help information: "/help [config]"
        - General configuration: /config <'mute_admins'| > <true/false> (more coming soon)
        - Set your own roles to control command permissions: /role <'admin'|'moderator'> <@your_role>
        - Create a new pomodoro environment: /create [name]{"Pomorodo"} [work_time]{25} [break_time]{5} [repetitions]{4}
        """
        embed.add_field(name=create_command, value=create_info, inline=False)

        session_command = "Session commands"
        session_info = """
        - Start a session: click on *START SESSION*
        - Edit the session: /session edit <'name'|'work_time'|'break_time'|'repetitions'> <value>
        - Force a break: /session break
        - Delete a session environment: /session delete
        - Reset a session to the initial state: /session reset
        """
        embed.add_field(name=session_command, value=session_info, inline=False)
        await ctx.respond(embed=embed)

