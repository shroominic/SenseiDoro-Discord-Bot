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
        """ todo write cleanup methode """
        await self.search_old_messages()
        if self.session.env.info_channel:
            async for msg in self.session.env.info_channel.history():
                if msg == self.session.env.info_msg or msg == self.session.env.timer_msg:
                    continue
                else:
                    await msg.delete()

    async def search_old_messages(self):
        """ todo write msg fetching methode """
        if self.session.env.info_channel:
            async for msg in self.session.env.info_channel.history():
                if msg.embeds:
                    for embed in msg.embeds:
                        if embed.fields:
                            for field in embed.fields:
                                if "Dashboard" in field.name:
                                    self.session.env.info_msg = msg
                        if "timer" in embed.title:
                            self.session.env.timer_msg = msg


class DashboardView(discord.ui.View):
    def __init__(self, session):
        super().__init__()
        self.bot = session.bot
        self.session = session

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.primary)
    async def first_button_callback(self, _, interaction):
        """ Use this command to reset your session. """
        # stop
        await self.session.stop_session()
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Break", style=discord.ButtonStyle.primary)
    async def second_button_callback(self, _, interaction):
        """ Use this command to reset your session. """
        # stop
        if self.session.timer.is_active:
            # todo add custom minutes
            await self.session.force_break(minutes=5)
            # todo show ui feedback
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.primary)
    async def third_button_callback(self, _, interaction):
        """ Use this command to delete your session. """
        # delete session
        asyncio.create_task(self.session.dispose())
        # disable buttons
        for child in self.children:  # loop through all children of the view
            child.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.primary)
    async def forth_button_callback(self, _, interaction):
        """ Use this command to edit your session. """
        # open edit form session
        await interaction.response.send_message(embed=discord.Embed(title="Session Editor"),
                                                view="")


class TimerView(discord.ui.View):
    def __init__(self, session):
        super().__init__()
        self.bot = session.bot
        self.session = session

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.primary)
    async def stop_button_callback(self, _, interaction):
        """ Use this command to stop and reset your session. """
        # stops session and timer
        await self.session.stop_session()
