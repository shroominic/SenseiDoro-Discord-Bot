import asyncio

import discord
from discord.ext import commands


class Data(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def data(self, ctx):
        """
        Use this command to get information about the data of the bot.
        """
        await ctx.respond(embed=discord.Embed(title="Data",
                                              description="Control the data of sensei doro."),
                          view=DataView(self.bot, ctx))


class DataView(discord.ui.View):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        # get dojo reference
        self.ctx = ctx
        self.dojo = self.bot.dojos[ctx.guild.id]

    @discord.ui.button(label="Reset", style=discord.ButtonStyle.primary)
    async def reset_callback(self, _, interaction):
        """ All data is reset as if the bot is new on the server. """
        # get dojo reference
        dojo = self.bot.dojos[self.ctx.guild.id]
        # update instance
        await dojo.reset_data()
        # disable button
        for child in self.children:  # loop through all the children of the view
            child.disabled = True
        await interaction.response.edit_message(embed=discord.Embed(title="Reset Successful", description=""),
                                                view=self)  # update view

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
    async def delete_callback(self, _, interaction):
        """ All data gets deleted. """
        # disable all buttons
        for child in self.children:
            child.disabled = True
        # Confirm deletion dialog
        title = "Confirm the deletion of ALL DATA"
        description = """
                    React with ✅ to confirm deletion.

                    This will delete:
                    - all configuration and settings
                    - all sessions on this server

                    Sensei Doro will leave the server afterwards.

                    Consider using `/data reset` if you only want to reset your data.
                    """
        confirm_dialog = discord.Embed(title=title, description=description)
        # change message view
        await interaction.response.edit_message(embed=confirm_dialog, view=self)
        # wait for confirmation
        try:
            await self.bot.wait_for('reaction_add',
                                    timeout=60.0,
                                    check=lambda reaction, user:
                                        user == self.ctx.author and str(reaction.emoji) == '✅')
        except asyncio.TimeoutError:
            await self.ctx.send('Sorry, this took to long for me. Try again!', delete_after=5)
        else:
            # get dojo reference
            dojo = self.bot.dojos[self.ctx.guild.id]
            # dojo delete
            await dojo.dispose()
