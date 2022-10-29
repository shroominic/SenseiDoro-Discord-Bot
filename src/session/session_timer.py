from datetime import timedelta
import discord
import asyncio
import time


class SessionTimer:
    def __init__(self, session, work_time, break_time, repetitions):
        self.session = session
        # settings
        self.tick = 20
        self.work_time = work_time
        self.break_time = break_time
        self.repetitions = repetitions
        # state
        self.is_active = False
        self.seconds_left = 0
        self.session_state = "Work"
        self.session_count = 0
        # controls
        self.buttons = None
        # set time left
        self.set_time_left(self.work_time)

    async def start_timer(self):
        # reset timer
        self.reset()
        # setup timing message
        timer_embed = self.build_timer_embed()
        self.session.env.timer_msg = await self.session.env.info_channel.send(embed=timer_embed)
        # create timer thread
        self.is_active = True
        asyncio.create_task(self.timer())
        # start next session
        self.increase_session_count()
        asyncio.create_task(self.session.next_session())

    def stop_timer(self):
        self.is_active = False
        self.buttons = None

    def reset(self):
        # reset session state
        self.is_active = False
        self.session_count = 0
        self.session_state = "Work"
        self.set_time_left(self.work_time)
        # delete timer message
        self.delete_timer_embed()

    async def timer(self):
        next_call = time.time()
        while self.is_active:
            # change tick size to 1 at the last 20 seconds
            if self.seconds_left <= 20:
                tick = 1
            else:
                tick = self.tick
            # check if timer is over
            if self.seconds_left < 1:
                self.display_update()
                self.manage_session()
            # timer logic
            else:
                # to run
                self.display_update()
                self.seconds_left -= tick
                # timer sleep
                next_call += tick
                await asyncio.sleep(next_call - time.time())

    def display_update(self):
        """ Update tne timer message/embed"""
        # buttons
        if self.buttons is None:
            self.buttons = TimerView(self.session) if self.session_state == "Work" else BreakView(self.session)
        # create embed
        timer_embed = self.build_timer_embed()
        # edit message
        asyncio.create_task(self.session.env.timer_msg.edit(embed=timer_embed, view=self.buttons))

    def build_timer_embed(self):
        # format seconds_left to [min]:[sec]
        str_time = str(timedelta(seconds=self.seconds_left))[2::]
        # create timer embed
        timer_embed = discord.Embed(title=f"{self.session_state} Timer", color=0xff0404)
        timer_embed.description = str_time

        return timer_embed

    def delete_timer_embed(self):
        if self.session.env.timer_msg:
            asyncio.create_task(self.session.env.timer_msg.delete())
            self.session.env.timer_msg = None

    def set_time_left(self, minutes_left):
        # format from minutes and set seconds_left
        self.seconds_left = minutes_left * 60

    def manage_session(self):
        # check if session is over
        if self.session_count < self.repetitions:
            # check for session_state and switch between <Work/Pause>
            if "Break" in self.session_state:
                self.set_time_left(self.work_time)
                self.session_state = "Work"
                self.increase_session_count()
                self.buttons = None
                asyncio.create_task(self.session.next_session())
            elif "Work" in self.session_state:
                self.set_time_left(self.break_time)
                self.session_state = "Break"
                asyncio.create_task(self.session.session_break())
                self.buttons = None
        # reset when session is over
        else:
            self.stop_timer()
            asyncio.create_task(self.session.stop_session())

    def increase_session_count(self):
        self.session_count += 1


class TimerView(discord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=None)
        self.bot = session.bot
        self.session = session

    @discord.ui.button(label="☕️ Break", style=discord.ButtonStyle.gray)
    async def break_button_callback(self, _, interaction):
        """ Use this command to pause your session. """
        if self.session.timer.is_active:
            await self.session.force_break(minutes=5)
            self.disable_all_items()
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="◽️ Stop", style=discord.ButtonStyle.danger)
    async def stop_button_callback(self, _, interaction):
        """ Use this command to stop and reset your session. """
        # stops session and timer
        asyncio.create_task(self.session.stop_session())
        await interaction.response.edit_message(view=self)


class BreakView(discord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=None)
        self.bot = session.bot
        self.session = session

    @discord.ui.button(label="⏩️ Skip", style=discord.ButtonStyle.primary)
    async def skip_button_callback(self, _, interaction):
        """ Use this command to stop and reset your session. """
        # skips break
        self.session.timer.seconds_left = 0
        self.disable_all_items()
        await interaction.response.edit_message(view=self)

    @discord.ui.button(emoji="⏳", label="+1", style=discord.ButtonStyle.gray)
    async def add3_button_callback(self, _, interaction):
        """ Use this command to pause your session. """
        if self.session.timer.session_state == "Break":
            self.session.timer.seconds_left += 60
            self.session.timer.initial_time += 60
            self.session.timer.display_update()
        await interaction.response.edit_message(view=self)



