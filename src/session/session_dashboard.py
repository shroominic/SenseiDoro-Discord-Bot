import asyncio

import discord
from discord import Embed


class SessionDashboard:
    def __init__(self, parent_session):
        self.session = parent_session
        self.embed_msg = None

    def build_dashboard_embed(self) -> Embed:
        embed = Embed(title=f"{self.session.name} Dashboard")
        embed.add_field(name="work time",
                             value=f"{self.session.timer.work_time} min")
        embed.add_field(name="break time",
                             value=f"{self.session.timer.break_time} min")
        embed.add_field(name="reps",
                             value=f"[ {self.session.timer.session_count} | {self.session.timer.repetitions} ]")
        return embed

    def build_timer_embed(self):
        """ todo write timer embed methode """
        pass

    async def update(self):
        """ creates/updates the dashboard """
        await self.cleanup()
        # dashboard buttons
        session_controls = DashboardView(session=self.session)
        # update dashboard
        if self.session.env.info_msg:
            await self.session.env.info_msg.edit(embed=self.build_dashboard_embed(),
                                                 view=session_controls)
        # create dashboard
        else:
            self.session.env.info_msg = await self.session.env.info_channel.send(embed=self.build_dashboard_embed(),
                                                                                 view=session_controls)

    async def cleanup(self):
        """ clears you dashboard  """
        await self.search_old_messages()
        if self.session.env.info_channel:
            async for msg in self.session.env.info_channel.history():
                if msg != self.session.env.info_msg and msg != self.session.env.timer_msg:
                    await msg.delete()

    async def search_old_messages(self):
        """ fetches old messages from the dashboard channel """
        if self.session.env.info_channel:
            async for msg in self.session.env.info_channel.history():
                if msg.embeds:
                    for embed in msg.embeds:
                        if "Dashboard" in embed.title:
                            self.session.env.info_msg = msg
                        if "timer" in embed.title:
                            self.session.env.timer_msg = msg


class DashboardView(discord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=None)
        self.bot = session.bot
        self.session = session

    @discord.ui.button(label="🚀 Start", style=discord.ButtonStyle.green)
    async def start(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.session.start_session()
        await interaction.response.edit_message(view=None)

    @discord.ui.button(label="✏️ Edit", style=discord.ButtonStyle.primary)
    async def forth_button_callback(self, _, interaction):
        """ Use this command to edit your session. """
        # open edit form session
        await interaction.response.send_message(embed=discord.Embed(title="Session Editor"))

    @discord.ui.button(label="🗑 Delete", style=discord.ButtonStyle.danger)
    async def third_button_callback(self, _, interaction):
        """ Use this command to delete your session. """
        # delete session
        asyncio.create_task(self.session.dispose())
        # disable buttons
        for child in self.children:  # loop through all children of the view
            child.disabled = True
        await interaction.response.edit_message(view=self)
