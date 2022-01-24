from .timer import Timer
import asyncio
import json


# Pomodoro Session Class
class Session:
    # channel labels
    start_button_label = "START SESSION"
    information_label = "info"
    config_label = "config"
    lobby_label = "Lobby"
    chat_label = "chat"

    def __init__(self,
                 guild,
                 category=None,
                 work_time=30,
                 break_time=5,
                 session_repetitions=4,
                 session_name="Pomodoro"
                 ):
        self.name = session_name
        self.label = f"🍅 {self.name}]"
        self.category = category
        self.guild = guild
        # channels pointer
        self.text_channel_pointer = None
        self.config_channel_pointer = None
        self.lobby_channel_pointer = None
        self.work_channel_pointer = None
        # timer settings
        self.break_time = break_time
        self.work_time = work_time
        self.session_repetitions = session_repetitions
        self.session_count = 0
        self.timer_instance = None
        self.timer_info_pointer = None
        self.is_active = False

    #############
    #   START   #
    #############
    def increase_session_count(self):
        self.session_count += 1

    async def display_timer(self, time_left):
        info_timer_string = f"Time left: {time_left}"
        await self.timer_info_pointer.edit(content=info_timer_string)

    #   starting a models
    async def init_timer(self):
        self.timer_instance = Timer(self)
        # start models timer
        asyncio.create_task(self.timer_instance.start_timer())

    async def start_session(self, member):
        # init models
        await self.text_channel_pointer.send("Session has started!")
        await member.edit(mute=True)
        self.timer_info_pointer = await self.text_channel_pointer.send(f"Time left: {self.work_time}")
        # the timer manages the whole models
        self.is_active = True
        await self.init_timer()

    # models navigation
    async def next_session(self):
        self.increase_session_count()
        # rename models
        await self.work_channel_pointer.edit(name=f"Session [ {self.session_count} | {self.session_repetitions} ]")
        # move all members from lobby to models
        for member in self.lobby_channel_pointer.members:
            await member.move_to(self.work_channel_pointer)
            await member.edit(mute=True)

    async def pause_session(self):
        # move and unmute all waiting members
        for member in self.work_channel_pointer.members:
            await member.move_to(self.lobby_channel_pointer)
            await member.edit(mute=False)
        # some chill quote
        await self.work_channel_pointer.edit(name="dude ... relax")

    async def reset_session(self):
        # move all back to lobby
        for member in self.work_channel_pointer.members:
            await member.move_to(self.lobby_channel_pointer)
            await member.edit(mute=False)
        # reset stats
        self.is_active = False
        self.session_count = 0
        # start button
        await self.work_channel_pointer.edit(name=self.start_button_label)
        # reset models chat
        async for msg in self.text_channel_pointer.history(limit=100):
            if "Session config:" in msg.content:
                continue
            asyncio.create_task(msg.delete())

    # deletes the models
    async def dispose(self):
        # turn timer off
        self.is_active = False
        # delete channels
        for vc in self.category.voice_channels:
            await vc.delete()
        for tc in self.category.text_channels:
            await tc.delete()
        await self.category.delete()

    # serializes important information to json string
    def to_json(self):
        return json.dumps({
            "name": self.name,
            "work_time": self.work_time,
            "pause_time": self.break_time,
            "number_sessions": self.session_repetitions
        })

    def __eq__(self, other):
        return self.name == other.name
