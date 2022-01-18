from .timer import Timer
import asyncio
import json


# Pomodoro Session Class
class Session:
    # channel names
    start_button_name = "START SESSION"
    chat_channel_name = "session_chat"
    session_config = "config"
    lobby_name = "Lobby"
    # next session id
    next_id = 0
    def __init__(self, guild, category=None, work_time=30, break_time=5, session_repetitions=4, session_id=None):
        self.name = f"🍅 - [{work_time} | {break_time}]"
        self.category = category
        self.guild = guild
        # session id
        self.id = session_id
        if not session_id:
            self.id = Session.next_id
            Session.next_id += 1
        # channels instance
        self.text_channel_instance = None
        self.config_channel_instance = None
        self.lobby_channel_instance = None
        self.work_channel_instance = None
        # timer settings
        self.break_time = break_time
        self.work_time = work_time
        self.session_repetitions = session_repetitions
        self.session_count = 0
        self.timer_instance = None
        self.timer_message_instance = None
        self.is_active = False
        # todo statistics

    async def create_environment(self):
        # create session category
        self.category = await self.guild.create_category_channel(self.name)
        # create initial channels
        self.text_channel_instance = await self.guild.create_text_channel(
            self.chat_channel_name,
            category=self.category
        )
        self.lobby_channel_instance = await self.guild.create_voice_channel(
            self.lobby_name,
            category=self.category
        )
        self.work_channel_instance = await self.guild.create_voice_channel(
            self.start_button_name,
            category=self.category
        )
        self.config_channel_instance = await self.guild.create_text_channel(
            self.session_config,
            category=self.category
        )
        await self.config_channel_instance.set_permissions(self.guild.default_role, read_messages=False)
        # send serialization of session as message
        await self.config_channel_instance.send(f"Session config: {self.to_json()}")

    async def setup_old_environment(self):
        for vc in self.category.voice_channels:
            channel_name = vc.name
            if self.lobby_name in channel_name:
                self.lobby_channel_instance = vc
            if self.start_button_name in channel_name \
                    or "Session" in channel_name \
                    or "dude ... relax" in channel_name:
                self.work_channel_instance = vc
        for tc in self.category.text_channels:
            channel_name = tc.name
            if self.chat_channel_name in channel_name:
                self.text_channel_instance = tc
        await self.reset_session()

    def increase_session_count(self):
        self.session_count += 1

    async def display_timer(self, time_left):
        info_timer_string = f"Time left: {time_left}"
        await self.timer_message_instance.edit(content=info_timer_string)

    #   starting a session
    async def init_timer(self):
        self.timer_instance = Timer(self)
        # start session timer
        asyncio.create_task(self.timer_instance.start_timer())

    async def start_session(self, member):
        # init session
        await self.text_channel_instance.send("Session has started!")
        await member.edit(mute=True)
        self.timer_message_instance = await self.text_channel_instance.send(f"Time left: {self.work_time}")
        # the timer manages the whole session
        self.is_active = True
        await self.init_timer()

    # session navigation
    async def next_session(self):
        self.increase_session_count()
        # TODO: Closed Permission for work_channel
        # rename session
        await self.work_channel_instance.edit(name=f"Session [ {self.session_count} | {self.session_repetitions} ]")
        # move all members from lobby to session
        for member in self.lobby_channel_instance.members:
            await member.move_to(self.work_channel_instance)
            await member.edit(mute=True)

    async def pause_session(self):
        # move and unmute all waiting members
        for member in self.work_channel_instance.members:
            await member.move_to(self.lobby_channel_instance)
            await member.edit(mute=False)
        # some chill quote
        await self.work_channel_instance.edit(name="dude ... relax")

    async def reset_session(self):
        # move all back to lobby
        for member in self.work_channel_instance.members:
            await member.move_to(self.lobby_channel_instance)
            await member.edit(mute=False)
        # reset stats
        self.is_active = False
        self.session_count = 0
        # start button
        await self.work_channel_instance.edit(name=self.start_button_name)
        # reset session chat
        async for msg in self.text_channel_instance.history(limit=100):
            if "Session config:" in msg.content:
                continue
            asyncio.create_task(msg.delete())

    # deletes the session
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
            "id": self.id,
            "work_time": self.work_time,
            "pause_time": self.break_time,
            "number_sessions": self.session_repetitions
        })

    def __eq__(self, other):
        return self.id == other.id
