from datetime import timedelta
import asyncio


class Timer:
    def __init__(self, work_time, pause_time, intervals, send_update, send_next, send_pause, send_stop):
        self.intervals = intervals
        # time in minutes
        self.work_time = work_time
        self.pause_time = pause_time
        # callback functions
        self.send_update = send_update

        self.send_next = send_next
        self.send_pause = send_pause
        self.send_stop = send_stop

    async def timer(self, minutes, final_function):
        tick = 5
        count = 0
        seconds = minutes * 60
        while count < seconds:
            await asyncio.sleep(tick)
            count += tick
            time_left = str(timedelta(seconds=(seconds-count)))[2::]
            asyncio.create_task(self.send_update(time_left))
        await final_function()

    async def run_session(self):
        await self.send_next()
        for i in range(self.intervals - 1):
            await self.timer(self.work_time, self.send_pause)
            await self.timer(self.pause_time, self.send_next)
        await self.timer(self.work_time, self.send_stop)

