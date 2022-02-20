import asyncio
import sqlite3
import sys
import traceback
from contextlib import closing

import discord
from discord import SlashCommandGroup, slash_command, ApplicationCommandInvokeError
from discord.ext.commands import has_permissions

from src.cogs.useful_decoration import default_feedback
from src.cogs.better_response import slash_response


class SetRole(SlashCommandGroup):
    def __init__(self, bot):
        super().__init__(name="role", description="set server roles")
        self.bot = bot

    @slash_command()
    @has_permissions(administrator=True)
    @default_feedback(title="Role was successfully set")
    async def admin(self, ctx, role: discord.Role):
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]
        # change role
        dojo.admin_role_id = role.id
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            c.execute("UPDATE dojos SET role_admin = :role_id WHERE id = :id",
                      {"role_id": role.id, "id": ctx.guild.id})
            conn.commit()

    @slash_command()
    @has_permissions(administrator=True)
    @default_feedback(title="Role was successfully set")
    async def moderator(self, ctx, role: discord.Role):
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]
        # change role
        dojo.moderator_role_id = role.id
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            c.execute("UPDATE dojos SET role_mod = :role_id WHERE id = :id",
                      {"role_id": role.id, "id": ctx.guild.id})
            conn.commit()

    @staticmethod
    @admin.error
    @moderator.error
    async def role_error(ctx, error):
        print(error)
        if isinstance(error, ApplicationCommandInvokeError):
            title = "Missing Permissions"
            feedback = "You are missing Administrator permission to run this command."
            asyncio.create_task(slash_response(ctx, title, feedback))
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
