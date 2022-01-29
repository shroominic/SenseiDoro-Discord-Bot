from discord.ext import commands


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def config(self, ctx, config_command=""):
        """
        Server configuration for admins.
        """
        if "" in config_command:
            pass
        else:
            await ctx.send("Sorry, this config command doesn't exist.")
