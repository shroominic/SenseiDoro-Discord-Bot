import sqlite3
from contextlib import closing

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions


class SetRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @has_permissions(administrator=True)
    async def set_roles(self, ctx, admin_role: discord.Role, mod_role: discord.Role):
        """
        Sets admin and mod roles for the current server.
        :param ctx: context of command
        :param admin_role: role to set as admin role
        :param mod_role: role to set as mod role
        """
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]
        # change roles
        dojo.admin_role_id = admin_role.id
        dojo.mod_role_id = mod_role.id
        # update database
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            c.execute("UPDATE dojos SET role_admin = :role_id WHERE id = :id",
                      {"role_id": admin_role.id, "id": ctx.guild.id})
            c.execute("UPDATE dojos SET role_mod = :role_id WHERE id = :id",
                      {"role_id": mod_role.id, "id": ctx.guild.id})
            conn.commit()
        # slash command response
        await ctx.respond(embed=discord.Embed(title="Admin and mod roles were successfully set"))
