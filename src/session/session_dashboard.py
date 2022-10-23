import asyncio

import discord
from discord import Embed


class SessionDashboard:
    def __init__(self, session):
        self.session = session
        # dashboard buttons
        self.buttons_view = None
        # dashboard embed
        # todo store dashboard embed references here

    def build_dashboard_embed(self) -> Embed:
        """ builds the dashboard embed """
        embed = Embed(title=f"{self.session.name} Dashboard")
        embed.add_field(name="🛠 work ",
                             value=f"{self.session.timer.work_time} min")
        embed.add_field(name="☕️ break ",
                             value=f"{self.session.timer.break_time} min")
        embed.add_field(name="♻️ reps ",
                             value=f"[ {self.session.timer.session_count} | {self.session.timer.repetitions} ]")
        return embed

    def build_timer_embed(self):
        """ todo write timer embed methode """
        pass

    async def update(self):
        """ creates/updates the dashboard """
        await self.cleanup()
        # dashboard buttons
        self.buttons_view = DashboardView(session=self.session)
        # disable buttons if session is not active
        if self.session.timer.is_active:
            self.buttons_view.disable_all_items()
        # check if dashboard message exists
        if self.session.env.info_msg:
            # update dashboard
            await self.session.env.info_msg.edit(embed=self.build_dashboard_embed(),
                                                 view=self.buttons_view)
        else:
            # create dashboard
            self.session.env.info_msg = await self.session.env.info_channel.send(embed=self.build_dashboard_embed(),
                                                                                 view=self.buttons_view)

    async def disable_buttons(self):
        """ disables all dashboard buttons """
        if self.buttons_view:
            self.buttons_view.disable_all_items()
            self.session.env.info_msg = await self.session.env.info_msg.edit(view=self.buttons_view)

    async def cleanup(self):
        """ clears you dashboard  """
        await self.search_old_messages()
        if self.session.env.info_channel:
            async for msg in self.session.env.info_channel.history():
                if msg != self.session.env.info_msg and msg != self.session.env.timer_msg:
                    try:
                        await msg.delete()
                    except discord.errors.NotFound:
                        pass

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
    """ dashboard buttons """
    def __init__(self, session):
        super().__init__(timeout=None)
        self.bot = session.bot
        self.session = session

    @discord.ui.button(emoji="🚀", label="Start", style=discord.ButtonStyle.green)
    async def start_button(self, _: discord.ui.Button, interaction: discord.Interaction):
        """ Use this button to start your session. """
        await self.session.start_session()
        # deactivate dashboard during session
        self.disable_all_items()
        # update dashboard
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="❖ More", style=discord.ButtonStyle.secondary)
    async def show_more_button(self, _: discord.ui.Button, interaction: discord.Interaction):
        """ Use this button to edit your session. """
        await interaction.response.edit_message(view=EditSessionView(session=self.session, parent_view=self))


class EditSessionView(discord.ui.View):
    """ edit buttons """
    def __init__(self, session, parent_view):
        super().__init__(timeout=None)
        self.bot = session.bot
        self.session = session
        self.parent_view = parent_view

    @discord.ui.button(label="⬅︎", style=discord.ButtonStyle.secondary)
    async def back(self, _: discord.ui.Button, interaction: discord.Interaction):
        """ Use this button to go back to the dashboard. """
        # move back to dashboard view
        await interaction.response.edit_message(view=self.parent_view)

    @discord.ui.button(emoji="✏️", label="Edit", style=discord.ButtonStyle.primary)
    async def edit_session(self, _: discord.ui.Button, interaction: discord.Interaction):
        """ Use this button to change the session name. """
        # input dialog
        modal = EditSessionModal(title="Edit Session", session=self.session)
        # update dashboard
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🗑 Delete", style=discord.ButtonStyle.danger)
    async def third_button_callback(self, _: discord.ui.Button, interaction: discord.Interaction):
        """ Use this button to delete your session. """
        # delete session
        asyncio.create_task(self.session.dispose())
        # disable buttons
        self.disable_all_items()
        # update view
        await interaction.response.edit_message(view=self)


class EditSessionModal(discord.ui.Modal):
    def __init__(self, session, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session = session

        self.add_item(discord.ui.InputText(label="Session Name"))
        self.add_item(discord.ui.InputText(label="Work Time"))
        self.add_item(discord.ui.InputText(label="Break Time"))
        self.add_item(discord.ui.InputText(label="Repetitions"))

    async def callback(self, interaction: discord.Interaction):
        """ callback for the modal """
        session_name = a if (a := self.children[0].value) == "" else None
        work_time = a if (a := self.children[1].value) == "" else None
        break_time = a if (a := self.children[2].value) == "" else None
        repetitions = a if (a := self.children[3].value) == "" else None
        # check if input is valid
        try:
            if work_time:
                self.session.timer.work_time = int(work_time)
        except ValueError:
            await interaction.channel.send_message("Invalid work time please use a number")
        try:
            if break_time:
                self.session.timer.break_time = int(break_time)
        except ValueError:
            await interaction.channel.send_message("Invalid break time please use a number")
        try:
            if repetitions:
                self.session.timer.repetitions = int(repetitions)
        except ValueError:
            await interaction.channel.send_message("Invalid repetitions please use a number")

        # response
        embed = discord.Embed(title="Edit Successful", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, delete_after=5)
