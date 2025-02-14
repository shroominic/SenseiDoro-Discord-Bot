import sqlite3
from contextlib import closing

import discord
from discord.ext import commands


class AllConfigs(discord.ui.View):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        # get dojo reference
        self.ctx = ctx
        self.dojo = self.bot.dojos[ctx.guild.id]

    @discord.ui.button(label="Mute Admins", style=discord.ButtonStyle.primary)
    async def first_button_callback(self, _, interaction):
        # show next view
        await interaction.channel.send(embed=discord.Embed(title="Mute Admins inside the focus session?"),
                                       view=ToggleMuteAdmins(self.bot, self.ctx))
        # disable button
        for child in self.children:  # loop through all the children of the view
            child.disabled = True
        await interaction.response.edit_message(view=self)  # update view


class ToggleMuteAdmins(discord.ui.View):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        # get dojo reference
        self.ctx = ctx
        self.dojo = self.bot.dojos[ctx.guild.id]

    @discord.ui.button(label="On", style=discord.ButtonStyle.success)
    async def first_button_callback(self, _, interaction):
        # update instance
        self.dojo.mute_admins = True
        # update database
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            c.execute("UPDATE dojos SET cfg_mute_admins = :cfg WHERE id = :id",
                      {"cfg": 1, "id": self.ctx.guild.id})
            conn.commit()
        # disable buttons
        for child in self.children:  # loop through all the children of the view
            child.disabled = True
        await interaction.response.edit_message(view=self)  # update view
        # respond to button pressed
        await interaction.channel.send("Mute admins is now enabled.", delete_after=3)

    @discord.ui.button(label="Off", style=discord.ButtonStyle.red)
    async def second_button_callback(self, _, interaction):
        # update instance
        self.dojo.mute_admins = False
        # update database
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            c.execute("UPDATE dojos SET cfg_mute_admins = :cfg WHERE id = :id",
                      {"cfg": 0, "id": self.ctx.guild.id})
            conn.commit()
        # disable button
        for child in self.children:  # loop through all the children of the view
            child.disabled = True
        await interaction.response.edit_message(view=self)  # update view
        # respond to button pressed
        await interaction.channel.send("Mute admins is now disabled.", delete_after=3)


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    # @admin_required
    async def config(self, ctx):
        # show button to toggle mute_admins
        await ctx.respond(embed=discord.Embed(title="Choose the config you want to change ..."),
                          view=AllConfigs(self.bot, ctx))
        # todo deactivate button after toggled
