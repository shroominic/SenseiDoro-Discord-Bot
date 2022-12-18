import asyncio
import os

import discord
from discord import Embed
from dotenv import load_dotenv
from discord.ext import commands, tasks


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # load token from .env
        load_dotenv()
        self.logging_token = os.getenv('LOGGING_TOKEN')
        #
        self.manager_id = None
        self.stats_embed = None

    @tasks.loop(minutes=0.1)
    async def auto_refresh(self):
        """ refreshes the stats embed every minute """
        pass
        # await self.update_stats()

    async def update_manager_id(self):
        if self.manager_id is None:
            self.manager_id = await self.bot.fetch_user(self.logging_token)
        return self.manager_id

    async def update_stats(self):
        """ Refreshes the stats embed """
        if self.stats_embed:
            await self.stats_embed.edit(embed=self.sensei_stats_embed)
        elif self.manager_id:
            self.stats_embed = await self.manager_id.send(embed=self.sensei_stats_embed)
        else:
            await self.manage_sensei_stats()

    async def send_control_panel(self):
        """ sends the control panel to the logging channel """
        if self.manager_id:
            # check if control panel exists
            control_panel = [msg async for msg in self.manager_id.history()
                             if msg.embeds and msg.embeds[0].title == "Control Panel"]
            if not control_panel:
                # create control panel
                control_panel_embed = Embed(title="Control Panel", color=0x0f0fff)
                asyncio.create_task(self.manager_id.send(embed=control_panel_embed, view=AdminDashboardView(self)))

    def send_log(self, title, body="", color=0xffffff, delete_after=None):
        """ sends a log to the logging channel """
        if self.manager_id:
            embed = Embed(title=title, description=body, color=color)
            asyncio.create_task(self.manager_id.send(embed=embed, delete_after=delete_after))

    def exception(self, exception_ctx, exception_body, color=0xff0000):
        """ sends an exception to the logging channel """
        self.send_log(f"Exception: {exception_ctx}", exception_body, color)

    @property
    def sensei_stats_embed(self):
        """ creates a embed for all sensei stats """
        embed = Embed(title="Sensei Stats")
        # number of dojos
        embed.add_field(name="Total Dojos",
                        value=f"{self.bot.total_dojos}")
        # number of all created sessions
        embed.add_field(name="Total Sessions",
                        value=f"{self.bot.total_sessions}")
        # number of running sessions
        embed.add_field(name="Active Sessions",
                        value=f"{self.bot.total_active_sessions}")
        # number of users inside active sessions
        embed.add_field(name="Active Users",
                        value=f"{self.bot.total_active_users}")
        # number of sessions running in the last 24 hours
        embed.add_field(name="Sessions per 24h",
                        value=f"{self.bot.total_sessions_24h}")
        # number of active users in the last 24 hours
        embed.add_field(name="Users per 24h",
                        value=f"{self.bot.total_users_24h}")
        # todo add more stats
        return embed

    async def manage_sensei_stats(self):
        """ manages the sensei stats embed """
        await self.update_manager_id()
        embeds = [msg async for msg in self.manager_id.history()
                  if msg.embeds for embed in msg.embeds
                  if "Sensei Stats" in embed.title]
        if len(embeds) == 0:
            self.stats_embed = await self.manager_id.send(embed=self.sensei_stats_embed)
        else:
            for embed in embeds[1:]:
                await embed.delete()
            self.stats_embed = embeds[0]
            await self.stats_embed.edit(embed=self.sensei_stats_embed)
        await self.send_control_panel()


class AdminDashboardView(discord.ui.View):
    """ admin dashboard buttons"""
    def __init__(self, parent):
        super().__init__(timeout=None)
        self.parent = parent

    @discord.ui.button(emoji="🥬", label="Refresh", style=discord.ButtonStyle.green, custom_id="refresh")
    async def refresh(self, _: discord.ui.Button, interaction: discord.Interaction):
        """ Refreshes the stats embed """
        await self.parent.update_stats()
        # update dashboard
        try:
            await interaction.response.edit_message(view=self)
        except discord.NotFound:
            pass

    @discord.ui.button(label="❖ More", style=discord.ButtonStyle.secondary, custom_id="more")
    async def show_more_button(self, _: discord.ui.Button, interaction: discord.Interaction):
        """ Use this button to show a sub menu. """
        await interaction.response.edit_message(view=MoreADView(parent_view=self))


class MoreADView(discord.ui.View):
    """ More admin dashboard buttons"""
    def __init__(self, parent_view):
        super().__init__(timeout=None)
        self.parent_view = parent_view

    @discord.ui.button(label="⬅", style=discord.ButtonStyle.secondary, custom_id="back")
    async def back_button(self, _: discord.ui.Button, interaction: discord.Interaction):
        """ Use this button to go back to the parent view. """
        await interaction.response.edit_message(view=self.parent_view)

    @discord.ui.button(label="Clear", style=discord.ButtonStyle.red, custom_id="clear")
    async def clear_button(self, _: discord.ui.Button, interaction: discord.Interaction):
        """ Use this button to clear the chat. """
        await interaction.response.edit_message(view=self.parent_view)
        async for msg in interaction.channel.history():
            if msg.author == self.parent_view.parent.bot.user and msg != interaction.message and msg != self.parent_view.parent.stats_embed:
                try:
                    await msg.delete()
                except discord.errors.NotFound:
                    pass

    @discord.ui.button(label="Shutdown", style=discord.ButtonStyle.red, custom_id="shutdown")
    async def shutdown_button(self, _: discord.ui.Button, interaction: discord.Interaction):
        """ Use this button to shutdown the bot. """
        await interaction.response.edit_message(view=self.parent_view)
        await self.parent_view.parent.bot.close()
