from datetime import timedelta
import asyncio
import time


class Timer:
    def __init__(self, session):
        self.session = session
        # time in minutes
        self.work_time = session.work_time
        self.pause_time = session.break_time
        # state
        self.seconds_left = 0
        self.last_session = ""
        # stream
        self.timerThread = None

    async def start_timer(self):
        self.last_session = "work"
        self.set_time_left(self.work_time)

        asyncio.create_task(self.timer())
        await self.session.next_session()
        print("timer started")

    def set_time_left(self, minutes_left):
        self.seconds_left = minutes_left * 60

    async def timer(self):
        next_call = time.time()
        tick = 5
        while self.session.is_active:
            # to run
            if self.seconds_left < 1:
                self.manage_session()
            else:
                str_time = str(timedelta(seconds=self.seconds_left))[2::]
                asyncio.create_task(self.session.display_timer(str_time))
                self.seconds_left -= tick
            # timer
            next_call += tick
            await asyncio.sleep(next_call - time.time())

    def manage_session(self):
        if self.session.session_count < self.session.session_repetitions:
            if "pause" in self.last_session:
                self.set_time_left(self.work_time)
                self.last_session = "work"
                asyncio.create_task(self.session.next_session())
            elif "work" in self.last_session:
                self.set_time_left(self.pause_time)
                self.last_session = "pause"
                asyncio.create_task(self.session.pause_session())
        else:
            asyncio.create_task(self.session.reset_session())



