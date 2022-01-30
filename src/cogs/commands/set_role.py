import discord
from discord.ext import commands


class SetRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def role(self, ctx, role_type: str, role: discord.Role):
        """
        Role configuration for admins.
        """
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]

        if "admin" in role_type:
            dojo.admin_role = role
        elif "moderator" in role_type:
            dojo.moderator_role = role
        elif "member" in role_type:
            dojo.member_role = role
        else:
            ctx.send("Sorry, I don't know this role.")
