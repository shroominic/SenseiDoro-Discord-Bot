from datetime import timedelta
import asyncio
import time

import discord


class Timer:
    def __init__(self, session, work_time, break_time, repetitions):
        self.session = session
        self.timer_info_pointer = None
        # settings
        self.work_time = work_time
        self.break_time = break_time
        self.repetitions = repetitions
        # state
        self.is_active = False
        self.seconds_left = 0
        self.last_session = ""
        self.session_count = 0

    async def start_timer(self):
        timer_embed = discord.Embed(title="Work Timer", color=0xff0000)
        timer_embed.description = f"{self.work_time}:00"
        # setup timing message
        self.timer_info_pointer = await self.session.info_channel_pointer.send(embed=timer_embed)
        self.last_session = "work"
        self.set_time_left(self.work_time)
        # create timer thread
        asyncio.create_task(self.timer())
        await self.session.next_session()

    async def timer(self):
        next_call = time.time()
        tick = 10
        while self.is_active:
            # timer logic
            next_call += tick
            await asyncio.sleep(next_call - time.time())
            # to run
            if self.seconds_left < 1:
                self.manage_session()
            else:
                asyncio.create_task(self.display_update())
                self.seconds_left -= tick

    async def display_update(self):
        # format time to string
        str_time = str(timedelta(seconds=self.seconds_left))[2::]
        timer_embed = discord.Embed(title="Session Timer", color=0xff0000)
        timer_embed.description = str_time
        # edit timer message
        await self.timer_info_pointer.edit(embed=timer_embed)

    def set_time_left(self, minutes_left):
        self.seconds_left = minutes_left * 60

    def manage_session(self):
        if self.session_count < self.repetitions:
            if "pause" in self.last_session:
                self.set_time_left(self.work_time)
                self.last_session = "work"
                asyncio.create_task(self.session.next_session())
            elif "work" in self.last_session:
                self.set_time_left(self.break_time)
                self.last_session = "pause"
                asyncio.create_task(self.session.take_a_break())
        else:
            asyncio.create_task(self.session.reset_session())

    def increase_session_count(self):
        self.session_count += 1
