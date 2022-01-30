from discord.ext import commands


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def config(self, ctx, config_command: str, arg1: bool):
        """
        Server configuration for admins.
        """
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]

        if "mute_admins" in config_command:
            if isinstance(arg1, bool):
                dojo.mute_admins = arg1
            else:
                ctx.send("Sorry, I need a boolean.")
        else:
            await ctx.send("Sorry, this config command doesn't exist.")
