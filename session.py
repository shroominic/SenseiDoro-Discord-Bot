from threading import Timer


# Pomodoro Session Class
class Session:
    def __init__(self, guild, work_time=25, pause_time=5, number_sessions=4):
        self.name = f"🍅 - [{work_time} | {pause_time}]"
        self.number_sessions = number_sessions
        self.pause_time = pause_time
        self.work_time = work_time
        self.session_count = 0
        self.category = None
        self.guild = guild
        self.timer = None

    async def create_environment(self):
        # create session category
        self.category = await self.guild.create_category_channel(self.name)
        # create initial channels
        await self.guild.create_text_channel("session_chat", category=self.category)
        await self.guild.create_voice_channel("WAITING ROOM", category=self.category)
        await self.guild.create_voice_channel("START SESSION", category=self.category)

    def increase_session_count(self):
        self.session_count += 1

    # starts a new session
    async def start_session(self, member):
        # TODO: Automatically Mute
        # TODO: Closed Permission
        work_channel = await self.guild.create_voice_channel("DEEP WORK", category=self.category)
        for channel in self.category.voice_channels:
            await member.move_to(work_channel)
            if channel.name == "START SESSION":
                await channel.delete()
        for tc in self.category.text_channels:
            if tc.name == "session_chat":
                await tc.send("Session has started!")
        # TODO: display timer somewhere
        self.timer = Timer(self.work_time * 60, self.stop_session)

    async def stop_session(self):
        # TODO: Move to PAUSE channel
        pass

    # deletes the category and all channels off self
    async def dispose(self):
        for vc in self.category.voice_channels:
            await vc.delete()
        for tc in self.category.text_channels:
            await tc.delete()
        await self.category.delete()

