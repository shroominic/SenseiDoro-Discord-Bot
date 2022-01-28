from datetime import timedelta
import asyncio
import time

import discord


class Timer:
    def __init__(self, session, work_time, break_time, repetitions):
        self.session = session
        self.info_msg = None
        # settings
        self.work_time = work_time
        self.break_time = break_time
        self.repetitions = repetitions
        # state
        self.is_active = False
        self.seconds_left = 0
        self.session_state = "Work"
        self.session_count = 0
        # set time left
        self.set_time_left(self.work_time)

    async def start_timer(self):
        # reset timer
        self.reset()
        # setup timing message
        timer_embed = self.get_timer_embed()
        self.info_msg = await self.session.info_channel_pointer.send(embed=timer_embed)
        # create timer thread
        self.is_active = True
        asyncio.create_task(self.timer())
        await self.session.next_session()

    def stop_timer(self):
        self.is_active = False

    def reset(self):
        self.is_active = False
        self.session_count = 0
        self.session_state = "Work"
        self.set_time_left(self.work_time)

    async def timer(self):
        next_call = time.time()
        while self.is_active:
            if self.seconds_left <= 10:
                tick = 1
            else:
                tick = 10
            # to run
            if self.seconds_left < 1:
                self.display_update()
                self.manage_session()
            else:
                # timer logic
                self.display_update()
                next_call += tick
                self.seconds_left -= tick
                await asyncio.sleep(next_call - time.time())

    def display_update(self):
        # format time to string
        timer_embed = self.get_timer_embed()
        # edit timer message
        asyncio.create_task(self.info_msg.edit(embed=timer_embed))

    def get_timer_embed(self):
        str_time = str(timedelta(seconds=self.seconds_left))[2::]
        timer_embed = discord.Embed(title=f"{self.session_state} timer", color=0xff0000)
        timer_embed.description = str_time
        return timer_embed

    def set_time_left(self, minutes_left):
        self.seconds_left = minutes_left * 60

    def manage_session(self):
        if self.session_count < self.repetitions:
            if "Pause" in self.session_state:
                self.set_time_left(self.work_time)
                self.session_state = "Work"
                asyncio.create_task(self.session.next_session())
            elif "Work" in self.session_state:
                self.set_time_left(self.break_time)
                self.session_state = "Pause"
                asyncio.create_task(self.session.take_a_break())
        else:
            asyncio.create_task(self.session.reset_session())

    def increase_session_count(self):
        self.session_count += 1
