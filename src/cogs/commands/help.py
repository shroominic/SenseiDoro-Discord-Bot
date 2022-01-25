from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, help_command=""):
        """
        Helps you out of every situation :)
        """
        if "" in help_command:
            await ctx.send("""
            If you see this the first time just type $create and look what happens.
            To start a session just join the START SESSION channel.
            All your mates waiting in the Lobby will automatically follow you.
            Use $help <create/session> to get detailed information about the commands.
            """)
        elif "create" in help_command:
            await ctx.send("To create a new session use '$create <name> <work_time> <break_time> <repetitions>'.")
        elif "session" in help_command:
            await ctx.send("You can currently '$session reset' or '$session delete'. \
            This only works inside a session chat.")
        else:
            await ctx.send("Sorry, I can't help you with this :(")
