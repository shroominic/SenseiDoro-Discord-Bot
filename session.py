
class Session:
    def __init__(self, guild, work=25, pause=5):
        self.guild = guild
        self.category = None
        self.name = f"🍅 - [{work} | {pause}]"

    async def create_environment(self):
        # create session category
        self.category = await self.guild.create_category_channel(self.name)
        # create initial channels
        await self.guild.create_voice_channel("WAITING ROOM", category=self.category)
        await self.guild.create_voice_channel("START SESSION", category=self.category)

    # starts a new session
    async def start_session(self, member):
        for channel in self.category.voice_channels:
            work_channel = await self.guild.create_voice_channel("DEEP WORK", category=self.category)
            await member.move_to(work_channel)
            if channel.name == "START SESSION":
                await channel.delete()

    # deletes the category and all channels off self
    async def dispose(self):
        for vc in self.category.voice_channels:
            await vc.delete()
        for tc in self.category.text_channels:
            await tc.delete()
        self.category.delete()

