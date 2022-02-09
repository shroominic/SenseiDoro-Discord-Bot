import asyncio
import sqlite3
from contextlib import closing

from discord import SlashCommandGroup, slash_command

from src.cogs.useful_decoration import admin_required, default_feedback


class Config(SlashCommandGroup):
    def __init__(self, bot):
        super().__init__(name="config", description="[Admin] Configure special settings for Sensei Doro.")
        self.bot = bot

    @slash_command()
    @admin_required
    @default_feedback(title="Config changed", description="")
    async def mute_admins(self, ctx, value: bool):
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]
        # update instance
        dojo.mute_admins = value
        # update database
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            c.execute("UPDATE dojos SET cfg_mute_admins = :cfg WHERE id = :id",
                      {"cfg": int(value), "id": ctx.guild.id})
            conn.commit()

