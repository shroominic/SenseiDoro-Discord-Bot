from datetime import timedelta
import asyncio
import time


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
        self.last_session = "work"
        self.set_time_left(self.work_time)
        # create timer thread
        asyncio.create_task(self.timer())
        await self.session.next_session()

    async def timer(self):
        next_call = time.time()
        tick = 5
        while self.session.is_active:
            # to run
            if self.seconds_left < 1:
                self.manage_session()
            else:
                asyncio.create_task(self.display_update())
                self.seconds_left -= tick
            # timer logic
            next_call += tick
            await asyncio.sleep(next_call - time.time())

    async def display_update(self):
        # format time to string
        str_time = str(timedelta(seconds=self.seconds_left))[2::]
        timer_message = f"Time left: {str_time}"
        # edit timer message
        await self.timer_info_pointer.edit(content=timer_message)

    def set_time_left(self, minutes_left):
        self.seconds_left = minutes_left * 60

    def manage_session(self):
        if self.session.session_count < self.session.session_repetitions:
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
