from .timer import Timer
import asyncio
import json


# Pomodoro Session Class
class Session:
    # channel labels
    start_button_label = "START SESSION"
    session_break_label = ""
    information_label = "information"
    config_label = "config"
    lobby_label = "Lobby"
    chat_label = "chat"

    def __init__(self,
                 guild,
                 category,
                 work_time,
                 break_time,
                 repetitions,
                 session_name="Pomodoro"
                 ):
        self.name = session_name
        self.label = f"🍅 {self.name}]"
        # pointers
        self.guild_pointer = guild
        self.category_pointer = category
        self.info_channel_pointer = None
        self.chat_channel_pointer = None
        self.work_channel_pointer = None
        self.lobby_channel_pointer = None
        self.config_channel_pointer = None
        # timer settings
        self.timer = Timer(self, work_time, break_time, repetitions)

    #############
    #   START   #
    #############

    async def start_session(self, member):
        # init session
        await self.chat_channel_pointer.send("Session has started!")
        await member.edit(mute=True)
        # the timer manages the whole session
        self.timer.is_active = True
        # setup timing message
        self.timer.timer_info_pointer = await self.info_channel_pointer.send(f"Time left: {self.timer.work_time}")
        # start session timer
        asyncio.create_task(self.timer.start_timer())

    ##################
    #   NAVIGATION   #
    ##################

    async def next_session(self):
        self.timer.increase_session_count()
        # rename session
        await self.work_channel_pointer.edit(name=f"Session [ {self.timer.session_count} | {self.timer.repetitions} ]")
        # move all members from lobby to session
        for member in self.lobby_channel_pointer.members:
            await member.move_to(self.work_channel_pointer)
            await member.edit(mute=True)

    async def take_a_break(self):
        # move and unmute all waiting members
        for member in self.work_channel_pointer.members:
            await member.move_to(self.lobby_channel_pointer)
            await member.edit(mute=False)
        # some chill quote
        await self.work_channel_pointer.edit(name=self.session_break_label)

    async def reset_session(self):
        # move all back to lobby
        for member in self.work_channel_pointer.members:
            await member.move_to(self.lobby_channel_pointer)
            await member.edit(mute=False)
        # reset stats
        self.timer.is_active = False
        self.session_count = 0
        # start button
        await self.work_channel_pointer.edit(name=self.start_button_label)
        # reset session chat
        async for msg in self.chat_channel_pointer.history(limit=100):
            if "Session config:" in msg.content:
                continue
            asyncio.create_task(msg.delete())

    ###############
    #    TOOLS    #
    ###############

    async def dispose(self):
        # turn timer off
        self.timer.is_active = False
        # delete channels
        for vc in self.category_pointer.voice_channels:
            await vc.delete()
        for tc in self.category_pointer.text_channels:
            await tc.delete()
        await self.category_pointer.delete()

    def to_json(self):
        """
        serializes important information to json string
        """
        return json.dumps({
            "name": self.name,
            "work_time": self.timer.work_time,
            "pause_time": self.timer.break_time,
            "number_sessions": self.timer.repetitions
        })

    def __eq__(self, other):
        return self.name == other.name
