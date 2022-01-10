from timer import Timer
import asyncio


# Pomodoro Session Class
class Session:
    def __init__(self, guild, work_time=25, pause_time=5, number_sessions=4):
        self.name = f"🍅 - [{work_time} | {pause_time}]"
        self.category = None
        self.guild = guild
        self.start_button = "START SESSION"
        # channels
        self.lobby = None
        self.text_channel = None
        self.work_channel = None
        # timer settings
        self.number_sessions = number_sessions
        self.pause_time = pause_time
        self.work_time = work_time
        self.session_count = 0
        self.timer_message = None
        self.timer = None

    async def create_environment(self):
        # create session category
        self.category = await self.guild.create_category_channel(self.name)
        # create initial channels
        self.text_channel = await self.guild.create_text_channel("session_chat", category=self.category)
        self.lobby = await self.guild.create_voice_channel("WAITING ROOM", category=self.category)
        self.work_channel = await self.guild.create_voice_channel(self.start_button, category=self.category)

    def increase_session_count(self):
        self.session_count += 1

    async def display_timer(self, time_left):
        info_timer_string = f"Time left: {time_left}"
        await self.timer_message.edit(content=info_timer_string)

    async def init_timer(self):
        self.timer = Timer(
            self.work_time,
            self.pause_time,
            self.number_sessions,
            self.display_timer,
            self.next_session,
            self.pause_session,
            self.reset_session)
        # start session timer
        asyncio.create_task(self.timer.run_session())

    # starts a new session
    async def start_session(self, member):
        # init session
        await self.text_channel.send("Session has started!")
        await member.edit(mute=True)
        self.timer_message = await self.text_channel.send(f"Time left: {self.work_time}")
        # the timer manages the whole session
        await self.init_timer()

    async def next_session(self):
        self.increase_session_count()
        # TODO: Closed Permission for work_channel
        # rename session
        await self.work_channel.edit(name=f"SESSION [ {self.session_count} | {self.number_sessions} ]")
        # move all members from lobby to session
        for member in self.lobby.members:
            await member.move_to(self.work_channel)
            await member.edit(mute=True)

    async def pause_session(self):
        # move and unmute all waiting members
        for member in self.work_channel.members:
            await member.move_to(self.lobby)
            await member.edit(mute=False)
        # some chill quote
        await self.work_channel.edit(name="dude ... relax")

    async def reset_session(self):
        # move all back to lobby
        for member in self.work_channel.members:
            await member.move_to(self.lobby)
            await member.edit(mute=False)
        # reset stats
        self.session_count = 0
        # start button
        await self.work_channel.edit(name=self.start_button)

    # deletes the category and all channels off self
    async def dispose(self):
        for vc in self.category.voice_channels:
            channel_id = vc.id
            asyncio.create_task(self.guild.get_channel(channel_id).delete())
        for tc in self.category.text_channels:
            channel_id = tc.id
            asyncio.create_task(self.guild.get_channel(channel_id).delete())
        asyncio.create_task(self.category.delete())


